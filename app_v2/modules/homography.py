"""
Custom Homography Mathematics Module
CSSD 315 Computer Graphics - Group Project (Brief 6)

Contains:
1. Corner ordering (TL, TR, BR, BL)
2. Formulation of the 8x8 linear system Ah = b with h33 = 1
3. Solving via numpy.linalg.solve (from scratch, no cv2.findHomography)
4. Construction of the 3-point Affine transform for comparison
"""

import numpy as np

def order_points(pts):
    """
    Orders 4 coordinates into:
    [top-left, top-right, bottom-right, bottom-left]
    Uses sum (x+y) and difference (y-x or x-y) properties.
    """
    pts = np.asarray(pts, dtype=np.float32).reshape(4, 2)
    rect = np.zeros((4, 2), dtype=np.float32)

    # Top-left has smallest sum (x + y), bottom-right has largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)] # TL
    rect[2] = pts[np.argmax(s)] # BR

    # Top-right has smallest diff (x - y), bottom-left has largest diff (x - y)
    diff = pts[:, 0] - pts[:, 1]
    rect[1] = pts[np.argmax(diff)] # TR
    rect[3] = pts[np.argmin(diff)] # BL

    return rect

def compute_homography_8x8(src_pts, dst_pts):
    """
    Solves for the 3x3 Homography Matrix H from 4 point correspondences.
    
    Formula derivation:
    For each correspondence (x, y) -> (u, v):
      u = (h11*x + h12*y + h13) / (h31*x + h32*y + h33)
      v = (h21*x + h22*y + h23) / (h31*x + h32*y + h33)
      
    Setting h33 = 1 (scale normalization) yields 2 linear equations:
      h11*x + h12*y + h13 - h31*u*x - h32*u*y = u
      h21*x + h22*y + h23 - h31*v*x - h32*v*y = v
      
    Stacking 4 points gives an 8x8 system: A * h = b
    h is [h11, h12, h13, h21, h22, h23, h31, h32]^T
    """
    src = np.asarray(src_pts, dtype=np.float64)
    dst = np.asarray(dst_pts, dtype=np.float64)

    A = []
    b = []
    for i in range(4):
        x, y = src[i]
        u, v = dst[i]
        A.append([x, y, 1.0, 0.0, 0.0, 0.0, -u * x, -u * y])
        b.append(u)
        A.append([0.0, 0.0, 0.0, x, y, 1.0, -v * x, -v * y])
        b.append(v)

    A = np.array(A, dtype=np.float64)
    b = np.array(b, dtype=np.float64)

    # Solve the system Ah = b
    h = np.linalg.solve(A, b)
    
    # Append h33 = 1 and reshape to 3x3
    H = np.append(h, 1.0).reshape(3, 3)
    return H, A, b

def compute_affine_6x6(src_pts, dst_pts):
    """
    Computes a 3-point Affine transform matrix (6 DOF).
    Uses the first 3 points (TL, TR, BL).
    In an affine transform, the bottom row is strictly [0, 0, 1].
    Notice: It CANNOT account for non-parallel perspective convergence!
    """
    src = np.asarray(src_pts[:3], dtype=np.float64)
    dst = np.asarray(dst_pts[:3], dtype=np.float64)

    A = []
    b = []
    for i in range(3):
        x, y = src[i]
        u, v = dst[i]
        A.append([x, y, 1.0, 0.0, 0.0, 0.0])
        b.append(u)
        A.append([0.0, 0.0, 0.0, x, y, 1.0])
        b.append(v)

    A = np.array(A, dtype=np.float64)
    b = np.array(b, dtype=np.float64)

    m = np.linalg.solve(A, b)
    M_affine = np.array([
        [m[0], m[1], m[2]],
        [m[3], m[4], m[5]],
        [0.0,  0.0,  1.0]
    ], dtype=np.float64)
    return M_affine
