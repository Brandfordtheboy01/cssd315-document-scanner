"""
Corner Detection & Contour Module
CSSD 315 Computer Graphics - Group Project (Brief 6)
High-precision detector for the 20 benchmark scenarios.
"""

import cv2
import numpy as np
from .homography import order_points

def auto_detect_corners(image):
    """
    Finds the 4 corners of a document with high accuracy.
    Uses multi-threshold Canny edge detection, morphological closing,
    and polygon contour approximation.
    """
    h, w = image.shape[:2]
    scale = min(1.0, 1000.0 / max(h, w))
    small = cv2.resize(image, (int(w * scale), int(h * scale))) if scale < 1.0 else image.copy()
    sh, sw = small.shape[:2]
    img_area = sh * sw
    
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Check edges across multiple threshold levels
    for low, high in [(30, 100), (20, 80), (50, 150), (15, 60)]:
        edges = cv2.Canny(blur, low, high)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
        dilated = cv2.dilate(closed, kernel, iterations=1)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]
        
        for c in contours:
            area = cv2.contourArea(c)
            if area < (0.08 * img_area) or area > (0.95 * img_area):
                continue
            peri = cv2.arcLength(c, True)
            for eps in [0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.05]:
                approx = cv2.approxPolyDP(c, eps * peri, True)
                if len(approx) == 4 and cv2.isContourConvex(approx):
                    raw_pts = approx.reshape(4, 2) / scale
                    return order_points(raw_pts), edges

    # Fallback default box if background is too noisy
    default_box = np.float32([
        [w * 0.15, h * 0.12],
        [w * 0.85, h * 0.12],
        [w * 0.85, h * 0.88],
        [w * 0.15, h * 0.88]
    ])
    debug_edges = cv2.Canny(blur, 40, 120)
    return order_points(default_box), debug_edges

def draw_corner_overlay(image, pts):
    """
    Renders visual indicator with numbered corners and connecting boundary.
    """
    vis = image.copy()
    if pts is None:
        return vis
        
    p = np.asarray(pts, dtype=np.int32)
    cv2.polylines(vis, [p], isClosed=True, color=(0, 220, 100), thickness=max(2, vis.shape[1] // 300))
    
    labels = ["1: TL", "2: TR", "3: BR", "4: BL"]
    colors = [(255, 60, 60), (60, 60, 255), (60, 200, 255), (255, 180, 60)]
    
    radius = max(8, vis.shape[1] // 80)
    for i, (x, y) in enumerate(p):
        cv2.circle(vis, (int(x), int(y)), radius, colors[i], -1)
        cv2.circle(vis, (int(x), int(y)), radius + 2, (255, 255, 255), 2)
        cv2.putText(
            vis, labels[i], (int(x) + 12, int(y) - 12),
            cv2.FONT_HERSHEY_SIMPLEX, max(0.5, vis.shape[1] // 1400),
            (255, 255, 255), 2, cv2.LINE_AA
        )
    return vis
