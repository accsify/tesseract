"""
Accsify Tesseract - Official High-Performance Python Package
============================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.

Modern, thread-safe, object-oriented interface for the monolithic
standalone Tesseract OCR engine with WinHTTP model downloader.
"""

__version__ = "5.5.0.1"
__company__ = "accsify"

from .types import (
    PageSegMode,
    OcrEngineMode,
    PageIteratorLevel,
    WritingDirection,
    TextlineOrder,
    ModelType,
    BoundingBox,
)

from .exceptions import (
    TesseractError,
    EngineInitError,
    ImageLoadError,
    RecognitionError,
    ModelDownloadError,
    ModelNotFoundError,
)

from .models import (
    ModelInfo,
    ModelManager,
)

from .osd import (
    OrientationScriptResult,
)

from .layout import (
    LayoutElement,
    LayoutSymbol,
    LayoutWord,
    LayoutLine,
    LayoutParagraph,
    LayoutBlock,
    PageLayout,
)

from .iterator import (
    TesseractIterator,
)

from .engine import (
    TesseractEngine,
    BatchOcrResult,
)


def image_to_string(
    image,
    lang: str = "eng",
    psm: PageSegMode = PageSegMode.AUTO,
    datapath: str = None
) -> str:
    """
    Convenient one-line OCR helper function returning plain text.
    
    Args:
        image: Path to image file, raw bytes, or PIL Image.
        lang: Language model name (default: 'eng').
        psm: Page segmentation mode.
        datapath: Optional custom path to tessdata folder.
        
    Returns:
        Recognized plain text string.
    """
    with TesseractEngine(datapath=datapath, language=lang) as engine:
        engine.set_page_seg_mode(psm)
        engine.set_image(image)
        engine.recognize()
        return engine.get_text()


def image_to_json(
    image,
    lang: str = "eng",
    psm: PageSegMode = PageSegMode.AUTO,
    datapath: str = None
) -> str:
    """
    Convenient one-line OCR helper function returning structured JSON.
    """
    with TesseractEngine(datapath=datapath, language=lang) as engine:
        engine.set_page_seg_mode(psm)
        engine.set_image(image)
        engine.recognize()
        return engine.get_json()


def image_to_dict(
    image,
    lang: str = "eng",
    psm: PageSegMode = PageSegMode.AUTO,
    datapath: str = None
) -> dict:
    """
    Convenient one-line OCR helper function returning structured Python dictionary.
    """
    with TesseractEngine(datapath=datapath, language=lang) as engine:
        engine.set_page_seg_mode(psm)
        engine.set_image(image)
        engine.recognize()
        return engine.get_structured_dict()


__all__ = [
    "__version__",
    "__company__",
    "TesseractEngine",
    "TesseractIterator",
    "BatchOcrResult",
    "ModelManager",
    "ModelInfo",
    "PageLayout",
    "LayoutElement",
    "LayoutSymbol",
    "LayoutWord",
    "LayoutLine",
    "LayoutParagraph",
    "LayoutBlock",
    "OrientationScriptResult",
    "BoundingBox",
    "PageSegMode",
    "OcrEngineMode",
    "PageIteratorLevel",
    "WritingDirection",
    "TextlineOrder",
    "ModelType",
    "TesseractError",
    "EngineInitError",
    "ImageLoadError",
    "RecognitionError",
    "ModelDownloadError",
    "ModelNotFoundError",
    "image_to_string",
    "image_to_json",
    "image_to_dict",
]
