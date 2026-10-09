"""
Low-Level C ABI Bindings and DLL Loader for Accsify Tesseract.
=============================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

import sys
import ctypes
from ctypes import (
    c_int, c_char_p, c_void_p, c_float, c_double,
    c_int32, c_int64, c_size_t, POINTER, Structure, CFUNCTYPE
)
from pathlib import Path
from typing import Optional


# C Structures matching tesseract_engine.h (#pragma pack(push, 8))
class CModelInfo(Structure):
    _pack_ = 8
    _fields_ = [
        ("name", ctypes.c_char * 64),
        ("display_name", ctypes.c_char * 128),
        ("model_type", c_int32),
        ("file_size", c_int64),
        ("download_url", ctypes.c_char * 256),
        ("is_installed", c_int32),
    ]


class CBoundingBox(Structure):
    _pack_ = 8
    _fields_ = [
        ("left", c_int32),
        ("top", c_int32),
        ("right", c_int32),
        ("bottom", c_int32),
    ]


# Callback prototype for download progress:
# int (*TessDownloadProgressCallback)(const char*, int, int64_t, int64_t, double, const char*, void*)
PROGRESS_CALLBACK_TYPE = CFUNCTYPE(
    c_int,
    c_char_p, c_int32, c_int64, c_int64, c_double, c_char_p, c_void_p
)


def get_native_lib_dir(arch: Optional[str] = None) -> Optional[Path]:
    """
    Return directory containing bundled native libraries for the specified architecture.
    Defaults to current Python process architecture ('x64' or 'x86').
    """
    if arch is None:
        arch = "x64" if sys.maxsize > 2**32 else "x86"
    pkg_dir = Path(__file__).resolve().parent
    for candidate in [
        pkg_dir / "lib" / arch,
        pkg_dir / "lib",
    ]:
        if candidate.is_dir():
            return candidate
    return None


def get_native_dll_path(arch: Optional[str] = None) -> Optional[Path]:
    """
    Return path to bundled or discovered tesseract_engine.dll.
    Natively searches the package's internal lib/ folder first, then external fallback directories.
    """
    if arch is None:
        arch = "x64" if sys.maxsize > 2**32 else "x86"
    pkg_dir = Path(__file__).resolve().parent

    # 1. First priority: Package-internal lib/ directory (bundled in wheel)
    internal_candidates = [
        pkg_dir / "lib" / arch / "tesseract_engine.dll",
        pkg_dir / "lib" / "tesseract_engine.dll",
    ]
    for p in internal_candidates:
        if p.is_file():
            return p

    # 2. Second priority: Main external and repository search directories
    repo_root = pkg_dir.parent.parent
    external_candidates = [
        repo_root / "dist" / arch / "tesseract_engine.dll",
        repo_root / "dist" / "tesseract_engine.dll",
        repo_root / "bin" / arch / "tesseract_engine.dll",
        repo_root / "build" / arch / "bin" / "tesseract_engine.dll",
        Path.cwd() / "dist" / arch / "tesseract_engine.dll",
        Path.cwd() / "dist" / "tesseract_engine.dll",
        Path.cwd() / "lib" / arch / "tesseract_engine.dll",
        Path.cwd() / "lib" / "tesseract_engine.dll",
        Path.cwd() / f"tesseract_engine_{arch}.dll",
        Path.cwd() / "tesseract_engine.dll",
    ]
    for p in external_candidates:
        if p.is_file():
            return p

    return None


def get_native_cli_path(arch: Optional[str] = None) -> Optional[Path]:
    """
    Return path to bundled or discovered tesseract_cli.exe executable.
    Natively searches the package's internal lib/ folder first, then external fallback directories.
    """
    if arch is None:
        arch = "x64" if sys.maxsize > 2**32 else "x86"
    pkg_dir = Path(__file__).resolve().parent

    # 1. First priority: Package-internal lib/ directory
    internal_candidates = [
        pkg_dir / "lib" / arch / "tesseract_cli.exe",
        pkg_dir / "lib" / "tesseract_cli.exe",
    ]
    for p in internal_candidates:
        if p.is_file():
            return p

    # 2. Second priority: Main external and repository search directories
    repo_root = pkg_dir.parent.parent
    external_candidates = [
        repo_root / "dist" / arch / "tesseract_cli.exe",
        repo_root / "dist" / "tesseract_cli.exe",
        repo_root / "bin" / arch / "tesseract_cli.exe",
        repo_root / "build" / arch / "bin" / "tesseract_cli.exe",
        Path.cwd() / "dist" / arch / "tesseract_cli.exe",
        Path.cwd() / "dist" / "tesseract_cli.exe",
        Path.cwd() / "lib" / arch / "tesseract_cli.exe",
        Path.cwd() / "lib" / "tesseract_cli.exe",
        Path.cwd() / f"tesseract_cli_{arch}.exe",
        Path.cwd() / "tesseract_cli.exe",
    ]
    for p in external_candidates:
        if p.is_file():
            return p

    return None


class NativeLibrary:
    """Singleton wrapper around loaded tesseract_engine.dll."""
    _instance: Optional['NativeLibrary'] = None

    def __init__(self, custom_dll_path: Optional[str] = None):
        self._dll = self._load_dll(custom_dll_path)
        self._bind_functions()

    @classmethod
    def get(cls, custom_dll_path: Optional[str] = None) -> 'NativeLibrary':
        if cls._instance is None:
            cls._instance = cls(custom_dll_path)
        return cls._instance

    @property
    def dll(self) -> ctypes.CDLL:
        return self._dll

    def _load_dll(self, custom_dll_path: Optional[str]) -> ctypes.CDLL:
        if custom_dll_path:
            p = Path(custom_dll_path)
            if not p.is_file():
                raise FileNotFoundError(f"Specified DLL path does not exist: {p}")
            return ctypes.CDLL(str(p))

        arch = "x64" if sys.maxsize > 2**32 else "x86"
        pkg_dir = Path(__file__).resolve().parent
        repo_root = pkg_dir.parent.parent

        # 1. Check native package lib directory first
        internal_dlls = [
            pkg_dir / "lib" / arch / "tesseract_engine.dll",
            pkg_dir / "lib" / "tesseract_engine.dll",
        ]
        for p in internal_dlls:
            if p.is_file():
                try:
                    return ctypes.CDLL(str(p))
                except Exception as e:
                    raise RuntimeError(f"Found bundled DLL at {p} but failed to load: {e}")

        # 2. Main fallback search directories (dist/, build/, cwd/)
        external_dlls = [
            repo_root / "dist" / arch / "tesseract_engine.dll",
            repo_root / "dist" / "tesseract_engine.dll",
            repo_root / "bin" / arch / "tesseract_engine.dll",
            repo_root / "build" / arch / "bin" / "tesseract_engine.dll",
            Path.cwd() / "dist" / arch / "tesseract_engine.dll",
            Path.cwd() / "dist" / "tesseract_engine.dll",
            Path.cwd() / "lib" / arch / "tesseract_engine.dll",
            Path.cwd() / "lib" / "tesseract_engine.dll",
            Path.cwd() / "bin" / arch / "tesseract_engine.dll",
            Path.cwd() / f"tesseract_engine_{arch}.dll",
            Path.cwd() / "tesseract_engine.dll",
        ]
        for p in external_dlls:
            if p.is_file():
                try:
                    return ctypes.CDLL(str(p))
                except Exception as e:
                    raise RuntimeError(f"Found DLL at {p} but failed to load: {e}")

        # 3. Fallback to Windows system library search path
        try:
            return ctypes.CDLL("tesseract_engine.dll")
        except Exception:
            all_searched = internal_dlls + external_dlls
            candidates_str = "\n".join(f"  - {p}" for p in all_searched)
            raise FileNotFoundError(
                f"Could not locate tesseract_engine.dll for architecture '{arch}'.\n"
                f"Searched locations (package lib checked first):\n{candidates_str}\n"
                f"Please ensure lib/{arch}/tesseract_engine.dll is bundled or run 'build.cmd' to compile the DLL."
            )

    def _bind_functions(self):
        d = self._dll

        d.tess_version.restype = c_char_p
        d.tess_version.argtypes = []

        d.tess_create.restype = c_void_p
        d.tess_create.argtypes = []

        d.tess_destroy.restype = None
        d.tess_destroy.argtypes = [c_void_p]

        d.tess_init.restype = c_int
        d.tess_init.argtypes = [c_void_p, c_char_p, c_char_p, c_int]

        d.tess_is_initialized.restype = c_int
        d.tess_is_initialized.argtypes = [c_void_p]

        d.tess_set_variable.restype = c_int
        d.tess_set_variable.argtypes = [c_void_p, c_char_p, c_char_p]

        d.tess_get_variable.restype = c_int
        d.tess_get_variable.argtypes = [c_void_p, c_char_p, c_char_p, c_int]

        d.tess_set_page_seg_mode.restype = None
        d.tess_set_page_seg_mode.argtypes = [c_void_p, c_int]

        d.tess_get_page_seg_mode.restype = c_int
        d.tess_get_page_seg_mode.argtypes = [c_void_p]

        d.tess_set_source_resolution.restype = None
        d.tess_set_source_resolution.argtypes = [c_void_p, c_int]

        if hasattr(d, "tess_get_source_resolution"):
            d.tess_get_source_resolution.restype = c_int
            d.tess_get_source_resolution.argtypes = [c_void_p]

        if hasattr(d, "tess_set_rectangle"):
            d.tess_set_rectangle.restype = None
            d.tess_set_rectangle.argtypes = [c_void_p, c_int, c_int, c_int, c_int]

        if hasattr(d, "tess_clear"):
            d.tess_clear.restype = None
            d.tess_clear.argtypes = [c_void_p]

        if hasattr(d, "tess_set_char_whitelist"):
            d.tess_set_char_whitelist.restype = c_int
            d.tess_set_char_whitelist.argtypes = [c_void_p, c_char_p]

        if hasattr(d, "tess_set_char_blacklist"):
            d.tess_set_char_blacklist.restype = c_int
            d.tess_set_char_blacklist.argtypes = [c_void_p, c_char_p]

        d.tess_set_image_file.restype = c_int
        d.tess_set_image_file.argtypes = [c_void_p, c_char_p]

        d.tess_set_image_bytes.restype = c_int
        d.tess_set_image_bytes.argtypes = [c_void_p, POINTER(ctypes.c_ubyte), c_size_t]

        d.tess_set_image_raw.restype = c_int
        d.tess_set_image_raw.argtypes = [c_void_p, POINTER(ctypes.c_ubyte), c_int, c_int, c_int, c_int]

        d.tess_recognize.restype = c_int
        d.tess_recognize.argtypes = [c_void_p]

        d.tess_get_utf8_text.restype = c_void_p
        d.tess_get_utf8_text.argtypes = [c_void_p]

        d.tess_get_hocr_text.restype = c_void_p
        d.tess_get_hocr_text.argtypes = [c_void_p, c_int]

        d.tess_get_tsv_text.restype = c_void_p
        d.tess_get_tsv_text.argtypes = [c_void_p, c_int]

        d.tess_get_box_text.restype = c_void_p
        d.tess_get_box_text.argtypes = [c_void_p, c_int]

        d.tess_get_unlv_text.restype = c_void_p
        d.tess_get_unlv_text.argtypes = [c_void_p]

        d.tess_get_json_text.restype = c_void_p
        d.tess_get_json_text.argtypes = [c_void_p]

        d.tess_get_mean_confidence.restype = c_int
        d.tess_get_mean_confidence.argtypes = [c_void_p]

        d.tess_free_text.restype = None
        d.tess_free_text.argtypes = [c_void_p]

        if hasattr(d, "tess_get_osd_text"):
            d.tess_get_osd_text.restype = c_void_p
            d.tess_get_osd_text.argtypes = [c_void_p, c_int]

        if hasattr(d, "tess_get_all_word_confidences"):
            d.tess_get_all_word_confidences.restype = POINTER(c_int)
            d.tess_get_all_word_confidences.argtypes = [c_void_p, POINTER(c_int)]

        if hasattr(d, "tess_free_confidences"):
            d.tess_free_confidences.restype = None
            d.tess_free_confidences.argtypes = [POINTER(c_int)]

        if hasattr(d, "tess_generate_searchable_pdf"):
            d.tess_generate_searchable_pdf.restype = c_int
            d.tess_generate_searchable_pdf.argtypes = [c_void_p, c_char_p, c_char_p]

        d.tess_detect_orientation_script.restype = c_int
        d.tess_detect_orientation_script.argtypes = [
            c_void_p, POINTER(c_int), POINTER(c_float), c_char_p, c_int, POINTER(c_float)
        ]

        d.tess_analyse_layout.restype = c_void_p
        d.tess_analyse_layout.argtypes = [c_void_p]

        d.tess_get_iterator.restype = c_void_p
        d.tess_get_iterator.argtypes = [c_void_p]

        d.tess_iterator_next.restype = c_int
        d.tess_iterator_next.argtypes = [c_void_p, c_int]

        d.tess_iterator_is_at_beginning_of.restype = c_int
        d.tess_iterator_is_at_beginning_of.argtypes = [c_void_p, c_int]

        d.tess_iterator_get_bounding_box.restype = c_int
        d.tess_iterator_get_bounding_box.argtypes = [
            c_void_p, c_int, POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int)
        ]

        d.tess_iterator_get_text.restype = c_void_p
        d.tess_iterator_get_text.argtypes = [c_void_p, c_int]

        d.tess_iterator_get_confidence.restype = c_float
        d.tess_iterator_get_confidence.argtypes = [c_void_p, c_int]

        d.tess_iterator_get_writing_direction.restype = c_int
        d.tess_iterator_get_writing_direction.argtypes = [c_void_p, POINTER(c_int)]

        d.tess_iterator_get_textline_order.restype = c_int
        d.tess_iterator_get_textline_order.argtypes = [c_void_p, POINTER(c_int)]

        d.tess_iterator_get_deskew_angle.restype = c_int
        d.tess_iterator_get_deskew_angle.argtypes = [c_void_p, POINTER(c_float)]

        d.tess_iterator_destroy.restype = None
        d.tess_iterator_destroy.argtypes = [c_void_p]

        d.tess_model_set_path.restype = c_int
        d.tess_model_set_path.argtypes = [c_char_p]

        d.tess_model_get_path.restype = c_int
        d.tess_model_get_path.argtypes = [c_char_p, c_int]

        d.tess_model_get_default_path.restype = c_int
        d.tess_model_get_default_path.argtypes = [c_char_p, c_int]

        d.tess_model_set_flavor.restype = None
        d.tess_model_set_flavor.argtypes = [c_int]

        d.tess_model_get_flavor.restype = c_int
        d.tess_model_get_flavor.argtypes = []

        d.tess_model_get_flavor_path.restype = c_int
        d.tess_model_get_flavor_path.argtypes = [c_int, c_char_p, c_int]

        d.tess_model_is_installed.restype = c_int
        d.tess_model_is_installed.argtypes = [c_char_p, c_int]

        d.tess_model_get_catalog_count.restype = c_int
        d.tess_model_get_catalog_count.argtypes = [c_int]

        d.tess_model_get_catalog_item.restype = c_int
        d.tess_model_get_catalog_item.argtypes = [c_int, c_int, POINTER(CModelInfo)]

        d.tess_model_download.restype = c_int
        d.tess_model_download.argtypes = [c_char_p, c_int, PROGRESS_CALLBACK_TYPE, c_void_p]

        d.tess_model_download_async.restype = c_int
        d.tess_model_download_async.argtypes = [c_char_p, c_int, PROGRESS_CALLBACK_TYPE, c_void_p, POINTER(c_void_p)]

        d.tess_model_cancel_download.restype = c_int
        d.tess_model_cancel_download.argtypes = [c_void_p]

        d.tess_model_get_installed_count.restype = c_int
        d.tess_model_get_installed_count.argtypes = []

        d.tess_model_get_installed_item.restype = c_int
        d.tess_model_get_installed_item.argtypes = [c_int, c_char_p, c_int]
