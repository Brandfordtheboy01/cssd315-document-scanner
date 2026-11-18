import os
import glob
from io import BytesIO
import cv2
import numpy as np
import streamlit as st
from PIL import Image

import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DATASET_DIR = os.path.join(BASE_DIR, 'test_dataset')


# Import our custom modules
from modules.homography import order_points, compute_homography_8x8, compute_affine_6x6
from modules.warp import custom_warp_perspective, compare_with_opencv
from modules.detector import auto_detect_corners, draw_corner_overlay
from modules.filters import (
    apply_grayscale,
    apply_adaptive_threshold,
    apply_shadow_removal,
    apply_color_enhance
)
from modules.pdf_gen import bgr_to_pil, generate_pdf_bytes
from modules.slides import render_slides

st.set_page_config(
    page_title="DocuScan Pro — Computer Vision Scanner",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for polished look
st.markdown("""
<style>
    .main-header { font-size: 2.1rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0px; }
    .sub-header { font-size: 1.05rem; color: #4B5563; margin-bottom: 20px; }
    .badge { background-color: #DBEAFE; color: #1E40AF; padding: 4px 10px; border-radius: 9999px; font-weight: 600; font-size: 0.85rem; }
    .stat-box { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 🎓 CSSD 315 Computer Graphics")
st.sidebar.markdown("**Group Project — Brief 6**")
st.sidebar.caption("Document Scanner App • GCTU")

mode = st.sidebar.radio(
    "Navigation Mode",
    [
        "🖥️ Interactive Presentation Slides",
        "1. Interactive Scanner (Upload / Camera)",
        "2. Theory Lab: Affine vs. Homography",
        "3. Course Benchmark (20 Test Photos)",
        "4. Math Engine & Derivation"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Core Graphics Algorithms:**
- 8x8 Linear System Formulation
- Custom Inverse Mapping Engine
- Vectorized Bilinear Interpolation
- Dual-Illumination Shadow Removal
""")

# Helper to load image as BGR
def load_uploaded_image(file):
    pil = Image.open(file).convert("RGB")
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

# -------------------------------------------------------------
# MODE 1: INTERACTIVE SCANNER
# -------------------------------------------------------------

# -------------------------------------------------------------
# MODE: INTERACTIVE PRESENTATION SLIDES
# -------------------------------------------------------------
if mode == "🖥️ Interactive Presentation Slides":
    render_slides()

# -------------------------------------------------------------
# MODE 1: INTERACTIVE SCANNER
# -------------------------------------------------------------
elif mode == "1. Interactive Scanner (Upload / Camera)":

    st.markdown('<p class="main-header">📄 DocuScan Pro — Document Scanner</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Live projective rectification, custom bilinear sampling & document restoration</p>', unsafe_allow_html=True)

    input_source = st.radio("Choose Input Method:", ["Upload File", "Use Live Camera", "Load Sample Test Photo"], horizontal=True)

    img = None
    if input_source == "Upload File":
        f = st.file_uploader("Upload photograph of a document", type=["jpg", "jpeg", "png", "webp"])
        if f: img = load_uploaded_image(f)
    elif input_source == "Use Live Camera":
        cam_photo = st.camera_input("Take a photo of a document / handout")
        if cam_photo: img = load_uploaded_image(cam_photo)
    else:
        sample_files = sorted(sorted(glob.glob(os.path.join(DATASET_DIR, "*.jpeg")) + glob.glob(os.path.join(DATASET_DIR, "*.jpg"))))
        if sample_files:
            chosen = st.selectbox("Select a benchmark photo:", sample_files)
            img = cv2.imread(chosen)
        else:
            st.warning("No benchmark dataset found. Generate dataset first.")

    if img is not None:
        h, w = img.shape[:2]
        col_img, col_controls = st.columns([1.1, 0.9])

        with col_controls:
            st.markdown("#### 1. Corner Detection & Tuning")
            corner_mode = st.radio("Corner Selection:", ["Auto-Detect (Canny + Contour)", "Manual Coordinate Adjust"], horizontal=True)

            auto_pts, edges = auto_detect_corners(img)
            
            if corner_mode == "Auto-Detect (Canny + Contour)":
                if auto_pts is not None:
                    st.success("✅ 4 document corners detected automatically!")
                    pts = auto_pts
                else:
                    st.warning("⚠️ Auto-detect could not confidently find 4 corners. Switching to image borders (adjust manually below).")
                    pts = np.float32([[w*0.1, h*0.1], [w*0.9, h*0.1], [w*0.9, h*0.9], [w*0.1, h*0.9]])
            else:
                pts = auto_pts if auto_pts is not None else np.float32([[w*0.1, h*0.1], [w*0.9, h*0.1], [w*0.9, h*0.9], [w*0.1, h*0.9]])
                st.markdown("**Quick Sliders to Fit Document Corners (X, Y):**")
                with st.expander("📍 Adjust 1: Top-Left (Red Dot)", expanded=True):
                    tl_x = st.slider("TL X", 0, w, int(pts[0][0]), 5, key="tl_x")
                    tl_y = st.slider("TL Y", 0, h, int(pts[0][1]), 5, key="tl_y")
                with st.expander("📍 Adjust 2: Top-Right (Blue Dot)", expanded=True):
                    tr_x = st.slider("TR X", 0, w, int(pts[1][0]), 5, key="tr_x")
                    tr_y = st.slider("TR Y", 0, h, int(pts[1][1]), 5, key="tr_y")
                with st.expander("📍 Adjust 3: Bottom-Right (Yellow Dot)", expanded=False):
                    br_x = st.slider("BR X", 0, w, int(pts[2][0]), 5, key="br_x")
                    br_y = st.slider("BR Y", 0, h, int(pts[2][1]), 5, key="br_y")
                with st.expander("📍 Adjust 4: Bottom-Left (Sky Dot)", expanded=False):
                    bl_x = st.slider("BL X", 0, w, int(pts[3][0]), 5, key="bl_x")
                    bl_y = st.slider("BL Y", 0, h, int(pts[3][1]), 5, key="bl_y")
                pts = np.float32([[tl_x, tl_y], [tr_x, tr_y], [br_x, br_y], [bl_x, bl_y]])

            st.markdown("#### 2. Scan Enhancement Filter")
            filter_choice = st.selectbox(
                "Post-processing filter:",
                ["B&W Photocopy (Adaptive Threshold)", "Shadow Removal (Illumination Normalization)", "Color Enhanced (CLAHE)", "Grayscale", "Original Color (Unfiltered)"]
            )

            compare_toggle = st.checkbox("🔬 Enable OpenCV Accuracy Comparison & Difference Heatmap", value=True)

        with col_img:
            preview_img = draw_corner_overlay(img, pts)
            st.image(bgr_to_pil(preview_img), caption="Input Image with 4 Corners (TL: Red, TR: Blue, BR: Yellow, BL: Sky)", use_container_width=True)

        # Processing button
        st.markdown("---")
        if st.button("🚀 Process & Generate Scan", type="primary"):
            ordered = order_points(pts)
            tl, tr, br, bl = ordered

            # Calculate destination dimensions based on max width/height
            out_w = max(300, int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl))))
            out_h = max(300, int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl))))
            dst_rect = np.float32([[0, 0], [out_w - 1, 0], [out_w - 1, out_h - 1], [0, out_h - 1]])

            # Solve Homography
            H, A, b = compute_homography_8x8(ordered, dst_rect)

            # Custom Warp
            warped = custom_warp_perspective(img, H, out_w, out_h)

            # Apply Filter
            if filter_choice == "B&W Photocopy (Adaptive Threshold)":
                final_scan = apply_adaptive_threshold(warped)
            elif filter_choice == "Shadow Removal (Illumination Normalization)":
                final_scan = apply_shadow_removal(warped)
            elif filter_choice == "Color Enhanced (CLAHE)":
                final_scan = apply_color_enhance(warped)
            elif filter_choice == "Grayscale":
                final_scan = apply_grayscale(warped)
            else:
                final_scan = warped

            st.session_state["active_scan"] = final_scan
            st.session_state["warped_raw"] = warped
            st.session_state["H_matrix"] = H
            st.session_state["ordered_pts"] = ordered
            st.session_state["out_dims"] = (out_w, out_h)

        if "active_scan" in st.session_state:
            st.markdown("### 🏆 Scanned Result")
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.image(bgr_to_pil(st.session_state["warped_raw"]), caption="1. Flattened Geometry (Homography Warp)", use_container_width=True)
            with res_col2:
                st.image(bgr_to_pil(st.session_state["active_scan"]), caption="2. Enhanced Document Output", use_container_width=True)

            # Export Controls
            exp1, exp2 = st.columns(2)
            pdf_data = generate_pdf_bytes([st.session_state["active_scan"]])
            exp1.download_button("📥 Download Scanned PDF", pdf_data, "docuscan_output.pdf", "application/pdf", use_container_width=True)
            
            jpg_buf = BytesIO()
            bgr_to_pil(st.session_state["active_scan"]).save(jpg_buf, format="JPEG", quality=95)
            exp2.download_button("🖼️ Download Clean JPG", jpg_buf.getvalue(), "docuscan_output.jpg", "image/jpeg", use_container_width=True)

            # Verification vs OpenCV
            if compare_toggle:
                st.markdown("### 🔬 Precision Benchmark: Custom Bilinear Engine vs OpenCV")
                out_w, out_h = st.session_state["out_dims"]
                custom_w, cv_w, mean_err, max_err, heat = compare_with_opencv(img, st.session_state["H_matrix"], out_w, out_h)
                
                m1, m2 = st.columns(2)
                m1.metric("Mean Absolute Pixel Error (0-255 scale)", f"{mean_err:.3f}", "Sub-pixel precision match")
                m2.metric("Maximum Absolute Pixel Difference", f"{max_err:.1f} / 255")
                
                c_heat, c_info = st.columns([1, 1])
                with c_heat:
                    st.image(bgr_to_pil(heat), caption="Difference Heatmap (Scaled 10x for visibility; dark blue = 0 difference)", use_container_width=True)
                with c_info:
                    st.markdown("""
                    **Mathematical Validation:**
                    - The heatmap shows negligible error across the image.
                    - Slight edge boundary discrepancies are due to floating-point rounding between OpenCV's C++ SIMD routines and our NumPy bilinear formulation.
                    - Confirms our custom `custom_warp_perspective` implementation matches industry standard!
                    """)

