"""
Synthetic Test Image Generator for Accsify Tesseract.
======================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.

Generates high-resolution test images containing both Left-To-Right (English)
and Right-To-Left (Arabic) text with proper Uniscribe glyph shaping.
"""

import sys
import ctypes
from ctypes import wintypes
from pathlib import Path
from typing import Optional, Union, Tuple, Any

try:
    from PIL import Image
    _HAVE_PIL = True
except ImportError:
    Image = None  # type: ignore
    _HAVE_PIL = False


def _render_with_windows_gdi(
    width: int,
    height: int,
    elements: list
) -> Any:
    """
    Render text elements onto a high-contrast bitmap using native Windows GDI
    with full Uniscribe support for bidirectional (BiDi) Arabic shaping.
    """
    if not _HAVE_PIL:
        raise ImportError(
            "Pillow is required for synthetic test image generation. "
            "Please install it with: pip install pillow"
        )
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32

    hdc_screen = user32.GetDC(0)
    hdc = gdi32.CreateCompatibleDC(hdc_screen)

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ('biSize', wintypes.DWORD),
            ('biWidth', wintypes.LONG),
            ('biHeight', wintypes.LONG),
            ('biPlanes', wintypes.WORD),
            ('biBitCount', wintypes.WORD),
            ('biCompression', wintypes.DWORD),
            ('biSizeImage', wintypes.DWORD),
            ('biXPelsPerMeter', wintypes.LONG),
            ('biYPelsPerMeter', wintypes.LONG),
            ('biClrUsed', wintypes.DWORD),
            ('biClrImportant', wintypes.DWORD)
        ]

    bmi = BITMAPINFOHEADER()
    bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.biWidth = width
    bmi.biHeight = -height  # Negative for top-down DIB
    bmi.biPlanes = 1
    bmi.biBitCount = 24
    bmi.biCompression = 0

    p_bits = ctypes.c_void_p()
    hbmp = gdi32.CreateDIBSection(hdc, ctypes.byref(bmi), 0, ctypes.byref(p_bits), None, 0)
    old_bmp = gdi32.SelectObject(hdc, hbmp)

    class RECT(ctypes.Structure):
        _fields_ = [
            ('left', wintypes.LONG),
            ('top', wintypes.LONG),
            ('right', wintypes.LONG),
            ('bottom', wintypes.LONG)
        ]

    # Fill crisp white background
    white_brush = gdi32.CreateSolidBrush(0x00FFFFFF)
    rc_full = RECT(0, 0, width, height)
    user32.FillRect(hdc, ctypes.byref(rc_full), white_brush)
    gdi32.DeleteObject(white_brush)

    # Set transparent text background
    gdi32.SetBkMode(hdc, 1)  # TRANSPARENT
    gdi32.SetTextColor(hdc, 0x00000000)  # Pure Black

    # DT flags
    DT_LEFT = 0x0000
    DT_RIGHT = 0x0002
    DT_CENTER = 0x0001
    DT_RTLREADING = 0x00020000

    fonts_cache = {}

    for elem in elements:
        text = elem["text"]
        font_size = elem.get("size", 28)
        weight = elem.get("weight", 400)
        font_family = elem.get("font", "Arial")
        is_rtl = elem.get("rtl", False)
        align = elem.get("align", "right" if is_rtl else "left")
        rect_coords = elem["rect"]

        # Cache created fonts
        fkey = (font_family, font_size, weight)
        if fkey not in fonts_cache:
            hfont = gdi32.CreateFontW(
                font_size, 0, 0, 0, weight, 0, 0, 0, 1, 0, 0, 4, 0, font_family
            )
            fonts_cache[fkey] = hfont

        hfont = fonts_cache[fkey]
        old_font = gdi32.SelectObject(hdc, hfont)

        # Flags calculation
        flags = DT_RTLREADING if is_rtl else 0
        if align == "center":
            flags |= DT_CENTER
        elif align == "right":
            flags |= DT_RIGHT
        else:
            flags |= DT_LEFT

        rc = RECT(rect_coords[0], rect_coords[1], rect_coords[2], rect_coords[3])
        user32.DrawTextW(hdc, text, -1, ctypes.byref(rc), flags)
        gdi32.SelectObject(hdc, old_font)

    # Read back image bytes
    stride = ((width * 3 + 3) // 4) * 4
    buf = (ctypes.c_char * (stride * height)).from_address(p_bits.value)
    raw_bytes = bytes(buf)

    # Cleanup GDI handles
    for f in fonts_cache.values():
        gdi32.DeleteObject(f)
    gdi32.SelectObject(hdc, old_bmp)
    gdi32.DeleteObject(hbmp)
    gdi32.DeleteDC(hdc)
    user32.ReleaseDC(0, hdc_screen)

    # Convert BGR DIB buffer to PIL RGB Image
    img = Image.frombytes("RGB", (width, height), raw_bytes, "raw", "BGR", stride, 1)
    return img


def generate_sample_document(
    output_path: Optional[Union[str, Path]] = None,
    width: int = 1200,
    height: int = 750
) -> Any:
    """
    Generate a bilingual (Arabic + English) document test image.
    Contains both LTR and RTL sections, metadata numbers, and headings.
    """
    elements = [
        # Document Title (English LTR)
        {
            "text": "Accsify Tesseract Native OCR Engine",
            "rect": (60, 40, width - 60, 95),
            "size": 42,
            "weight": 700,
            "rtl": False,
            "align": "left",
        },
        # Document Subtitle (Arabic RTL)
        {
            "text": "محرك التعرف الضوئي على الحروف - أكسيفاي",
            "rect": (60, 110, width - 60, 170),
            "size": 38,
            "weight": 700,
            "rtl": True,
            "align": "right",
        },
        # English Paragraph
        {
            "text": "High Performance C++20 Core with Python 3.14 Bindings and Native DLL.",
            "rect": (60, 200, width - 60, 245),
            "size": 26,
            "weight": 400,
            "rtl": False,
            "align": "left",
        },
        {
            "text": "Engineered for speed, thread safety, and zero external runtime dependencies.",
            "rect": (60, 250, width - 60, 295),
            "size": 24,
            "weight": 400,
            "rtl": False,
            "align": "left",
        },
        # Arabic Paragraph
        {
            "text": "دعم كامل للغة العربية والإنجليزية وقراءة النصوص ثنائية الاتجاه بدقة فائقة.",
            "rect": (60, 325, width - 60, 375),
            "size": 28,
            "weight": 400,
            "rtl": True,
            "align": "right",
        },
        {
            "text": "معالجة المستندات متعددة اللغات واستخراج الكتل والفقرات والكلمات وإحداثياتها.",
            "rect": (60, 385, width - 60, 435),
            "size": 26,
            "weight": 400,
            "rtl": True,
            "align": "right",
        },
        # Metadata / Codes / Numbers (English)
        {
            "text": "Invoice Reference: #INV-2026-9821 | Status: APPROVED | Total: $4,580.00 USD",
            "rect": (60, 475, width - 60, 525),
            "size": 26,
            "weight": 600,
            "rtl": False,
            "align": "left",
        },
        # Metadata / Codes / Numbers (Arabic)
        {
            "text": "رقم الفاتورة: ٩٨٢١ - الحالة: معتمدة - المبلغ الإجمالي: ٤٥٨٠ دولار أمريكي",
            "rect": (60, 545, width - 60, 595),
            "size": 26,
            "weight": 600,
            "rtl": True,
            "align": "right",
        },
        # Footer
        {
            "text": "Copyright (C) 2026 accsify. All rights reserved. | جميع الحقوق محفوظة لشركة أكسيفاي",
            "rect": (60, 660, width - 60, 705),
            "size": 20,
            "weight": 400,
            "rtl": False,
            "align": "center",
        },
    ]

    img = _render_with_windows_gdi(width, height, elements)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(out))

    return img


