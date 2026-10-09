"""
Image Preprocessing, DPI Normalization, and Enhancement Suite.
==============================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

from typing import Optional, Union, Tuple, Any
from pathlib import Path
import io

try:
    from PIL import Image, ImageOps, ImageFilter
except ImportError:
    Image = None
    ImageOps = None
    ImageFilter = None


def extract_image_dpi(image: Any) -> Optional[int]:
    """
    Extract DPI/PPI resolution from a Pillow Image or file if available.
    Returns None if no valid positive DPI is found.
    """
    if Image is None or not hasattr(image, "info"):
        return None
    dpi_info = image.info.get("dpi")
    if dpi_info:
        if isinstance(dpi_info, (tuple, list)) and len(dpi_info) > 0:
            try:
                val = int(round(float(dpi_info[0])))
                if val > 0:
                    return val
            except (ValueError, TypeError):
                pass
        elif isinstance(dpi_info, (int, float)):
            val = int(round(float(dpi_info)))
            if val > 0:
                return val
    return None


def enhance_for_ocr(
    image: Any,
    auto_contrast: bool = True,
    sharpen: bool = True,
    binarize: bool = False,
    max_dimension: Optional[int] = None
) -> Any:
    """
    Preprocess and enhance a PIL image to maximize Tesseract OCR accuracy.
    
    Features:
      - Ensures 24-bit RGB or 8-bit Grayscale color profile
      - Auto-contrast stretching to enhance faded ink/low-contrast text
      - Unsharp mask sharpening to clarify small fonts and blurred characters
      - Optional Otsu-style threshold binarization for receipts/noisy documents
      - Preserves original DPI metadata across all filter operations
    """
    if Image is None or not isinstance(image, Image.Image):
        return image

    img = image.convert("RGB")

    # Proportionally downscale if extraordinarily large
    if max_dimension and max(img.width, img.height) > max_dimension:
        ratio = float(max_dimension) / float(max(img.width, img.height))
        new_w = max(1, int(img.width * ratio))
        new_h = max(1, int(img.height * ratio))
        resample = getattr(Image, "Resampling", Image).BILINEAR
        img = img.resize((new_w, new_h), resample=resample)

    # 1. Auto-contrast normalization
    if auto_contrast and ImageOps is not None:
        try:
            img = ImageOps.autocontrast(img, cutoff=1)
        except Exception:
            pass

    # 2. Sharpening filter to clarify character edges
    if sharpen and ImageFilter is not None:
        try:
            img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=3))
        except Exception:
            pass

    # 3. Optional Otsu-like binarization
    if binarize:
        img_gray = img.convert("L")
        img = img_gray.point(lambda p: 255 if p > 128 else 0, mode="1").convert("RGB")

    # Preserve original DPI metadata
    if "dpi" in image.info:
        img.info["dpi"] = image.info["dpi"]

    return img
