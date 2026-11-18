# DocuScan — Document Scanner App

## Run locally
1. Install Python 3.10+.
2. Extract the ZIP and open a terminal in the folder.
3. Run `pip install -r requirements.txt`.
4. Run `streamlit run app.py`.
5. Open the local URL Streamlit prints (normally http://localhost:8501).

## Features
- Automatic page corner detection (Canny edges, contours, quadrilateral approximation).
- Manual corner fallback with pixel-coordinate inputs.
- Own 8×8 homography solve using NumPy, with h33 fixed to 1.
- Own inverse mapping and bilinear interpolation.
- Comparison with OpenCV warpPerspective and difference heat map.
- Grayscale, adaptive threshold, colour enhancement and basic shadow removal.
- Single-page and multi-page PDF export.
- Batch processing up to 20 photos with success-rate calculation.

## Notes
Automatic detection can fail on low-contrast pages, busy backgrounds, curled paper, shadows or cropped edges. Use manual corner fallback in those cases. The batch success rate is based on the images you test; for the assignment, use 20 varied photos and report the actual outcomes. Shadow removal is a basic normalization method. OCR and real-time video are stretch goals and are not included.
