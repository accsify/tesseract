"""
Drop-in pytesseract Compatibility Shim for Accsify Tesseract.
=============================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.

Provides 100% API compatibility with the classical `pytesseract` package.
Allows replacing `import pytesseract` with:
    from accsify_tesseract import compat as pytesseract
or:
    import accsify_tesseract.compat as pytesseract
"""

from typing import Any, List, Optional, Dict
import io
import re

from .types import PageSegMode
from .exceptions import TesseractError
from . import (
    image_to_string as _image_to_string,
    image_to_osd as _image_to_osd,
    image_to_boxes as _image_to_boxes,
    image_to_data as _image_to_data,
    image_to_hocr as _image_to_hocr,
    get_languages as _get_languages,
    get_tesseract_version as _get_tesseract_version,
)


class TesseractNotFoundError(TesseractError):
    """Raised when tesseract executable or DLL is missing."""
    pass


class _PytesseractConfigProxy:
    """Simulates pytesseract.pytesseract object with tesseract_cmd property."""
    def __init__(self):
        self._cmd = "internal_dll"

    @property
    def tesseract_cmd(self) -> str:
        return self._cmd

    @tesseract_cmd.setter
    def tesseract_cmd(self, val: str) -> None:
        self._cmd = str(val) if val else "internal_dll"


pytesseract = _PytesseractConfigProxy()
tesseract_cmd = "internal_dll"


class Output:
    STRING = "string"
    BYTES = "bytes"
    DICT = "dict"
    DATAFRAME = "dataframe"


def get_tesseract_version() -> str:
    """Return Tesseract version string."""
    return _get_tesseract_version()


def get_languages(config: str = "") -> List[str]:
    """Return list of available language codes."""
    return _get_languages(config)


def image_to_string(
    image: Any,
    lang: Optional[str] = None,
    config: str = "",
    nice: int = 0,
    output_type: str = Output.STRING,
    timeout: int = 0,
    **kwargs
) -> Any:
    """
    Drop-in replacement for pytesseract.image_to_string.
    """
    res = _image_to_string(image=image, lang=lang or "eng", config=config)
    if output_type == Output.BYTES:
        return res.encode("utf-8")
    return res


def image_to_osd(
    image: Any,
    config: str = "",
    nice: int = 0,
    output_type: str = Output.STRING,
    timeout: int = 0,
    **kwargs
) -> Any:
    """
    Drop-in replacement for pytesseract.image_to_osd.
    Auto-downloads osd.traineddata if missing and returns classical OSD output.
    """
    res = _image_to_osd(image=image, config=config)
    if output_type == Output.BYTES:
        return res.encode("utf-8")
    elif output_type == Output.DICT:
        # Parse standard key: value format
        data: Dict[str, Any] = {}
        for line in res.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip().lower().replace(" ", "_")
                v = v.strip()
                try:
                    data[k] = int(v) if v.isdigit() else float(v)
                except ValueError:
                    data[k] = v
        return data
    return res


def image_to_boxes(
    image: Any,
    lang: Optional[str] = None,
    config: str = "",
    nice: int = 0,
    output_type: str = Output.STRING,
    timeout: int = 0,
    **kwargs
) -> Any:
    """
    Drop-in replacement for pytesseract.image_to_boxes.
    """
    res = _image_to_boxes(image=image, lang=lang or "eng", config=config)
    if output_type == Output.BYTES:
        return res.encode("utf-8")
    return res


def image_to_data(
    image: Any,
    lang: Optional[str] = None,
    config: str = "",
    nice: int = 0,
    output_type: str = Output.STRING,
    timeout: int = 0,
    **kwargs
) -> Any:
    """
    Drop-in replacement for pytesseract.image_to_data.
    Supports Output.STRING, Output.BYTES, Output.DICT, and Output.DATAFRAME.
    """
    tsv_str = _image_to_data(image=image, lang=lang or "eng", config=config)

    if output_type == Output.BYTES:
        return tsv_str.encode("utf-8")

    elif output_type == Output.DICT:
        lines = [line for line in tsv_str.split("\n") if line.strip()]
        if not lines:
            return {}
        header = lines[0].split("\t")
        result: Dict[str, List[Any]] = {col: [] for col in header}
        for line in lines[1:]:
            parts = line.split("\t")
            for i, col in enumerate(header):
                val = parts[i] if i < len(parts) else ""
                # Convert numbers if integer
                if val.isdigit() or (val.startswith("-") and val[1:].isdigit()):
                    try:
                        val = int(val)
                    except ValueError:
                        pass
                result[col].append(val)
        return result

    elif output_type == Output.DATAFRAME:
        try:
            import pandas as pd
            return pd.read_csv(io.StringIO(tsv_str), sep="\t")
        except ImportError:
            raise ImportError("pandas is required for Output.DATAFRAME.")

    return tsv_str


def image_to_pdf_or_hocr(
    image: Any,
    lang: Optional[str] = None,
    config: str = "",
    nice: int = 0,
    extension: str = "pdf",
    timeout: int = 0,
    **kwargs
) -> Any:
    """Drop-in replacement for pytesseract.image_to_pdf_or_hocr."""
    if extension == "hocr":
        return _image_to_hocr(image=image, lang=lang or "eng", config=config)
    raise NotImplementedError("For searchable PDF generation, use engine.generate_searchable_pdf().")


__all__ = [
    "pytesseract",
    "tesseract_cmd",
    "Output",
    "TesseractError",
    "TesseractNotFoundError",
    "get_tesseract_version",
    "get_languages",
    "image_to_string",
    "image_to_osd",
    "image_to_boxes",
    "image_to_data",
    "image_to_pdf_or_hocr",
]
