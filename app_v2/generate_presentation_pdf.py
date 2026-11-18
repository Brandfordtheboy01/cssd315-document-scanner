import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages):
        self.saveState()
        self.setFillColor(colors.HexColor("#1E3A8A"))
        self.rect(0, 592, 792, 20, fill=1, stroke=0)
        
        self.setFillColor(colors.HexColor("#F1F5F9"))
        self.rect(0, 0, 792, 28, fill=1, stroke=0)
        
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(36, 10, "CSSD 315 Computer Graphics  |  Group Project: Brief 6 (Document Scanner App)  |  GCTU")
        
        page_str = f"Slide {self._pageNumber} of {total_pages}"
        self.drawRightString(756, 10, page_str)
        self.restoreState()

def create_presentation_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'SlideSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=10
    )

    body_style = ParagraphStyle(
        'SlideBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=5
    )

    bold_body = ParagraphStyle(
        'SlideBodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    formula_style = ParagraphStyle(
        'FormulaText',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=1
    )

    story = []

    def make_box(content_list, bg_color="#F8FAFC", border_color="#CBD5E1"):
        data = [[content] for content in content_list]
        t = Table(data, colWidths=[720])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg_color)),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor(border_color)),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        return t

    # SLIDE 1
    story.append(Spacer(1, 35))
    h_title = ParagraphStyle('H1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=26, leading=30, textColor=colors.HexColor('#1E3A8A'), alignment=1)
    h_sub = ParagraphStyle('H2', parent=styles['Normal'], fontName='Helvetica', fontSize=13, leading=17, textColor=colors.HexColor('#0284C7'), alignment=1)
    h_meta = ParagraphStyle('H3', parent=styles['Normal'], fontName='Helvetica', fontSize=10.5, leading=15, textColor=colors.HexColor('#475569'), alignment=1)

    story.append(Paragraph("DOCUSCAN: COMPUTER VISION DOCUMENT SCANNER", h_title))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Perspective Rectification, Homography Mathematics & Document Clean-up", h_sub))
    story.append(Spacer(1, 20))
    
    meta_box = [
        Paragraph("<b>Course:</b> CSSD 315 Computer Graphics", h_meta),
        Paragraph("<b>Lecturer:</b> Dr. Kwame Assa-Agyei  |  <b>Institution:</b> Ghana Communication Technology University (GCTU)", h_meta),
        Paragraph("<b>Group Project Slot B:</b> Brief 6 (Document Scanner App)", h_meta),
        Paragraph("<b>Step-by-Step Technical Teaching Deck with Worked Examples</b>", h_meta)
    ]
    story.append(make_box(meta_box, bg_color="#EFF6FF", border_color="#93C5FD"))
    story.append(PageBreak())

    # SLIDE 2
    story.append(Paragraph("1. The Problem: Why Document Photos Look Bad", title_style))
    story.append(Paragraph("Students photograph handouts with phones, but camera optics introduce physical distortion.", subtitle_style))
    p2 = [
        Paragraph("<b>The 4 Optical Problems:</b>", bold_body),
        Paragraph("1. <b>Camera tilt:</b> phone is rarely held 100% parallel to the desk.", body_style),
        Paragraph("2. <b>Perspective foreshortening:</b> far edge of the page looks smaller than the near edge.", body_style),
        Paragraph("3. <b>Converging edges:</b> parallel A4 lines lean inward toward a vanishing point.", body_style),
        Paragraph("4. <b>Shadows:</b> hands, phone body, and uneven lighting cause dark gradients.", body_style),
        Paragraph("<b>Worked Example (Real Pixel Measurements):</b>", bold_body),
        Paragraph("• Top edge: (120, 80) to (520, 110) ➜ Width = 400 pixels<br/>• Bottom edge: (90, 560) to (560, 600) ➜ Width = 470 pixels<br/>• <b>Result:</b> The bottom edge looks <b>70 pixels wider</b> because it was closer to the lens!", formula_style)
    ]
    story.append(make_box(p2))
    story.append(PageBreak())

    # SLIDE 3
    story.append(Paragraph("2. Step 1: Finding the 4 Corners of the Page", title_style))
    story.append(Paragraph("How the computer vision algorithm detects the paper perimeter automatically.", subtitle_style))
    p3 = [
        Paragraph("<b>1. Greyscale & Gaussian Blur:</b> Strips color and suppresses high-frequency desk noise.", body_style),
        Paragraph("<b>2. Canny Edge Detection:</b> Computes spatial gradient: grad(I) = (dI/dx, dI/dy).", body_style),
        Paragraph("<b>Worked Numerical Example (Detecting the Paper Edge):</b>", bold_body),
        Paragraph("Along a horizontal scan line moving from dark desk to white paper:<br/>Pixel values: [60, 62, 61, 210, 212]<br/>Differences: 62-60 = +2,  61-62 = -1,  <b>210-61 = +149 (Edge Detected!)</b>,  212-210 = +2<br/>Since gradient 149 > Canny threshold (100), the computer marks this as the paper boundary.", formula_style),
        Paragraph("<b>3. Contour Approx (Douglas-Peucker):</b> Simplifies the border into a strict 4-vertex polygon.", body_style),
        Paragraph("<b>4. Interactive Fallback:</b> Users drag corner sliders if fingers obscure the margin.", body_style)
    ]
    story.append(make_box(p3))
    story.append(PageBreak())

    # SLIDE 4
    story.append(Paragraph("3. Week 3 Theory: Homogeneous Coordinates", title_style))
    story.append(Paragraph("Why we add an extra '1' to 2D coordinates: (x, y) ➜ [x, y, 1]^T.", subtitle_style))
    p4 = [
        Paragraph("<b>The Translation Problem in 2D:</b>", bold_body),
        Paragraph("Scaling and rotation are 2x2 matrix multiplications. But translation (x' = x + tx) adds a constant. A 2x2 matrix cannot do addition! By appending 1, translation becomes standard matrix multiplication:", body_style),
        Paragraph("[ 1  0  tx ]   [ x ]     [ x + tx ]<br/>[ 0  1  ty ] * [ y ]  =  [ y + ty ]<br/>[ 0  0   1 ]   [ 1 ]     [   1    ]", formula_style),
        Paragraph("<b>Worked Calculation 1 (Translation):</b> Move point (2, 3) by (4, 1):<br/>Row 1: 1(2) + 0(3) + 4(1) = <b>6</b> | Row 2: 0(2) + 1(3) + 1(1) = <b>4</b> ➜ New point = (6, 4)", formula_style),
        Paragraph("<b>Worked Calculation 2 (Rotation by 30 deg):</b> Point (2, 0):<br/>x' = 2*cos(30) - 0*sin(30) = <b>1.732</b> | y' = 2*sin(30) + 0*cos(30) = <b>1.0</b> ➜ New point = (1.732, 1)", formula_style),
        Paragraph("<b>Composite Transformation:</b> T * R combined into one matrix moves (2, 0) directly to (5.732, 2).", body_style)
    ]
    story.append(make_box(p4))
    story.append(PageBreak())

    # SLIDE 5
    story.append(Paragraph("4. Affine (3-Point) vs. Projective Homography (4-Point)", title_style))
    story.append(Paragraph("Course Requirement 4: Proving why an affine transform cannot fix camera perspective.", subtitle_style))
    p5 = [
        Paragraph("<b>Affine Matrix (6 DOF):</b> Bottom row is locked at [0, 0, 1] ➜ Parallel lines stay parallel.", bold_body),
        Paragraph("<b>Homography Matrix (8 DOF):</b> Bottom row is [h31, h32, 1] ➜ Allows lines to converge/diverge.", bold_body),
        Paragraph("<b>Worked Example 1 (How dividing by w' creates perspective):</b><br/>Let H have bottom row [0.001, 0, 1]. For points at x=100, w'=1.1. For points at x=500, w'=1.5.<br/>Two horizontal lines with gap = 100 px before transform:<br/>• At x=100: gap becomes 136.36 - 45.45 = <b>90.91 px</b><br/>• At x=500: gap becomes 100.00 - 33.33 = <b>66.67 px (Lines converged!)</b>", formula_style),
        Paragraph("<b>Worked Example 2 (Affine Failure on Real Document):</b><br/>Fitting affine with 3 corners (TL, TR, BL) to an A4 rectangle (400x500):<br/>The 4th corner (BR) lands at <b>(470.30, 504.92) instead of (400, 500)</b> — off by <b>~70 pixels!</b><br/>Only 4-point Homography squares all 4 corners to 90 degrees.", formula_style)
    ]
    story.append(make_box(p5))
    story.append(PageBreak())

    # SLIDE 6
    story.append(Paragraph("5. The Math: Solving the 8x8 Linear System", title_style))
    story.append(Paragraph("Computing matrix H without using OpenCV's findHomography solver.", subtitle_style))
    p6 = [
        Paragraph("For each corner: u = (h11*x + h12*y + h13) / (h31*x + h32*y + 1). Cross-multiplying gives 2 equations:", body_style),
        Paragraph("Eq 1: h11*x + h12*y + h13 - h31*u*x - h32*u*y = u<br/>Eq 2: h21*x + h22*y + h23 - h31*v*x - h32*v*y = v", formula_style),
        Paragraph("<b>Worked Row Formulation (TR Corner: x=520, y=110, u=400, v=0):</b><br/>-u*x = -400*520 = -208,000 | -u*y = -400*110 = -44,000<br/>Row 3: [ 520, 110, 1, 0, 0, 0, -208000, -44000 ] = 400<br/>Row 4: [ 0, 0, 0, 520, 110, 1, 0, 0 ] = 0", formula_style),
        Paragraph("Stacking all 4 corners creates <b>A (8x8) * h = b</b>. Solved via: <b>h = numpy.linalg.solve(A, b)</b>.", body_style),
        Paragraph("<b>Verification of TR:</b> u' = 415.07, w' = 1.0377 ➜ u = 415.07 / 1.0377 = <b>400.00 (Exact Match!)</b>", formula_style)
    ]
    story.append(make_box(p6))
    story.append(PageBreak())

    # SLIDE 7
    story.append(Paragraph("6. Image Warping: Inverse Mapping & Bilinear Sampling", title_style))
    story.append(Paragraph("Why forward mapping leaves holes and how inverse mapping fills every pixel smoothly.", subtitle_style))
    p7 = [
        Paragraph("<b>Why Forward Mapping Fails:</b> If page is 2x larger, photo pixel x=1 lands at 2x=2, x=2 lands at 4. Pixels 1, 3, 5 are never filled, leaving unpainted holes and cracks in the scan.", body_style),
        Paragraph("<b>The Inverse Mapping Solution:</b> Loop over each output pixel (u, v) and map backward via H^-1:<br/>[x', y', w']^T = H^-1 * [u, v, 1]^T  ➜  x = x'/w',  y = y'/w'<br/><b>Example:</b> Page pixel (200, 250) maps backward to photo position <b>(321.32, 317.92)</b>.", formula_style),
        Paragraph("<b>Worked Bilinear Interpolation Example:</b><br/>At (321.32, 317.92), offsets are dx = 0.32, dy = 0.92. Surrounding pixels: Ia=200, Ib=180, Ic=60, Id=40.<br/>Weights: (1-dx)(1-dy)=0.0544, dx(1-dy)=0.0256, (1-dx)dy=0.6256, dx*dy=0.2944 (Sum = 1.0)<br/>Color = 0.0544(200) + 0.0256(180) + 0.6256(60) + 0.2944(40) = <b>64.8</b> (Clean sub-pixel blend!)", formula_style)
    ]
    story.append(make_box(p7))
    story.append(PageBreak())

    # SLIDE 8
    story.append(Paragraph("7. Post-Processing: Clean-up & Shadow Removal", title_style))
    story.append(Paragraph("Normalizing uneven room lighting and generating photocopy-quality output.", subtitle_style))
    p8 = [
        Paragraph("<b>1. Shadow Removal by Illumination Division:</b><br/>Heavily blurred background (sigma=35) captures only room lighting pattern. Formula: I_clean = (I_pixel / I_blurred) * 255.<br/><b>Worked Calculation:</b><br/>• Bright paper: 220 / 220 * 255 = <b>255 (Pure White)</b><br/>• Shadowed paper: 110 / 110 * 255 = <b>255 (Pure White)</b><br/>• Both ink areas: 80/220*255 and 40/110*255 both equal <b>92.7 (Equalized Ink!)</b>", formula_style),
        Paragraph("<b>2. Adaptive Thresholding (B&W Mode):</b> Uses a local 31x31 window threshold (local_mean - 10). In shadows, paper (110) > threshold (100) stays white, while ink (40) < threshold (100) turns black.", body_style),
        Paragraph("<b>3. Color Mode (CLAHE in LAB):</b> Boosts contrast strictly on the L (Luminance) channel without altering color hues.", body_style)
    ]
    story.append(make_box(p8))
    story.append(PageBreak())

    # SLIDE 9
    story.append(Paragraph("8. Experimental Verification & 20-Photo Benchmark", title_style))
    story.append(Paragraph("Validating custom math against OpenCV and testing across 20 challenge conditions.", subtitle_style))
    p9 = [
        Paragraph("<b>OpenCV Difference Comparison:</b><br/>We compute: difference = | ours - cv2.warpPerspective |.<br/><b>Example:</b> Pixel differences [0, 1, 0, 0] ➜ Mean error = <b>0.25 / 255</b> (~0.1%, imperceptible).<br/>Difference heatmap confirms our pure NumPy implementation produces identical geometry to OpenCV.", formula_style),
        Paragraph("<b>Course Benchmark Suite (20 Scenarios):</b><br/>Formula: Success Rate = (Scanned Correctly / 20) * 100%.<br/>Evaluates 4 categories: straight desk angles, steep keystone foreshortening, heavy diagonal shadows, and textured backgrounds.", body_style)
    ]
    story.append(make_box(p9))
    story.append(PageBreak())

    # SLIDE 10
    story.append(Paragraph("9. Live Demo & Class Interactive Activity", title_style))
    story.append(Paragraph("Meeting the course handbook requirement for live audience participation.", subtitle_style))
    p10 = [
        Paragraph("<b>Course Handbook Requirement:</b> <i>'Classmates photograph a page with their phones; the group scans the photos live.'</i>", bold_body),
        Paragraph("<b>Local Network Deployment:</b><br/>• Application server runs locally and broadcasts over class Wi-Fi at <b>http://192.168.x.x:8501</b>.<br/>• Classmates open the IP on mobile Safari or Chrome with zero app installation.<br/>• Tap <b>'Use Live Camera'</b>, photograph any handout, and the live scan appears on the projector screen.<br/>• Instant download of single or multi-page A4 PDFs.", body_style)
    ]
    story.append(make_box(p10))
    story.append(PageBreak())

    # SLIDE 11
    story.append(Paragraph("10. Summary & Viva Defense Cheat Sheet", title_style))
    story.append(Paragraph("Quick-reference technical answers and numbers for examination defense.", subtitle_style))
    t_summary_data = [
        [Paragraph("<b>Question</b>", bold_body), Paragraph("<b>Core Technical Explanation</b>", bold_body), Paragraph("<b>Number to Quote</b>", bold_body)],
        [
            Paragraph("<b>Homogeneous coords?</b>", body_style),
            Paragraph("Adding 1 allows translation to be a matrix multiplication, unifying transforms into 3x3 matrices.", body_style),
            Paragraph("(2, 3) + (4, 1) = (6, 4)", formula_style)
        ],
        [
            Paragraph("<b>Why 8 equations?</b>", body_style),
            Paragraph("H has 9 values, but h33=1 leaves 8 unknowns. 4 corners x 2 eq each = 8 equations.", body_style),
            Paragraph("TR row: [520, 110, 1, 0, 0, 0, -208000, -44000] = 400", formula_style)
        ],
        [
            Paragraph("<b>Why does affine fail?</b>", body_style),
            Paragraph("Affine bottom row is [0, 0, 1] so lines stay parallel. Homography divides by w' to fix depth.", body_style),
            Paragraph("4th corner misses by ~70 px: (470, 505) vs (400, 500)", formula_style)
        ],
        [
            Paragraph("<b>Why inverse mapping?</b>", body_style),
            Paragraph("Forward mapping causes holes. Inverse mapping visits every output pixel and maps backward.", body_style),
            Paragraph("Page (200, 250) ➜ Photo (321.32, 317.92)", formula_style)
        ],
        [
            Paragraph("<b>How bilinear works?</b>", body_style),
            Paragraph("Blends 4 nearest pixels weighted by distance (1-dx)(1-dy), preventing jagged letter edges.", body_style),
            Paragraph("Weights sum to 1.0 (0.0544 + 0.0256 + 0.6256 + 0.2944)", formula_style)
        ],
        [
            Paragraph("<b>Shadow removal?</b>", body_style),
            Paragraph("Divide image by blurred lighting pattern so both bright and dark paper become pure white.", body_style),
            Paragraph("220/220 and 110/110 both equal 255", formula_style)
        ]
    ]
    t_sum = Table(t_summary_data, colWidths=[130, 360, 230])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DBEAFE')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_sum)

    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF build complete!")

if __name__ == "__main__":
    out_file = "/home/hnry01/Documents/lvl300/ComputerGraphics/groupwork/CSSD315_Brief6_Document_Scanner_Presentation.pdf"
    create_presentation_pdf(out_file)
