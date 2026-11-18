import math
from io import BytesIO
import cv2
import numpy as np
import streamlit as st
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

st.set_page_config(page_title="DocuScan", page_icon="▤", layout="wide")

def to_bgr(pil):
    return cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)

def to_pil(img):
    if img.ndim == 2: return Image.fromarray(img)
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

def order_corners(p):
    p=np.asarray(p,dtype=np.float32).reshape(4,2)
    s=p.sum(axis=1); d=np.diff(p,axis=1).ravel()
    return np.array([p[np.argmin(s)],p[np.argmin(d)],p[np.argmax(s)],p[np.argmax(d)]],np.float32)

def detect_corners(img):
    h,w=img.shape[:2]; scale=min(1,1200/max(h,w))
    small=cv2.resize(img,(int(w*scale),int(h*scale))) if scale<1 else img.copy()
    gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
    edges=cv2.Canny(cv2.GaussianBlur(gray,(5,5),0),50,150)
    edges=cv2.dilate(edges,np.ones((3,3),np.uint8),iterations=1)
    contours,_=cv2.findContours(edges,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    for c in sorted(contours,key=cv2.contourArea,reverse=True)[:35]:
        peri=cv2.arcLength(c,True); approx=cv2.approxPolyDP(c,.02*peri,True)
        if len(approx)==4 and cv2.contourArea(approx)>.08*small.shape[0]*small.shape[1]:
            return order_corners(approx.reshape(4,2)/scale),edges
    return None,edges

def homography_8x8(src,dst):
    A=[]; b=[]
    for (x,y),(u,v) in zip(src,dst):
        A.append([x,y,1,0,0,0,-u*x,-u*y]); b.append(u)
        A.append([0,0,0,x,y,1,-v*x,-v*y]); b.append(v)
    h=np.linalg.solve(np.asarray(A,float),np.asarray(b,float))
    return np.append(h,1).reshape(3,3)

def bilinear(image,mx,my):
    h,w=image.shape[:2]
    x=np.clip(mx,0,w-1.001); y=np.clip(my,0,h-1.001)
    x0=x.astype(np.int32); y0=y.astype(np.int32)
    x1=np.minimum(x0+1,w-1); y1=np.minimum(y0+1,h-1)
    dx=(x-x0)[...,None]; dy=(y-y0)[...,None]
    a=image[y0,x0].astype(float); b=image[y0,x1].astype(float)
    c=image[y1,x0].astype(float); d=image[y1,x1].astype(float)
    return np.clip(a*(1-dx)*(1-dy)+b*dx*(1-dy)+c*(1-dx)*dy+d*dx*dy,0,255).astype(np.uint8)

def manual_warp(img,H,ow,oh):
    inv=np.linalg.inv(H)
    yy,xx=np.indices((oh,ow),dtype=float)
    q=np.stack([xx.ravel(),yy.ravel(),np.ones(ow*oh)])
    p=inv@q; p/=p[2]
    mx=p[0].reshape(oh,ow).astype(np.float32); my=p[1].reshape(oh,ow).astype(np.float32)
    out=bilinear(img,mx,my)
    valid=(mx>=0)&(mx<img.shape[1])&(my>=0)&(my<img.shape[0])
    out[~valid]=255
    return out

def flatten(img,corners,method):
    tl,tr,br,bl=corners
    ow=max(200,int(max(np.linalg.norm(br-bl),np.linalg.norm(tr-tl))))
    oh=max(200,int(max(np.linalg.norm(tr-br),np.linalg.norm(tl-bl))))
    dst=np.array([[0,0],[ow-1,0],[ow-1,oh-1],[0,oh-1]],np.float32)
    H=homography_8x8(corners,dst)
    if method=="OpenCV warpPerspective":
        out=cv2.warpPerspective(img,H,(ow,oh),flags=cv2.INTER_LINEAR,borderValue=(255,255,255))
    else: out=manual_warp(img,H,ow,oh)
    return out,H

def cleanup(img,mode):
    if mode=="Original colour": return img
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    if mode=="Grayscale": return cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
    if mode=="Adaptive threshold":
        x=cv2.GaussianBlur(gray,(3,3),0)
        x=cv2.adaptiveThreshold(x,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,31,11)
        return cv2.cvtColor(x,cv2.COLOR_GRAY2BGR)
    if mode=="Colour enhance":
        lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB); l,a,b=cv2.split(lab)
        l=cv2.createCLAHE(clipLimit=2,tileGridSize=(8,8)).apply(l)
        return cv2.cvtColor(cv2.merge([l,a,b]),cv2.COLOR_LAB2BGR)
    bg=cv2.GaussianBlur(gray,(0,0),35)
    norm=cv2.divide(gray,np.maximum(bg,1),scale=255)
    norm=cv2.normalize(norm,None,0,255,cv2.NORM_MINMAX)
    x=cv2.adaptiveThreshold(norm,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,35,12)
    return cv2.cvtColor(x,cv2.COLOR_GRAY2BGR)

