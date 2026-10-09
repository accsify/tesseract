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
    return "1.0.6.2"


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

from .preprocessing import (
    extract_image_dpi,
    enhance_for_ocr,
)


def get_tesseract_version() -> str:
    """Return Tesseract engine version string."""
    try:
        return NativeLibrary.get().dll.tess_version().decode("utf-8")
    except Exception:
        return "5.5.0"


def get_languages(config: str = "") -> list:
    """Return list of available/installed language model names."""
    try:
        models = ModelManager.get_installed_models()
        if models:
            return [m.name for m in models]
    except Exception:
        pass
    return ["eng"]


def image_to_string(
    image,
    lang: str = "eng",
    config: str = "",
    psm: PageSegMode = None,
    datapath: str = None,
    enhance: bool = False,
    dpi: int = None
) -> str:
    """
    Convenient one-line OCR helper function returning plain text.
    
    Args:
        image: Path to image file, raw bytes, or PIL Image.
        lang: Language model name (default: 'eng').
        config: Optional command line flags (e.g. '--psm 11 -c tessedit_char_whitelist=...').
        psm: Optional PageSegMode enum override.
        datapath: Optional custom path to tessdata folder.
        enhance: Whether to apply Pillow contrast & sharpening preprocessing.
        dpi: Optional forced resolution in DPI.
        
    Returns:
        Recognized plain text string.
    """
    with TesseractEngine(datapath=datapath, language=lang, auto_download=True) as engine:
        if psm is not None:
            engine.set_page_seg_mode(psm)
        if config:
            engine.apply_config(config)
        engine.set_image(image, enhance=enhance, dpi=dpi)
        engine.recognize()
        return engine.get_text()


def image_to_osd(
    image,
    config: str = "",
    datapath: str = None,
    auto_download: bool = True
) -> str:
    """
    Run Orientation and Script Detection (OSD) and return formatted OSD string.
    
    Compatible with classical pytesseract format:
        Page number: 0
        Orientation in degrees: 0
        Rotate: 0
        Orientation confidence: 100.00
        Script: Latin
        Script confidence: 100.00
    """
    if auto_download and not ModelManager.is_installed("osd"):
        try:
            ModelManager.download("osd")
        except Exception:
            pass

    with TesseractEngine(datapath=datapath, language="osd", auto_download=auto_download) as engine:
        engine.set_page_seg_mode(PageSegMode.OSD_ONLY)
        if config:
            engine.apply_config(config)
        engine.set_image(image)

        # 1. Try native tess_get_osd_text
        try:
            txt = engine.get_osd_text(0)
            if txt and "Orientation in degrees:" in txt:
                return txt
        except Exception:
            pass

        # 2. Structured fallback matching exact pytesseract format
        try:
            osd = engine.detect_orientation_and_script()
            return (
                f"Page number: 0\n"
                f"Orientation in degrees: {osd.orientation_deg}\n"
                f"Rotate: {osd.orientation_deg}\n"
                f"Orientation confidence: {osd.orientation_confidence:.2f}\n"
                f"Script: {osd.script_name}\n"
                f"Script confidence: {osd.script_confidence:.2f}\n"
            )
        except Exception as e:
            raise RecognitionError(f"OSD detection failed: {e}")


def image_to_boxes(
    image,
    lang: str = "eng",
    config: str = "",
    datapath: str = None
) -> str:
    """Return recognized text in Tesseract Box format."""
    with TesseractEngine(datapath=datapath, language=lang, auto_download=True) as engine:
        if config:
            engine.apply_config(config)
        engine.set_image(image)
        engine.recognize()
        return engine.get_box(0)


def image_to_data(
    image,
    lang: str = "eng",
    config: str = "",
    datapath: str = None
) -> str:
    """Return recognized text in TSV (Tab-Separated Values) format with header."""
    with TesseractEngine(datapath=datapath, language=lang, auto_download=True) as engine:
        if config:
            engine.apply_config(config)
        engine.set_image(image)
        engine.recognize()
        tsv = engine.get_tsv(0)
        header = "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
        if not tsv.startswith("level\t"):
            return header + tsv
        return tsv


def image_to_hocr(
    image,
    lang: str = "eng",
    config: str = "",
    datapath: str = None
) -> str:
    """Return recognized text in HOCR format."""
    with TesseractEngine(datapath=datapath, language=lang, auto_download=True) as engine:
        if config:
            engine.apply_config(config)
        engine.set_image(image)
        engine.recognize()
        return engine.get_hocr(0)


def image_to_pdf(
    image_path: str,
    output_pdf_base: str,
    lang: str = "eng",
    datapath: str = None
) -> bool:
    """Generate a searchable PDF from an image file on disk."""
    with TesseractEngine(datapath=datapath, language=lang, auto_download=True) as engine:
        return engine.generate_searchable_pdf(image_path, output_pdf_base)


def image_to_json(
    image,
    lang: str = "eng",
    config: str = "",
    psm: PageSegMode = PageSegMode.AUTO,
    datapath: str = None
) -> str:
    """Convenient one-line OCR helper function returning structured JSON."""
    with TesseractEngine(datapath=datapath, language=lang, auto_download=True) as engine:
        engine.set_page_seg_mode(psm)
        if config:
            engine.apply_config(config)
        engine.set_image(image)
        engine.recognize()
        return engine.get_json()


def image_to_dict(
    image,
    lang: str = "eng",
    config: str = "",
    psm: PageSegMode = PageSegMode.AUTO,
    datapath: str = None
) -> dict:
    """Convenient one-line OCR helper function returning structured Python dictionary."""
    with TesseractEngine(datapath=datapath, language=lang, auto_download=True) as engine:
        engine.set_page_seg_mode(psm)
        if config:
            engine.apply_config(config)
        engine.set_image(image)
        engine.recognize()
        return engine.get_structured_dict()


from . import compat
pytesseract = compat


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
    "extract_image_dpi",
    "enhance_for_ocr",
    "get_tesseract_version",
    "get_languages",
    "image_to_string",
    "image_to_osd",
    "image_to_boxes",
    "image_to_data",
    "image_to_hocr",
    "image_to_pdf",
    "image_to_json",
    "image_to_dict",
    "generate_sample_document",
    "generate_sample_receipt",
    "compat",
    "pytesseract",
]
