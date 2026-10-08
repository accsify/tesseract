"""
Accsify Tesseract OCR Engine - High-Performance Python Wrapper
==============================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.

This module re-exports the full accsify_tesseract package for convenience.
"""

from accsify_tesseract import (
    __version__,
    __company__,
    TesseractEngine,
    TesseractIterator,
    ModelManager,
    ModelInfo,
    PageLayout,
    LayoutElement,
    OrientationScriptResult,
    BoundingBox,
    PageSegMode,
    OcrEngineMode,
    PageIteratorLevel,
    WritingDirection,
    TextlineOrder,
    ModelType,
    TesseractError,
    EngineInitError,
    ImageLoadError,
    RecognitionError,
    ModelDownloadError,
    ModelNotFoundError,
    image_to_string,
)

__all__ = [
    "__version__,",
    "__company__",
    "TesseractEngine",
    "TesseractIterator",
    "ModelManager",
    "ModelInfo",
    "PageLayout",
    "LayoutElement",
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
]
