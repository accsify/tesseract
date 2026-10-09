"""
Accsify Tesseract - Official High-Performance Python Package
============================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.

Modern, thread-safe, object-oriented interface for the monolithic
standalone Tesseract OCR engine with WinHTTP model downloader.
"""

from pathlib import Path


def _resolve_version() -> str:
    pkg_dir = Path(__file__).resolve().parent
    for cand in (pkg_dir / "VERSION", pkg_dir.parent / "VERSION", pkg_dir.parent.parent / "VERSION"):
        if cand.is_file():
            v = cand.read_text(encoding="utf-8").strip()
            if v:
                return v
    return "1.0.5.1"


__version__ = _resolve_version()
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

from .core import (
    NativeLibrary,
    get_native_lib_dir,
    get_native_dll_path,
    get_native_cli_path,
)

from .engine import (
    TesseractEngine,
    BatchOcrResult,
)

from .sample_generator import (
    generate_sample_document,
    generate_sample_receipt,
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
    "NativeLibrary",
    "get_native_lib_dir",
    "get_native_dll_path",
    "get_native_cli_path",
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
    "generate_sample_document",
    "generate_sample_receipt",
]
