"""
Image Enhancement & Clean-up Pipeline
CSSD 315 Computer Graphics - Group Project (Brief 6)

Contains:
1. Grayscale
2. High-contrast adaptive thresholding (scanned document look)
3. Shadow removal via background illumination modeling
4. Color enhancement using CLAHE in LAB color space
"""

import cv2
import numpy as np

def apply_grayscale(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

def apply_adaptive_threshold(image, block_size=25, c=10):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c
    )
    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

def apply_shadow_removal(image):
    """
    Shadow removal via Illumination Estimation:
    1. Estimate non-uniform background lighting using heavy morphological or Gaussian blur.
    2. Divide original by the estimated background to normalize illumination.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Large kernel to capture background illumination gradient
    background = cv2.GaussianBlur(gray, (0, 0), sigmaX=35, sigmaY=35)
    
    # Division normalization: (image / background) * 255
    normalized = cv2.divide(gray, np.maximum(background, 1), scale=255)
    normalized = cv2.normalize(normalized, None, 0, 255, cv2.NORM_MINMAX)
    
    # Light adaptive thresholding on normalized image
    cleaned = cv2.adaptiveThreshold(
        normalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
    )
    return cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)

def apply_color_enhance(image):
    """
    Enhance colors without shifting hue by applying CLAHE
    to the L (Luminance) channel in CIE LAB color space.
    """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    enhanced_lab = cv2.merge((cl, a, b))
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