def pdf_bytes(images):
    buf=BytesIO(); c=canvas.Canvas(buf,pagesize=A4); pw,ph=A4; margin=24
    for img in images:
        pil=to_pil(img).convert("RGB"); w,h=pil.size
        s=min((pw-2*margin)/w,(ph-2*margin)/h)
        c.drawImage(ImageReader(pil),(pw-w*s)/2,(ph-h*s)/2,w*s,h*s,mask="auto")
        c.showPage()
    c.save(); buf.seek(0); return buf.getvalue()

def corner_preview(img,pts):
    x=img.copy()
    if pts is not None:
        p=np.asarray(pts,dtype=np.int32)
        cv2.polylines(x,[p],True,(30,180,70),max(2,x.shape[1]//500))
        for i,(a,b) in enumerate(p):
            cv2.circle(x,(int(a),int(b)),max(6,x.shape[1]//100),(20,70,230),-1)
            cv2.putText(x,str(i+1),(int(a)+7,int(b)-7),cv2.FONT_HERSHEY_SIMPLEX,.8,(20,70,230),2)
    return x

st.markdown("""<style>
.stApp{background:#F3F6F8} section[data-testid="stSidebar"]{background:#173447}
section[data-testid="stSidebar"] *{color:#fff!important}
h1,h2,h3{color:#173447}
.stButton>button,.stDownloadButton>button{background:#176B65;color:white;border:0;border-radius:9px}
</style>""",unsafe_allow_html=True)
st.sidebar.markdown("# ▤ DOCUSCAN")
st.sidebar.markdown("### DOCUMENT SCANNER")
st.sidebar.caption("Find • Flatten • Clean • Export")
page=st.sidebar.radio("WORKSPACE",["Scan a document","Batch scan & PDF","How it works"])
st.title("Document Scanner App")
st.write("Turn angled phone photographs of handouts into clean, flat, print-ready scans.")

if page=="Scan a document":
    file=st.file_uploader("Upload a document photo",type=["jpg","jpeg","png","webp"])
    if file:
        img=to_bgr(Image.open(file))
        detected,_=detect_corners(img)
        choice=st.radio("Corner selection",["Automatic detection","Manual corner fallback"],horizontal=True)
        corners=None
        h,w=img.shape[:2]
        if choice=="Automatic detection":
            corners=detected
            if corners is None: st.warning("Could not confidently find the page. Use manual corner fallback.")
            else: st.success("Four page corners detected.")
        else:
            st.image(corner_preview(img,detected),caption=f"Original image: {w} × {h} pixels",use_container_width=True)
            st.caption("Enter coordinates in this order: top-left, top-right, bottom-right, bottom-left.")
            base=detected if detected is not None else np.array([[0,0],[w-1,0],[w-1,h-1],[0,h-1]])
            vals=[]; cols=st.columns(4)
            for i,label in enumerate(["Top-left","Top-right","Bottom-right","Bottom-left"]):
                with cols[i]:
                    st.markdown("**"+label+"**")
                    xx=st.number_input(f"X{i+1}",0,w-1,int(np.clip(base[i,0],0,w-1)),key=f"x{i}")
                    yy=st.number_input(f"Y{i+1}",0,h-1,int(np.clip(base[i,1],0,h-1)),key=f"y{i}")
                    vals.append([xx,yy])
            corners=order_corners(vals)
        if corners is not None:
            st.image(corner_preview(img,corners),caption="Selected page boundary",use_container_width=True)
            a,b=st.columns(2)
            with a:
                method=st.selectbox("Perspective warp",["Our inverse mapping + bilinear interpolation","OpenCV warpPerspective"])
                filter_name=st.selectbox("Clean-up filter",["Original colour","Grayscale","Adaptive threshold","Colour enhance","Shadow removal"])
            with b:
                compare=st.checkbox("Compare with OpenCV",True)
                st.info("The homography is calculated by solving an 8 × 8 linear system with h33 = 1.")
            if st.button("Flatten document",type="primary"):
                try:
                    raw,H=flatten(img,corners,"OpenCV warpPerspective" if method.startswith("OpenCV") else "Manual")
                    result=cleanup(raw,filter_name)
                    st.session_state["scan_result"]=result
                    st.session_state["scan_raw"]=raw
                    st.session_state["scan_H"]=H
                    st.success("Scan created.")
                except Exception as e: st.error(f"Unable to flatten this image: {e}")
            if "scan_result" in st.session_state:
                raw=st.session_state["scan_raw"]; result=st.session_state["scan_result"]
                l,r=st.columns(2)
                with l: st.image(to_pil(raw),caption="Perspective-corrected page",use_container_width=True)
                with r: st.image(to_pil(result),caption="Final cleaned scan",use_container_width=True)
                d1,d2=st.columns(2)
                d1.download_button("Download PDF",pdf_bytes([result]),"document_scan.pdf","application/pdf",use_container_width=True)
                out=BytesIO(); to_pil(result).save(out,format="JPEG",quality=94)
                d2.download_button("Download JPG",out.getvalue(),"document_scan.jpg","image/jpeg",use_container_width=True)
                if compare:
                    cv,_=flatten(img,corners,"OpenCV warpPerspective")
                    manual,_=flatten(img,corners,"Manual")
                    hh=min(cv.shape[0],manual.shape[0]); ww=min(cv.shape[1],manual.shape[1])
                    diff=cv2.absdiff(cv[:hh,:ww],manual[:hh,:ww])
                    st.write(f"Manual warp vs OpenCV mean absolute pixel difference: **{np.mean(diff):.2f} / 255**")
                    heat=cv2.applyColorMap(cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY),cv2.COLORMAP_JET)
                    st.image(to_pil(heat),caption="Difference heat map",use_container_width=True)
                with st.expander("View computed 3 × 3 homography matrix"):
                    st.code(np.array2string(st.session_state["scan_H"],precision=5))

elif page=="Batch scan & PDF":
    st.subheader("Batch processing — test up to 20 photos")
    files=st.file_uploader("Choose multiple photos",type=["jpg","jpeg","png","webp"],accept_multiple_files=True)
    if files:
        if len(files)>20: st.error("Maximum 20 photos per test batch.")
        elif st.button("Process batch",type="primary"):
            results=[]; report=[]; bar=st.progress(0)
            for i,f in enumerate(files):
                try:
                    image=to_bgr(Image.open(f)); pts,_=detect_corners(image)
                    if pts is None: report.append((f.name,"Failed — corners not detected"))
                    else:
                        warped,_=flatten(image,pts,"Manual")
                        results.append(cleanup(warped,"Adaptive threshold"))
                        report.append((f.name,"Success"))
                except Exception as e: report.append((f.name,"Failed — "+str(e)[:70]))
                bar.progress((i+1)/len(files))
            st.session_state["batch_images"]=results
            st.session_state["batch_report"]=report
        if "batch_report" in st.session_state:
            report=st.session_state["batch_report"]
            ok=sum(status=="Success" for _,status in report); total=len(report)
            st.metric("Automatic scan success rate",f"{100*ok/total:.1f}%",f"{ok} successful / {total} photos")
            st.dataframe([{"Photo":n,"Result":s} for n,s in report],use_container_width=True,hide_index=True)
            if ok: st.download_button("Download combined multi-page PDF",pdf_bytes(st.session_state["batch_images"]),"batch_scans.pdf","application/pdf")
            st.caption("For failed photos, use the single-scan page and select manual corner fallback.")

else:
    st.subheader("How it works")
    st.markdown("""
**1. Corner detection:** grayscale conversion, Gaussian blur, Canny edges, contour search and quadrilateral approximation.

**2. Corner ordering:** arrange the four page corners as TL, TR, BR, BL.

**3. Homography:** calculate a 3 × 3 projective transform by solving an 8 × 8 linear system, fixing h33 = 1.

**4. Inverse mapping:** map each destination pixel back into the original photograph using the inverse homography.

**5. Bilinear interpolation:** blend the four nearest source pixels using fractional x/y distances.

**6. Clean-up:** grayscale, adaptive threshold, colour enhancement or basic shadow removal.

**7. PDF export:** export a single scan or combine successful batch scans into a multi-page PDF.
""")
    st.warning("A three-point affine transform cannot correct general perspective distortion. A projective homography requires four non-collinear point correspondences.")
    st.markdown("**Testing:** Upload 20 photos with varied angles, lighting and backgrounds. Success rate = successful detections ÷ total photos × 100%. The batch workspace calculates this from your actual test results.")

st.markdown("---")
st.caption("DOCUSCAN • Student computer-vision prototype • Inspect scan quality before printing or submitting.")