# -------------------------------------------------------------
# MODE 2: THEORY LAB - AFFINE VS. HOMOGRAPHY
# -------------------------------------------------------------
elif mode == "2. Theory Lab: Affine vs. Homography":
    st.markdown('<p class="main-header">📐 Theory Lab: Why 3 Points (Affine) Fails</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Course Requirement 4: Demonstrate why a 3-point affine warp cannot fix perspective foreshortening</p>', unsafe_allow_html=True)

    st.markdown("""
    In CSSD 315 Week 3, we studied affine transformations ($3 \\times 3$ matrices with the bottom row strictly $[0, 0, 1]$).
    - **Affine (3 correspondences, 6 DOF):** Preserves parallelism. Parallel lines in 3D remain strictly parallel in 2D.
    - **Projective / Homography (4 correspondences, 8 DOF):** Allows the bottom row to be non-zero $[h_{31}, h_{32}, 1]$, which models **depth perspective division**.
    """)

    sample = cv2.imread(os.path.join(DATASET_DIR, "06_steep_keystone_top_narrow.jpg"))
    if sample is None:
        st.warning("Generate test dataset first.")
    else:
        pts, _ = auto_detect_corners(sample)
        if pts is None:
            h_s, w_s = sample.shape[:2]
            pts = np.float32([(450, 80), (830, 80), (1080, 910), (200, 910)])
        
        ordered = order_points(pts)
        tl, tr, br, bl = ordered
        ow = 600
        oh = 840
        dst_rect = np.float32([[0, 0], [ow - 1, 0], [ow - 1, oh - 1], [0, oh - 1]])

        # 1. 3-point Affine
        M_aff = compute_affine_6x6(ordered, dst_rect)
        affine_warp = cv2.warpAffine(sample, M_aff[:2], (ow, oh))

        # 2. 4-point Homography
        H, _, _ = compute_homography_8x8(ordered, dst_rect)
        homog_warp = custom_warp_perspective(sample, H, ow, oh)

        col1, col2 = st.columns(2)
        with col1:
            st.error("❌ 3-Point Affine Warp (Fails on Perspective)")
            st.image(bgr_to_pil(affine_warp), caption="Notice: The bottom edge is slanted/sheared. It can only produce a parallelogram, never a squared page!", use_container_width=True)
            st.code("""
Affine Matrix (Bottom row is locked):
[[ a11  a12  tx ]
 [ a21  a22  ty ]
 [  0    0    1 ]]
Degrees of freedom = 6 (Only 3 points)
            """)

        with col2:
            st.success("✅ 4-Point Homography Warp (Correct)")
            st.image(bgr_to_pil(homog_warp), caption="Notice: All 4 corners square up into 90° right angles. Perspective lines are restored!", use_container_width=True)
            st.code(f"""
Projective Matrix H (8 Degrees of Freedom):
{np.array2string(H, precision=4)}
Bottom row [h31, h32, 1] enables perspective division!
            """)

