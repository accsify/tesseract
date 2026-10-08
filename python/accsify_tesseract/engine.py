"""
High-Level OOP Tesseract Engine Interface.
==========================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

import os
import json
import ctypes
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union, List, Dict, Any

from .core import NativeLibrary
from .types import (
    PageSegMode, OcrEngineMode, PageIteratorLevel, BoundingBox, ModelType
)
from .layout import LayoutElement, PageLayout
from .osd import OrientationScriptResult
from .iterator import TesseractIterator
from .models import ModelManager
from .exceptions import (
    EngineInitError, ImageLoadError, RecognitionError
)


@dataclass
class BatchOcrResult:
    """Structured result for a single image in batch recognition."""
    image_path: Optional[str]
    text: str
    mean_confidence: int
    psm: PageSegMode
    words_count: int
    structured_data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image": self.image_path,
            "text": self.text,
            "mean_confidence": self.mean_confidence,
            "psm": self.psm.name,
            "words_count": self.words_count,
            "structured_data": self.structured_data,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


class TesseractEngine:
    """
    Main Accsify Tesseract OCR Engine instance.
    
    Provides thread-safe initialization, image loading, full OCR recognition,
    layout analysis, script detection, multi-image batch processing, and formatted exports.
    """

    def __init__(
        self,
        datapath: Optional[str] = None,
        language: str = "eng",
        flavor: Optional[ModelType] = None,
        oem: OcrEngineMode = OcrEngineMode.DEFAULT,
        auto_download: bool = False,
        custom_dll_path: Optional[str] = None
    ):
        self._lib = NativeLibrary.get(custom_dll_path)
        self._handle = self._lib.dll.tess_create()
        if not self._handle:
            raise MemoryError("Failed to allocate Tesseract engine handle.")

        if flavor is not None:
            ModelManager.set_flavor(flavor)
        active_flavor = flavor or ModelManager.get_flavor()

        # Handle multi-language parsing & auto-download if requested (e.g. "ara+eng")
        if auto_download:
            for sub_lang in language.split("+"):
                sub_lang = sub_lang.strip()
                if sub_lang and not ModelManager.is_installed(sub_lang, active_flavor):
                    ModelManager.download(sub_lang, active_flavor)

        dpath = datapath.encode("utf-8") if datapath else None
        res = self._lib.dll.tess_init(self._handle, dpath, language.encode("utf-8"), int(oem))
        if res != 0:
            active_path = ModelManager.get_path()
            self.close()
            raise EngineInitError(
                f"Failed to initialize Tesseract engine with language '{language}'.\n"
                f"Active tessdata directory: '{active_path}'.\n"
                f"Use ModelManager.download('{language}') to install the model file.",
                language=language,
                datapath=active_path,
                code=res
            )

    def __enter__(self) -> 'TesseractEngine':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        """Release native engine resources."""
        if self._handle:
            self._lib.dll.tess_destroy(self._handle)
            self._handle = None

    def __del__(self) -> None:
        self.close()

    @property
    def is_valid(self) -> bool:
        return self._handle is not None

    @classmethod
    def version(cls) -> str:
        """Get the underlying Tesseract version string."""
        lib = NativeLibrary.get()
        v = lib.dll.tess_version()
        return v.decode("utf-8") if v else "Unknown"

    def set_variable(self, name: str, value: str) -> bool:
        """Set an internal Tesseract variable (e.g. 'tessedit_char_whitelist')."""
        if not self._handle:
            return False
        return self._lib.dll.tess_set_variable(
            self._handle, name.encode("utf-8"), value.encode("utf-8")
        ) != 0

    def get_variable(self, name: str) -> Optional[str]:
        """Get the value of an internal Tesseract variable."""
        if not self._handle:
            return None
        buf = ctypes.create_string_buffer(256)
        if self._lib.dll.tess_get_variable(self._handle, name.encode("utf-8"), buf, 256):
            return buf.value.decode("utf-8")
        return None

    def set_page_seg_mode(self, psm: PageSegMode) -> None:
        """Set Page Segmentation Mode (PSM)."""
        if self._handle:
            self._lib.dll.tess_set_page_seg_mode(self._handle, int(psm))

    def get_page_seg_mode(self) -> PageSegMode:
        """Get current Page Segmentation Mode (PSM)."""
        if not self._handle:
            return PageSegMode.AUTO
        return PageSegMode(self._lib.dll.tess_get_page_seg_mode(self._handle))

    def set_resolution(self, ppi: int) -> None:
        """Set source image resolution in Pixels Per Inch (PPI)."""
        if self._handle:
            self._lib.dll.tess_set_source_resolution(self._handle, ppi)

    def set_image(self, image: Union[str, Path, bytes, bytearray, Any]) -> None:
        """
        Load an image into the engine.
        
        Supports:
          - File paths (str or Path): PNG, JPEG, TIFF, BMP, WebP, GIF
          - In-memory bytes / bytearray
          - PIL.Image.Image instances
          - NumPy image arrays (OpenCV ndarray)
        """
        if not self._handle:
            raise RuntimeError("Engine is closed.")

        if isinstance(image, (str, Path)):
            p = str(image)
            if not os.path.exists(p):
                raise ImageLoadError(f"Image file does not exist: {p}")
            res = self._lib.dll.tess_set_image_file(self._handle, p.encode("utf-8"))
            if res != 0:
                raise ImageLoadError(f"Failed to load image file: {p}")

        elif isinstance(image, (bytes, bytearray)):
            raw = bytes(image)
            c_buf = (ctypes.c_ubyte * len(raw)).from_buffer_copy(raw)
            res = self._lib.dll.tess_set_image_bytes(self._handle, c_buf, len(raw))
            if res != 0:
                raise ImageLoadError("Failed to decode image from memory buffer.")

        else:
            # Check for PIL Image
            if hasattr(image, "tobytes") and hasattr(image, "mode") and hasattr(image, "size"):
                w, h = image.size
                img_rgb = image.convert("RGB")
                raw = img_rgb.tobytes()
                c_buf = (ctypes.c_ubyte * len(raw)).from_buffer_copy(raw)
                res = self._lib.dll.tess_set_image_raw(self._handle, c_buf, w, h, 3, w * 3)
                if res != 0:
                    raise ImageLoadError("Failed to load image from PIL Image.")

            # Check for NumPy array (OpenCV)
            elif hasattr(image, "shape") and hasattr(image, "dtype") and hasattr(image, "tobytes"):
                h, w = image.shape[:2]
                channels = image.shape[2] if len(image.shape) > 2 else 1
                raw = image.tobytes()
                c_buf = (ctypes.c_ubyte * len(raw)).from_buffer_copy(raw)
                res = self._lib.dll.tess_set_image_raw(self._handle, c_buf, w, h, channels, w * channels)
                if res != 0:
                    raise ImageLoadError("Failed to load image from NumPy array.")

            else:
                raise TypeError(f"Unsupported image type: {type(image)}")

    def recognize(self) -> None:
        """Run OCR recognition pipeline on the currently loaded image."""
        if not self._handle:
            raise RuntimeError("Engine is closed.")
        res = self._lib.dll.tess_recognize(self._handle)
        if res != 0:
            raise RecognitionError("OCR recognition failed.")

    def get_text(self) -> str:
        """Get recognized UTF-8 plain text."""
        if not self._handle:
            return ""
        ptr = self._lib.dll.tess_get_utf8_text(self._handle)
        if not ptr:
            return ""
        try:
            return ctypes.string_at(ptr).decode("utf-8", errors="replace")
        finally:
            self._lib.dll.tess_free_text(ptr)

    def get_json(self) -> str:
        """
        Get full structured document analysis directly from native engine as JSON string.
        Includes full text, mean confidence, psm, and word elements with bounding boxes and writing directions.
        """
        if not self._handle:
            return "{}"
        ptr = self._lib.dll.tess_get_json_text(self._handle)
        if not ptr:
            return "{}"
        try:
            return ctypes.string_at(ptr).decode("utf-8", errors="replace")
        finally:
            self._lib.dll.tess_free_text(ptr)

    def get_structured_dict(self) -> Dict[str, Any]:
        """Get full structured document analysis parsed as a native Python dictionary."""
        raw_json = self.get_json()
        try:
            return json.loads(raw_json)
        except Exception:
            return {"text": self.get_text(), "mean_confidence": self.get_mean_confidence(), "words": []}

    def get_hocr(self, page_num: int = 0) -> str:
        """Get recognized text formatted as HOCR (HTML with bounding boxes)."""
        if not self._handle:
            return ""
        ptr = self._lib.dll.tess_get_hocr_text(self._handle, page_num)
        if not ptr:
            return ""
        try:
            return ctypes.string_at(ptr).decode("utf-8", errors="replace")
        finally:
            self._lib.dll.tess_free_text(ptr)

    def get_tsv(self, page_num: int = 0) -> str:
        """Get recognized text formatted as TSV (Tab-Separated Values)."""
        if not self._handle:
            return ""
        ptr = self._lib.dll.tess_get_tsv_text(self._handle, page_num)
        if not ptr:
            return ""
        try:
            return ctypes.string_at(ptr).decode("utf-8", errors="replace")
        finally:
            self._lib.dll.tess_free_text(ptr)

    def get_box(self, page_num: int = 0) -> str:
        """Get recognized text in Tesseract Box format."""
        if not self._handle:
            return ""
        ptr = self._lib.dll.tess_get_box_text(self._handle, page_num)
        if not ptr:
            return ""
        try:
            return ctypes.string_at(ptr).decode("utf-8", errors="replace")
        finally:
            self._lib.dll.tess_free_text(ptr)

    def get_unlv(self) -> str:
        """Get recognized text in UNLV format."""
        if not self._handle:
            return ""
        ptr = self._lib.dll.tess_get_unlv_text(self._handle)
        if not ptr:
            return ""
        try:
            return ctypes.string_at(ptr).decode("utf-8", errors="replace")
        finally:
            self._lib.dll.tess_free_text(ptr)

    def get_mean_confidence(self) -> int:
        """Get average recognition confidence percentage (0 to 100)."""
        if not self._handle:
            return 0
        return int(self._lib.dll.tess_get_mean_confidence(self._handle))

    def detect_orientation_and_script(self) -> OrientationScriptResult:
        """
        Detect page orientation degrees and writing script (requires 'osd.traineddata').
        """
        if not self._handle:
            raise RuntimeError("Engine is closed.")

        deg = ctypes.c_int()
        deg_conf = ctypes.c_float()
        s_name = ctypes.create_string_buffer(64)
        s_conf = ctypes.c_float()

        res = self._lib.dll.tess_detect_orientation_script(
            self._handle,
            ctypes.byref(deg),
            ctypes.byref(deg_conf),
            s_name,
            64,
            ctypes.byref(s_conf)
        )
        if res != 0:
            raise RecognitionError("Orientation & Script Detection failed. Ensure 'osd.traineddata' is installed.")

        return OrientationScriptResult(
            orientation_deg=deg.value,
            orientation_confidence=float(deg_conf.value),
            script_name=s_name.value.decode("utf-8"),
            script_confidence=float(s_conf.value)
        )

    def get_iterator(self) -> Optional[TesseractIterator]:
        """Obtain a low-level ResultIterator after recognition."""
        if not self._handle:
            return None
        ptr = self._lib.dll.tess_get_iterator(self._handle)
        if not ptr:
            return None
        return TesseractIterator(ptr, self._lib)

    def analyse_layout(self, level: PageIteratorLevel = PageIteratorLevel.WORD) -> PageLayout:
        """
        Run layout analysis and return structured elements with coordinates,
        writing directions, and confidences.
        """
        self.recognize()
        it = self.get_iterator()
        if not it or not it.is_valid:
            return PageLayout()

        elements: List[LayoutElement] = []
        try:
            while True:
                bbox = it.get_bounding_box(level)
                if bbox is not None:
                    txt = it.get_text(level).strip()
                    conf = it.get_confidence(level)
                    wdir = it.get_writing_direction()
                    torder = it.get_textline_order()
                    angle = it.get_deskew_angle()

                    elements.append(LayoutElement(
                        level=level,
                        text=txt,
                        confidence=conf,
                        bbox=bbox,
                        writing_direction=wdir,
                        textline_order=torder,
                        deskew_angle=angle
                    ))

                if not it.next(level):
                    break
        finally:
            it.close()

        return PageLayout(elements=elements)

    def recognize_batch(
        self,
        images: List[Union[str, Path, bytes, bytearray, Any]]
    ) -> List[BatchOcrResult]:
        """
        Process multiple images sequentially with high performance and return structured results.
        """
        results: List[BatchOcrResult] = []
        psm = self.get_page_seg_mode()

        for img in images:
            img_label = str(img) if isinstance(img, (str, Path)) else "<memory_buffer>"
            self.set_image(img)
            structured = self.get_structured_dict()
            words_list = structured.get("words", [])

            results.append(BatchOcrResult(
                image_path=img_label,
                text=structured.get("text", ""),
                mean_confidence=structured.get("mean_confidence", 0),
                psm=psm,
                words_count=len(words_list),
                structured_data=structured
            ))

        return results
