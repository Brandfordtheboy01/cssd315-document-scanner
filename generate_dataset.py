import cv2
import numpy as np
import os

os.makedirs('test_dataset', exist_ok=True)

# Generate a synthetic A4 document image with realistic text, title, table, and border
def create_base_doc():
    doc = np.ones((840, 600, 3), dtype=np.uint8) * 255
    # Border
    cv2.rectangle(doc, (20, 20), (580, 820), (50, 50, 50), 2)
    # Header
    cv2.putText(doc, "CSSD 315: COMPUTER GRAPHICS", (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 150), 2)
    cv2.putText(doc, "Project 6: Document Scanner Benchmark Sheet", (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (80, 80, 80), 1)
    cv2.line(doc, (50, 130), (550, 130), (0, 0, 0), 2)
    
    # Body text paragraphs
    text_lines = [
        "Homogeneous coordinates allow us to represent 2D affine and projective",
        "transformations as unified 3x3 matrix multiplications. While a 3-point affine",
        "warp preserves parallelism, phone camera photographs introduce severe",
        "perspective foreshortening where parallel edges converge.",
        "",
        "To recover a clean scan, we formulate an 8-DOF projective homography matrix H.",
        "The system is solved from 4 corner correspondences using numpy.linalg.solve.",
        "Inverse mapping with bilinear interpolation maps destination pixels smoothly",
        "back to the source domain without sampling holes or aliasing artifacts.",
        "",
        "Filter Pipeline Benchmark Results:",
        "- Grayscale conversion and illumination normalization via large Gaussian blur.",
        "- Adaptive Gaussian thresholding for binarized scan output.",
        "- Contrast Limited Adaptive Histogram Equalization (CLAHE) for color enhancement.",
        "- Multi-page PDF generation via ReportLab."
    ]
    y = 170
    for line in text_lines:
        if line:
            cv2.putText(doc, line, (50, y), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (30, 30, 30), 1)
        y += 28

    # Table
    cv2.rectangle(doc, (50, 600), (550, 750), (100, 100, 100), 1)
    cv2.line(doc, (50, 640), (550, 640), (100, 100, 100), 1)
    cv2.putText(doc, "Transform Method", (60, 628), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
    cv2.putText(doc, "Degrees of Freedom", (230, 628), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
    cv2.putText(doc, "Parallelism", (430, 628), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
    
    cv2.putText(doc, "Affine (3-pt)", (60, 675), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (50, 50, 50), 1)
    cv2.putText(doc, "6 DOF", (230, 675), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (50, 50, 50), 1)
    cv2.putText(doc, "Preserved", (430, 675), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 150, 0), 1)

    cv2.putText(doc, "Projective (4-pt)", (60, 715), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (50, 50, 50), 1)
    cv2.putText(doc, "8 DOF", (230, 715), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (50, 50, 50), 1)
    cv2.putText(doc, "Not Preserved", (430, 715), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 200), 1)

    return doc

base_doc = create_base_doc()
dh, dw = base_doc.shape[:2]
doc_corners = np.float32([[0, 0], [dw, 0], [dw, dh], [0, dh]])

# Background generators
def get_background(bg_type, canvas_w=1280, canvas_h=960):
    if bg_type == 'wood':
        bg = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
        bg[:, :] = (35, 60, 110) # brown wood tone
        noise = np.random.normal(0, 8, (canvas_h, canvas_w, 3)).astype(np.int16)
        bg = np.clip(bg.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        for y in range(0, canvas_h, 40):
            cv2.line(bg, (0, y), (canvas_w, y), (25, 45, 90), 2)
        return bg
    elif bg_type == 'tablecloth':
        bg = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
        bg[:] = (180, 180, 180)
        for x in range(0, canvas_w, 30):
            cv2.line(bg, (x, 0), (x, canvas_h), (160, 160, 200), 1)
        for y in range(0, canvas_h, 30):
            cv2.line(bg, (0, y), (canvas_w, y), (160, 160, 200), 1)
        return bg
    elif bg_type == 'dark':
        bg = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
        bg[:] = (30, 30, 30)
        return bg
    else: # desk neutral
        bg = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
        bg[:] = (70, 90, 120)
        return bg

# 20 distinct scenarios (Angles, Backgrounds, Lighting, Shadow)
scenarios = [
    # Category 1: Clean Desk Angles (Normal to moderate)
    ("01_clean_straight_desk", "desk", [(340, 60), (940, 60), (940, 900), (340, 900)], "none"),
    ("02_slight_angle_wood", "wood", [(360, 100), (970, 70), (910, 890), (320, 850)], "none"),
    ("03_moderate_tilt_dark", "dark", [(300, 120), (1000, 80), (930, 910), (250, 830)], "none"),
    ("04_rotation_tablecloth", "tablecloth", [(380, 180), (1020, 90), (880, 930), (270, 790)], "none"),
    ("05_overhead_wood", "wood", [(320, 80), (960, 80), (970, 880), (310, 880)], "none"),

    # Category 2: Steep Perspective Foreshortening (Challenging Angles)
    ("06_steep_keystone_top_narrow", "wood", [(450, 80), (830, 80), (1080, 910), (200, 910)], "none"),
    ("07_steep_keystone_bottom_narrow", "desk", [(220, 70), (1060, 70), (850, 900), (430, 900)], "none"),
    ("08_severe_side_slant_left", "dark", [(460, 70), (1020, 160), (920, 920), (280, 750)], "none"),
    ("09_severe_side_slant_right", "tablecloth", [(260, 150), (820, 60), (1000, 770), (360, 930)], "none"),
    ("10_dramatic_isometric_angle", "wood", [(400, 80), (1050, 190), (880, 940), (230, 730)], "none"),

    # Category 3: Non-uniform Lighting & Shadow Overlays
    ("11_harsh_diagonal_shadow", "wood", [(350, 90), (960, 70), (920, 890), (330, 850)], "diag_shadow"),
    ("12_corner_phone_shadow", "desk", [(330, 70), (950, 60), (960, 890), (320, 880)], "corner_shadow"),
    ("13_horizontal_half_shadow", "dark", [(320, 80), (970, 80), (940, 900), (310, 890)], "half_shadow"),
    ("14_vignette_low_light", "wood", [(340, 80), (950, 70), (930, 890), (330, 870)], "vignette"),
    ("15_steep_angle_with_shadow", "tablecloth", [(440, 80), (840, 80), (1050, 900), (230, 900)], "diag_shadow"),

    # Category 4: Cluttered / Textured / Complex Environments
    ("16_high_noise_background", "wood", [(340, 90), (960, 90), (930, 890), (330, 870)], "noise"),
    ("17_low_contrast_page_edges", "tablecloth", [(320, 80), (970, 70), (940, 890), (310, 870)], "low_contrast"),
    ("18_close_cropped_corners", "desk", [(180, 40), (1100, 30), (1070, 930), (150, 920)], "none"),
    ("19_curved_skew_effect", "wood", [(360, 100), (950, 80), (900, 880), (300, 840)], "vignette"),
    ("20_mixed_shadow_high_angle", "dark", [(460, 90), (820, 80), (1060, 920), (220, 910)], "half_shadow")
]

cw, ch = 1280, 960
for name, bg_style, pts, lighting in scenarios:
    bg = get_background(bg_style, cw, ch)
    target_pts = np.float32(pts)
    H = cv2.getPerspectiveTransform(doc_corners, target_pts)
    
    # Warp doc onto canvas
    warped_doc = cv2.warpPerspective(base_doc, H, (cw, ch), borderValue=(0,0,0))
    
    # Create mask for document
    mask = cv2.warpPerspective(np.ones((dh, dw), dtype=np.uint8)*255, H, (cw, ch), borderValue=0)
    
    # Combine doc with background
    inv_mask = cv2.bitwise_not(mask)
    bg_part = cv2.bitwise_and(bg, bg, mask=inv_mask)
    doc_part = cv2.bitwise_and(warped_doc, warped_doc, mask=mask)
    final_img = cv2.add(bg_part, doc_part)
    
    # Apply Lighting / Shadows
    if lighting == "diag_shadow":
        sh = np.ones((ch, cw), dtype=np.float32)
        for y in range(ch):
            for x in range(cw):
                if x + y > 1000:
                    sh[y, x] = max(0.45, 1.0 - (x + y - 1000) * 0.0007)
        final_img = np.clip(final_img.astype(np.float32) * sh[..., None], 0, 255).astype(np.uint8)
    elif lighting == "corner_shadow":
        cv2.circle(final_img, (int(cw*0.7), int(ch*0.7)), 350, (0, 0, 0), -1)
        blur_circ = cv2.GaussianBlur(final_img, (99, 99), 40)
        final_img = cv2.addWeighted(final_img, 0.75, blur_circ, 0.25, 0)
    elif lighting == "half_shadow":
        sh = np.ones((ch, cw), dtype=np.float32)
        sh[int(ch*0.45):, :] = 0.55
        sh = cv2.GaussianBlur(sh, (71, 71), 25)
        final_img = np.clip(final_img.astype(np.float32) * sh[..., None], 0, 255).astype(np.uint8)
    elif lighting == "vignette":
        Y, X = np.ogrid[:ch, :cw]
        dist = np.sqrt((X - cw/2)**2 + (Y - ch/2)**2)
        vignette = 1.0 - np.clip((dist - 300) / 700, 0, 0.55)
        final_img = np.clip(final_img.astype(np.float32) * vignette[..., None], 0, 255).astype(np.uint8)
    elif lighting == "noise":
        noise = np.random.normal(0, 12, final_img.shape).astype(np.int16)
        final_img = np.clip(final_img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    save_path = f"test_dataset/{name}.jpg"
    cv2.imwrite(save_path, final_img)

print(f"Generated 20 benchmark test photos successfully in test_dataset/")