def generate_sample_receipt(
    output_path: Optional[Union[str, Path]] = None,
    width: int = 850,
    height: int = 1000
) -> Any:
    """
    Generate a bilingual commercial receipt test image with tabular columns.
    """
    elements = [
        # Store Header
        {
            "text": "ACCOSIFY RETAIL TECHNOLOGY",
            "rect": (40, 40, width - 40, 90),
            "size": 36,
            "weight": 700,
            "rtl": False,
            "align": "center",
        },
        {
            "text": "شركة أكسيفاي للتقنيات والحلول البرمجية",
            "rect": (40, 100, width - 40, 150),
            "size": 30,
            "weight": 700,
            "rtl": True,
            "align": "center",
        },
        {
            "text": "Branch #104 - Al-Olaya District, Riyadh, KSA",
            "rect": (40, 160, width - 40, 200),
            "size": 22,
            "weight": 400,
            "rtl": False,
            "align": "center",
        },
        {
            "text": "--------------------------------------------------------------------------------",
            "rect": (40, 210, width - 40, 235),
            "size": 20,
            "weight": 400,
            "rtl": False,
            "align": "center",
        },
        # Table Header
        {
            "text": "Description / الوصف",
            "rect": (40, 250, 400, 290),
            "size": 22,
            "weight": 700,
            "rtl": False,
            "align": "left",
        },
        {
            "text": "Qty",
            "rect": (480, 250, 550, 290),
            "size": 22,
            "weight": 700,
            "rtl": False,
            "align": "center",
        },
        {
            "text": "Price (USD)",
            "rect": (600, 250, width - 40, 290),
            "size": 22,
            "weight": 700,
            "rtl": False,
            "align": "right",
        },
        # Line 1
        {
            "text": "Laptop Workstation / حاسوب محمول",
            "rect": (40, 310, 460, 350),
            "size": 22,
            "weight": 400,
            "rtl": False,
            "align": "left",
        },
        {
            "text": "1",
            "rect": (480, 310, 550, 350),
            "size": 22,
            "weight": 400,
            "rtl": False,
            "align": "center",
        },
        {
            "text": "$1,450.00",
            "rect": (600, 310, width - 40, 350),
            "size": 22,
            "weight": 400,
            "rtl": False,
            "align": "right",
        },
        # Line 2
        {
            "text": "Mechanical Keyboard / لوحة مفاتيح",
            "rect": (40, 370, 460, 410),
            "size": 22,
            "weight": 400,
            "rtl": False,
            "align": "left",
        },
        {
            "text": "2",
            "rect": (480, 370, 550, 410),
            "size": 22,
            "weight": 400,
            "rtl": False,
            "align": "center",
        },
        {
            "text": "$180.00",
            "rect": (600, 370, width - 40, 410),
            "size": 22,
            "weight": 400,
            "rtl": False,
            "align": "right",
        },
        # Line 3
        {
            "text": "Laser Mouse Pro / فارة ليزرية",
            "rect": (40, 430, 460, 470),
            "size": 22,
            "weight": 400,
            "rtl": False,
            "align": "left",
        },
        {
            "text": "2",
            "rect": (480, 430, 550, 470),
            "size": 22,
            "weight": 400,
            "rtl": False,
            "align": "center",
        },
        {
            "text": "$75.00",
            "rect": (600, 430, width - 40, 470),
            "size": 22,
            "weight": 400,
            "rtl": False,
            "align": "right",
        },
        # Separator
        {
            "text": "--------------------------------------------------------------------------------",
            "rect": (40, 490, width - 40, 515),
            "size": 20,
            "weight": 400,
            "rtl": False,
            "align": "center",
        },
        # Subtotal
        {
            "text": "Subtotal / المجموع الفرعي:",
            "rect": (40, 530, 500, 570),
            "size": 22,
            "weight": 400,
            "rtl": False,
            "align": "left",
        },
        {
            "text": "$1,705.00",
            "rect": (550, 530, width - 40, 570),
            "size": 22,
            "weight": 400,
            "rtl": False,
            "align": "right",
        },
        # Tax
        {
            "text": "VAT (15%) / ضريبة القيمة المضافة:",
            "rect": (40, 580, 500, 620),
            "size": 22,
            "weight": 400,
            "rtl": False,
            "align": "left",
        },
        {
            "text": "$255.75",
            "rect": (550, 580, width - 40, 620),
            "size": 22,
            "weight": 400,
            "rtl": False,
            "align": "right",
        },
        # Grand Total
        {
            "text": "NET TOTAL / الإجمالي النهائي:",
            "rect": (40, 640, 500, 690),
            "size": 28,
            "weight": 700,
            "rtl": False,
            "align": "left",
        },
        {
            "text": "$1,960.75 USD",
            "rect": (550, 640, width - 40, 690),
            "size": 28,
            "weight": 700,
            "rtl": False,
            "align": "right",
        },
        # Thank You Message
        {
            "text": "شكرا لتعاملكم معنا - نتشرف بزيارتكم دائما",
            "rect": (40, 770, width - 40, 820),
            "size": 26,
            "weight": 600,
            "rtl": True,
            "align": "center",
        },
        {
            "text": "Thank you for shopping with Accsify!",
            "rect": (40, 830, width - 40, 870),
            "size": 22,
            "weight": 400,
            "rtl": False,
            "align": "center",
        },
    ]

    img = _render_with_windows_gdi(width, height, elements)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(out))

    return img