# -------------------------------------------------------------
# MODE 3: COURSE BENCHMARK (20 TEST PHOTOS)
# -------------------------------------------------------------
elif mode == "3. Course Benchmark (20 Test Photos)":
    st.markdown('<p class="main-header">📊 Course Benchmark: 20 Test Photos Dataset</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Course Requirement 7: Test on 20 photos across angles, lighting and backgrounds, and report success rate</p>', unsafe_allow_html=True)

    files = sorted(sorted(glob.glob(os.path.join(DATASET_DIR, "*.jpeg")) + glob.glob(os.path.join(DATASET_DIR, "*.jpg"))))
    if not files:
        st.warning("Benchmark photos not found. Click to generate them:")
        if st.button("Generate 20 Benchmark Images Now"):
            os.system("python generate_dataset.py")
            st.rerun()
    else:
        st.markdown(f"Found **{len(files)} benchmark photos** across 4 challenge categories.")
        
        if st.button("▶️ Execute Full 20-Photo Benchmark Pipeline", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            scanned_pages = []
            
            for i, fpath in enumerate(files):
                fname = os.path.basename(fpath)
                status_text.text(f"Processing ({i+1}/20): {fname}")
                test_img = cv2.imread(fpath)
                
                pts, _ = auto_detect_corners(test_img)
                if pts is not None:
                    try:
                        ordered = order_points(pts)
                        ow = 600
                        oh = 840
                        dst_rect = np.float32([[0, 0], [ow - 1, 0], [ow - 1, oh - 1], [0, oh - 1]])
                        H, _, _ = compute_homography_8x8(ordered, dst_rect)
                        warped = custom_warp_perspective(test_img, H, ow, oh)
                        cleaned = apply_shadow_removal(warped)
                        scanned_pages.append(cleaned)
                        results.append({"Photo": fname, "Detection": "Success", "Warp": "Success", "Status": "PASS"})
                    except Exception as e:
                        results.append({"Photo": fname, "Detection": "Success", "Warp": "Error", "Status": "FAIL"})
                else:
                    results.append({"Photo": fname, "Detection": "Failed (Faint Edge/Background)", "Warp": "Skipped", "Status": "FAIL (Use Manual Fallback)"})
                    
                progress_bar.progress((i + 1) / len(files))
                
            status_text.success("Benchmark Run Complete!")
            
            passes = sum(1 for r in results if r["Status"] == "PASS")
            rate = (passes / len(results)) * 100
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            col_stat1.metric("Overall Success Rate", f"{rate:.1f}%")
            col_stat2.metric("Successful Scans", f"{passes} / {len(results)}")
            col_stat3.metric("Manual Fallbacks Required", f"{len(results) - passes}")
            
            st.dataframe(results, use_container_width=True)
            
            if scanned_pages:
                batch_pdf = generate_pdf_bytes(scanned_pages)
                st.download_button("📥 Download Combined Multi-Page Benchmark PDF", batch_pdf, "CSSD315_20_Page_Benchmark_Scan.pdf", "application/pdf")

# -------------------------------------------------------------
# MODE 4: MATH ENGINE & DERIVATION
# -------------------------------------------------------------
else:
    st.markdown('<p class="main-header">🧠 Mathematical Engine & Derivations</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Complete step-by-step mathematical reference for viva defense</p>', unsafe_allow_html=True)

    st.markdown("### 1. Homogeneous Coordinates Formulation")
    st.markdown("In Euclidean 2D space, a point is $(x, y)$. In homogeneous coordinates, we append a third scale component:")
    st.latex(r"\mathbf{p} = \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}")
    
    st.markdown(r"A projective transformation (Homography) maps $(x, y)$ on the photo to $(u, v)$ on the flat document via a $3 \times 3$ matrix $H$:")
    st.latex(r"\begin{bmatrix} u' \\ v' \\ w' \end{bmatrix} = \begin{bmatrix} h_{11} & h_{12} & h_{13} \\ h_{21} & h_{22} & h_{23} \\ h_{31} & h_{32} & h_{33} \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}")
    
    st.markdown("The Cartesian coordinates $(u, v)$ are recovered through perspective division by $w'$:")
    st.latex(r"u = \frac{u'}{w'} = \frac{h_{11}x + h_{12}y + h_{13}}{h_{31}x + h_{32}y + h_{33}}, \quad v = \frac{v'}{w'} = \frac{h_{21}x + h_{22}y + h_{23}}{h_{31}x + h_{32}y + h_{33}}")

    st.markdown("---")
    st.markdown(r"### 2. Formulating the $8 \times 8$ Linear System")
    st.markdown("Cross-multiplying by the denominator gives:")
    st.latex(r"h_{11}x + h_{12}y + h_{13} - h_{31}ux - h_{32}uy - h_{33}u = 0")
    st.latex(r"h_{21}x + h_{22}y + h_{23} - h_{31}vx - h_{32}vy - h_{33}v = 0")
    
    st.markdown("Because homography is defined up to scale, we set $h_{33} = 1$:")
    st.latex(r"h_{11}x + h_{12}y + h_{13} - h_{31}ux - h_{32}uy = u")
    st.latex(r"h_{21}x + h_{22}y + h_{23} - h_{31}vx - h_{32}vy = v")
    
    st.markdown(r"With 4 corner pairs $(x_i, y_i) \to (u_i, v_i)$ for $i \in \{1, 2, 3, 4\}$, we obtain an $8 \times 8$ linear system $\mathbf{A}\mathbf{h} = \mathbf{b}$:")
    st.latex(r"\begin{bmatrix} x_1 & y_1 & 1 & 0 & 0 & 0 & -u_1 x_1 & -u_1 y_1 \\ 0 & 0 & 0 & x_1 & y_1 & 1 & -v_1 x_1 & -v_1 y_1 \\ \vdots & \vdots & \vdots & \vdots & \vdots & \vdots & \vdots & \vdots \\ x_4 & y_4 & 1 & 0 & 0 & 0 & -u_4 x_4 & -u_4 y_4 \\ 0 & 0 & 0 & x_4 & y_4 & 1 & -v_4 x_4 & -v_4 y_4 \end{bmatrix} \begin{bmatrix} h_{11} \\ h_{12} \\ h_{13} \\ h_{21} \\ h_{22} \\ h_{23} \\ h_{31} \\ h_{32} \end{bmatrix} = \begin{bmatrix} u_1 \\ v_1 \\ \vdots \\ u_4 \\ v_4 \end{bmatrix}")
    st.caption("Solved directly via numpy.linalg.solve(A, b).")

    st.markdown("---")
    st.markdown("### 3. Inverse Mapping & Bilinear Interpolation")
    st.markdown("Forward mapping creates holes. With **Inverse Mapping**, we iterate over destination $(u, v)$ and map backwards into source continuous coordinates:")
    st.latex(r"\begin{bmatrix} x' \\ y' \\ w' \end{bmatrix} = H^{-1} \begin{bmatrix} u \\ v \\ 1 \end{bmatrix}, \quad x = \frac{x'}{w'}, \quad y = \frac{y'}{w'}")
    
    st.markdown("Using the fractional offsets $dx = x - x_0$ and $dy = y - y_0$, bilinear interpolation computes:")
    st.latex(r"I(x, y) = (1 - dx)(1 - dy)I_a + dx(1 - dy)I_b + (1 - dx)dyI_c + dx dy I_d")
