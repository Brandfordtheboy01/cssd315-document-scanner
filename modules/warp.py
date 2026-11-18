"""
Custom Warp & Bilinear Interpolation Engine
CSSD 315 Computer Graphics - Group Project (Brief 6)

Contains:
1. Pure NumPy vectorized bilinear interpolation
2. Inverse mapping loop (mapping destination grid -> source space)
3. Quantitative comparison against OpenCV warpPerspective
"""

import numpy as np
import cv2

def bilinear_sample(image, map_x, map_y):
    """
    Samples pixels at non-integer coordinates (map_x, map_y)
    using Bilinear Interpolation.
    
    Formula:
      f(x, y) = (1 - dx)(1 - dy)*I(x0, y0) + 
                dx*(1 - dy)*I(x1, y0) + 
                (1 - dx)*dy*I(x0, y1) + 
                dx*dy*I(x1, y1)
    """
    h, w = image.shape[:2]
    
    # Clip coordinates to valid image bounds
    x = np.clip(map_x, 0, w - 1.001)
    y = np.clip(map_y, 0, h - 1.001)
    
    x0 = x.astype(np.int32)
    y0 = y.astype(np.int32)
    x1 = np.minimum(x0 + 1, w - 1)
    y1 = np.minimum(y0 + 1, h - 1)
    
    # Fractional offsets
    dx = (x - x0)[..., None]
    dy = (y - y0)[..., None]
    
    # Neighbor intensity values
    Ia = image[y0, x0].astype(np.float64)
    Ib = image[y0, x1].astype(np.float64)
    Ic = image[y1, x0].astype(np.float64)
    Id = image[y1, x1].astype(np.float64)
    
    # Weighted blend
    interp = (Ia * (1.0 - dx) * (1.0 - dy) +
              Ib * dx * (1.0 - dy) +
              Ic * (1.0 - dx) * dy +
              Id * dx * dy)
              
    return np.clip(interp, 0, 255).astype(np.uint8)

def custom_warp_perspective(image, H, out_w, out_h):
    """
    Warps an image using inverse mapping:
    For every pixel (u, v) in destination rectangle:
      [x, y, w]^T = H_inv * [u, v, 1]^T
      x_src = x / w
      y_src = y / w
    Sample at (x_src, y_src) via bilinear interpolation.
    """
    H_inv = np.linalg.inv(H)
    
    # Generate grid of destination coordinates
    v_coords, u_coords = np.indices((out_h, out_w), dtype=np.float64)
    
    # Destination homogeneous points (3 x N)
    dst_pts_homog = np.stack([u_coords.ravel(), v_coords.ravel(), np.ones(out_w * out_h)])
    
    # Map back to source homogeneous coordinates
    src_pts_homog = H_inv @ dst_pts_homog
    
    # Perspective division
    src_x = (src_pts_homog[0] / src_pts_homog[2]).reshape(out_h, out_w).astype(np.float32)
    src_y = (src_pts_homog[1] / src_pts_homog[2]).reshape(out_h, out_w).astype(np.float32)
    
    # Sample source image
    warped = bilinear_sample(image, src_x, src_y)
    
    # Mask out-of-bound pixels as white background
    valid_mask = (src_x >= 0) & (src_x < image.shape[1]) & (src_y >= 0) & (src_y < image.shape[0])
    warped[~valid_mask] = 255
    
    return warped

def compare_with_opencv(image, H, out_w, out_h):
    """
    Computes custom warp vs OpenCV cv2.warpPerspective,
    calculates mean absolute difference and difference heat map.
    """
    custom_res = custom_warp_perspective(image, H, out_w, out_h)
    cv_res = cv2.warpPerspective(image, H, (out_w, out_h), flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255))
    
    diff = cv2.absdiff(custom_res, cv_res)
    mean_error = np.mean(diff)
    max_error = np.max(diff)
    
    # Generate color heatmap of differences (JET)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    heatmap = cv2.applyColorMap(diff_gray * 10, cv2.COLORMAP_JET) # scaled for visibility
    
    return custom_res, cv_res, mean_error, max_error, heatmap
