"""
Multi-Page PDF Generator Module
CSSD 315 Computer Graphics - Group Project (Brief 6)
"""

from io import BytesIO
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import cv2

def bgr_to_pil(img_bgr):
    if img_bgr.ndim == 2:
        return Image.fromarray(img_bgr)
    return Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

def generate_pdf_bytes(cv2_images):
    """
    Renders a list of scanned images into a clean, printable A4 PDF.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    page_w, page_h = A4
    margin = 28 # standard margin in points
    
    for img in cv2_images:
        pil_img = bgr_to_pil(img).convert("RGB")
        w, h = pil_img.size
        
        # Fit image maintaining aspect ratio within printable boundaries
        scale = min((page_w - 2 * margin) / w, (page_h - 2 * margin) / h)
        render_w = w * scale
        render_h = h * scale
        
        x = (page_w - render_w) / 2.0
        y = (page_h - render_h) / 2.0
        
        c.drawImage(ImageReader(pil_img), x, y, width=render_w, height=render_h, mask='auto')
        c.showPage()
        
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
