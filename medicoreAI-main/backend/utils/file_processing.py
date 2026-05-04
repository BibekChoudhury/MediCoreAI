"""
Utilities for preparing image/PDF bytes before sending to Groq Vision.

Groq limits:
  - Input must be a real image (JPEG/PNG/WEBP/GIF) — raw PDFs are rejected
  - Max ~33,177,600 pixels per image
"""
import io
import logging
import math

import fitz  # PyMuPDF
from PIL import Image

logger = logging.getLogger(__name__)

# Leave a small margin below Groq's hard limit of 33,177,600 px
GROQ_MAX_PIXELS = 32_000_000


def _resize_pil_if_needed(img: Image.Image) -> Image.Image:
    """Downscale a PIL image if it exceeds GROQ_MAX_PIXELS, preserving aspect ratio."""
    w, h = img.size
    if w * h > GROQ_MAX_PIXELS:
        scale = math.sqrt(GROQ_MAX_PIXELS / (w * h))
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        logger.info("Resizing image from %dx%d to %dx%d to meet Groq pixel limit", w, h, new_w, new_h)
        img = img.resize((new_w, new_h), Image.LANCZOS)
    return img


def _pil_to_jpeg_bytes(img: Image.Image, quality: int = 88) -> bytes:
    img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def _pdf_bytes_to_pil(pdf_bytes: bytes) -> Image.Image:
    """
    Render every page of a PDF at 150 DPI and stitch them vertically.
    Falls back to the first page only if the combined image would be enormous.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    # Scale factor: 1.5 ≈ 108 DPI — good quality, sane file sizes
    matrix = fitz.Matrix(1.5, 1.5)

    page_images: list[Image.Image] = []
    for page in doc:
        pix = page.get_pixmap(matrix=matrix)
        page_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        page_images.append(page_img)

    if not page_images:
        raise ValueError("PDF appears to have no pages.")

    if len(page_images) == 1:
        return page_images[0]

    # Stitch pages vertically (same width, the max of all page widths)
    max_w = max(img.width for img in page_images)
    total_h = sum(img.height for img in page_images)

    combined = Image.new("RGB", (max_w, total_h), (255, 255, 255))
    y_offset = 0
    for img in page_images:
        combined.paste(img, (0, y_offset))
        y_offset += img.height

    return combined


def prepare_for_groq(file_bytes: bytes, content_type: str) -> tuple[bytes, str]:
    """
    Convert file bytes into a Groq-compatible JPEG image.

    - PDFs are rendered to images via PyMuPDF (all pages, stitched vertically).
    - Oversized images are downscaled to fit within Groq's pixel limit.

    Returns:
        (jpeg_bytes, "image/jpeg")
    """
    if content_type == "application/pdf" or content_type == "application/octet-stream":
        # Try PDF rendering; fall back to treating as image if fitz rejects it
        try:
            pil_img = _pdf_bytes_to_pil(file_bytes)
        except Exception as exc:
            # Not a valid PDF stream — try opening as image instead
            logger.warning("fitz could not open as PDF (%s); trying as image", exc)
            pil_img = Image.open(io.BytesIO(file_bytes))
    else:
        pil_img = Image.open(io.BytesIO(file_bytes))

    pil_img = _resize_pil_if_needed(pil_img)
    return _pil_to_jpeg_bytes(pil_img), "image/jpeg"
