import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

def create_guide_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45
    )
    
    styles = getSampleStyleSheet()
    
    # Custom palette
    NAVY = colors.HexColor("#1A365D")
    TEAL = colors.HexColor("#0D9488")
    DARK = colors.HexColor("#1F2937")
    LIGHT_BG = colors.HexColor("#F8FAFC")
    BORDER_COLOR = colors.HexColor("#E2E8F0")
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=22, leading=26,
        textColor=NAVY, spaceAfter=4
    )
    
    sub_title = ParagraphStyle(
        'DocSub', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=16,
        textColor=TEAL, spaceAfter=15
    )
    
    h1 = ParagraphStyle(
        'H1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=14, leading=18,
        textColor=NAVY, spaceBefore=12, spaceAfter=6, keepWithNext=True
    )

    h2 = ParagraphStyle(
        'H2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=15,
        textColor=TEAL, spaceBefore=8, spaceAfter=4, keepWithNext=True
    )

    body = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=14,
        textColor=DARK, spaceAfter=8
    )

    body_bold = ParagraphStyle(
        'BodyBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9.5, leading=14,
        textColor=DARK
    )

    callout = ParagraphStyle(
        'Callout', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=9, leading=13,
        textColor=DARK
    )

    story = []

    # Title Banner
    story.append(Paragraph("CSSD 315 Computer Graphics — Group Project", sub_title))
    story.append(Paragraph("Document Scanner App (Brief 6) — Complete Project Guide", title_style))
    story.append(Paragraph("<b>Course:</b> Level 300 Computer Graphics | <b>Institution:</b> GCTU | <b>Topic:</b> Homogeneous Coordinates & Projective Warping", body))
    story.append(HRFlowable(width="100%", thickness=1.5, color=TEAL, spaceAfter=12))

    # Section 1: Plain English Summary
    story.append(Paragraph("1. Plain English Summary: What Did We Build?", h1))
    summary_text = (
        "When you photograph a piece of paper or handout with a phone, the picture is almost always "
        "tilted, warped, and unevenly lit. Faraway edges look smaller, and text lines slant inward. "
        "We built a full document scanner application (similar to CamScanner or Adobe Scan) that takes "
        "that crooked photograph and automatically converts it into a <b>flat, crisp, professional PDF</b>."
    )
    story.append(Paragraph(summary_text, body))

    # Comparison Table
    table_data = [
        [Paragraph("<b>Step in Pipeline</b>", body_bold), Paragraph("<b>What It Actually Does (In Simple Words)</b>", body_bold), Paragraph("<b>Math / Algorithm Used</b>", body_bold)],
        [Paragraph("<b>1. Find Corners</b>", body), Paragraph("Finds the 4 corners of the sheet of paper on the desk.", body), Paragraph("Canny Edges & Contour Polygon Approximation", body)],
        [Paragraph("<b>2. 8x8 Homography</b>", body), Paragraph("Calculates the exact 3x3 mathematical recipe to un-tilt the 4 corners into a 90° rectangle.", body), Paragraph("Homogeneous coordinates + <code>numpy.linalg.solve</code>", body)],
        [Paragraph("<b>3. Inverse Warping</b>", body), Paragraph("Stretches the paper flat. Looks up every pixel on the output grid and samples color smoothly without leaving holes.", body), Paragraph("Inverse Mapping + Vectorized Bilinear Interpolation", body)],
        [Paragraph("<b>4. Clean-up Filters</b>", body), Paragraph("Removes phone shadows, yellow lighting, and enhances text into crisp black and white.", body), Paragraph("Gaussian illumination division + Adaptive thresholding", body)],
        [Paragraph("<b>5. PDF Export</b>", body), Paragraph("Packs the scanned pages into a standard printable A4 PDF file.", body), Paragraph("ReportLab engine with aspect-ratio scaling", body)],
    ]
    t1 = Table(table_data, colWidths=[110, 240, 170])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t1)
    story.append(Spacer(1, 14))

    # Section 2: Why Affine Fails
    story.append(Paragraph("2. The Big Viva Question: Why 3 Points (Affine) Isn't Enough", h1))
    affine_explanation = (
        "Dr. Kwame Assa-Agyei's project handbook specifically demands: <i>'Show why an affine (3-point) warp is not enough.'</i><br/>"
        "Here is the simple explanation everyone in the group must memorize:<br/><br/>"
        "• <b>Affine Transformation (3 corners, 6 numbers):</b> In an affine matrix, the bottom row is permanently locked to <code>[0, 0, 1]</code>. "
        "Because of this, affine transformations <b>preserve parallel lines</b>. They can rotate, slide, and stretch, but opposite edges MUST remain parallel. "
        "Therefore, an affine warp can only turn a rectangle into a <b>parallelogram</b>. It can never fix camera foreshortening where faraway edges look smaller!<br/>"
        "• <b>Projective / Homography Transform (4 corners, 8 numbers):</b> The bottom row is <code>[h31, h32, 1]</code>. "
        "These extra numbers allow <b>perspective division</b> (dividing by depth). This is what enables the app to bend converging perspective lines back into right angles."
    )
    story.append(Paragraph(affine_explanation, body))
    story.append(Spacer(1, 10))

    # Section 3: The 8x8 Math Explained
    story.append(Paragraph("3. Understanding the 8x8 Linear System Without Panicking", h1))
    math_simple = (
        "To map a tilted corner (x, y) to a destination corner (u, v), the projective formula is:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>u = (h11*x + h12*y + h13) / (h31*x + h32*y + 1)</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>v = (h21*x + h22*y + h23) / (h31*x + h32*y + 1)</b><br/><br/>"
        "Because fractions are hard to solve directly in computer matrices, we cross-multiply by the denominator:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>h11*x + h12*y + h13 - h31*u*x - h32*u*y = u</code><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>h21*x + h22*y + h23 - h31*v*x - h32*v*y = v</code><br/><br/>"
        "Notice that <b>one corner point gives us 2 linear equations</b>. Since a sheet of paper has <b>4 corners</b>, "
        "4 corners × 2 equations = <b>8 linear equations</b>. We stack them into an 8×8 grid <code>A * h = b</code> "
        "and tell Python (<code>numpy.linalg.solve</code>) to find the 8 unknowns in a microsecond."
    )
    story.append(Paragraph(math_simple, body))
    story.append(Spacer(1, 10))

    # Section 4: What We Actually Built in app_v2
    story.append(Paragraph("4. Project Structure in 'groupwork/app_v2'", h1))
    files_data = [
        [Paragraph("<b>File / Module</b>", body_bold), Paragraph("<b>Role in Project</b>", body_bold)],
        [Paragraph("<code>app.py</code>", body), Paragraph("Interactive Streamlit Web Application with 4 complete interactive modes.", body)],
        [Paragraph("<code>modules/homography.py</code>", body), Paragraph("Our scratch math engine: corner sorting, 8x8 formulation, and affine solver.", body)],
        [Paragraph("<code>modules/warp.py</code>", body), Paragraph("Custom inverse-mapping engine with vectorized bilinear interpolation + OpenCV comparison heatmap.", body)],
        [Paragraph("<code>modules/detector.py</code>", body), Paragraph("Automated Canny edge detector and contour approximation module.", body)],
        [Paragraph("<code>modules/filters.py</code>", body), Paragraph("Illumination normalization (shadow removal), adaptive thresholding, and CLAHE color enhancement.", body)],
        [Paragraph("<code>modules/pdf_gen.py</code>", body), Paragraph("Multi-page printable A4 PDF compiler via ReportLab.", body)],
        [Paragraph("<code>test_dataset/</code>", body), Paragraph("20 benchmark photos covering straight angles, extreme keystone, shadows, and textures.", body)],
    ]
    t2 = Table(files_data, colWidths=[160, 360])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 12))

    # Section 5: Group Work Packages
    story.append(Paragraph("5. Official Group Work Packages (For Your Final Report)", h1))
    wp_text = (
        "When submitting the group report and contribution table, allocate the work packages as follows:<br/>"
        "• <b>WP 1 (Corner Detection):</b> Canny edge thresholds, contour approximations, manual fallback UI.<br/>"
        "• <b>WP 2 (Homography Mathematics):</b> 8x8 matrix formulation, corner sorting, numpy solver.<br/>"
        "• <b>WP 3 (Warp & Bilinear Interpolation):</b> Inverse mapping grid, sub-pixel interpolation, OpenCV error comparison.<br/>"
        "• <b>WP 4 (Clean-up Filters):</b> Gaussian background illumination modeling, adaptive binarization, CLAHE.<br/>"
        "• <b>WP 5 (PDF & UI):</b> Streamlit web application, live camera capture, ReportLab multi-page PDF export.<br/>"
        "• <b>WP 6 (Testing & Report):</b> 20-photo benchmark dataset, success rate metrics, presentation slides."
    )
    story.append(Paragraph(wp_text, body))
    
    doc.build(story)
    print(f"Guide PDF built successfully: {filename}")

if __name__ == "__main__":
    out_pdf = "/home/hnry01/Documents/lvl300/ComputerGraphics/groupwork/DocuScan_Project_Guide_CSSD315.pdf"
    create_guide_pdf(out_pdf)
