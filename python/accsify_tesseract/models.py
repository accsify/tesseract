"""
Model Management, Catalog, and WinHTTP Downloader.
==================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

import json
import ctypes
from dataclasses import dataclass
from typing import List, Optional, Callable, Dict, Any
from pathlib import Path

from .types import ModelType
from .core import NativeLibrary, CModelInfo, PROGRESS_CALLBACK_TYPE
from .exceptions import ModelDownloadError, ModelNotFoundError


@dataclass
class ModelInfo:
    """Represents a traineddata language or script model."""
    name: str
    display_name: str
    model_type: ModelType
    file_size: int
    download_url: str
    is_installed: bool

    @property
    def file_size_mb(self) -> float:
        return self.file_size / (1024.0 * 1024.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "model_type": self.model_type.name,
            "file_size": self.file_size,
            "file_size_mb": round(self.file_size_mb, 2),
            "download_url": self.download_url,
            "is_installed": self.is_installed,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def __repr__(self) -> str:
        status = "Installed" if self.is_installed else "Not Installed"
        return f"<ModelInfo '{self.name}' ({self.display_name}) [{self.model_type.name}] - {self.file_size_mb:.1f}MB - {status}>"


class ModelManager:
    """Manages traineddata models on disk and provides catalog access and downloads."""

    def __init__(self, lib: Optional[NativeLibrary] = None):
        self._lib = lib or NativeLibrary.get()

    @classmethod
    def set_path(cls, path: str) -> None:
        """Set the active directory path for storing and loading .traineddata files."""
        lib = NativeLibrary.get()
        p = str(path).encode("utf-8") if path else None
        lib.dll.tess_model_set_path(p)

    @classmethod
    def get_path(cls) -> str:
        """Get the current active tessdata path."""
        lib = NativeLibrary.get()
        buf = ctypes.create_string_buffer(512)
        lib.dll.tess_model_get_path(buf, 512)
        return buf.value.decode("utf-8")

    @classmethod
    def get_default_path(cls) -> str:
        """Get the default tessdata path (./tessdata adjacent to the DLL)."""
        lib = NativeLibrary.get()
        buf = ctypes.create_string_buffer(512)
        lib.dll.tess_model_get_default_path(buf, 512)
        return buf.value.decode("utf-8")

    @classmethod
    def set_flavor(cls, flavor: ModelType) -> None:
        """
        Set active model flavor (ModelType.FAST, ModelType.BEST, etc.).
        Models are stored into and loaded from dedicated subdirectories (e.g. ./tessdata/best/).
        """
        lib = NativeLibrary.get()
        lib.dll.tess_model_set_flavor(int(flavor))

    @classmethod
    def get_flavor(cls) -> ModelType:
        """Get current active model flavor."""
        lib = NativeLibrary.get()
        return ModelType(lib.dll.tess_model_get_flavor())

    @classmethod
    def get_flavor_path(cls, flavor: ModelType) -> str:
        """Get folder path for a specific model flavor."""
        lib = NativeLibrary.get()
        buf = ctypes.create_string_buffer(512)
        lib.dll.tess_model_get_flavor_path(int(flavor), buf, 512)
        return buf.value.decode("utf-8")

    @classmethod
    def is_installed(cls, model_name: str, model_type: ModelType = ModelType.FAST) -> bool:
        """Check if a model exists in the active tessdata folder or flavor subfolder."""
        lib = NativeLibrary.get()
        return lib.dll.tess_model_is_installed(model_name.encode("utf-8"), int(model_type)) != 0

    @classmethod
    def list_catalog(cls, model_type: Optional[ModelType] = None) -> List[ModelInfo]:
        """Query all official models available in the catalog."""
        lib = NativeLibrary.get()
        filter_type = int(model_type) if model_type is not None else -1
        count = lib.dll.tess_model_get_catalog_count(filter_type)
        items = []
        c_info = CModelInfo()

        for i in range(count):
            if lib.dll.tess_model_get_catalog_item(filter_type, i, ctypes.byref(c_info)) == 0:
                items.append(ModelInfo(
                    name=c_info.name.decode("utf-8"),
                    display_name=c_info.display_name.decode("utf-8"),
                    model_type=ModelType(c_info.model_type),
                    file_size=c_info.file_size,
                    download_url=c_info.download_url.decode("utf-8"),
                    is_installed=bool(c_info.is_installed)
                ))
        return items

    @classmethod
    def list_installed(cls) -> List[str]:
        """List all .traineddata models currently present in the active tessdata directory."""
        lib = NativeLibrary.get()
        count = lib.dll.tess_model_get_installed_count()
        results = []
        buf = ctypes.create_string_buffer(128)
        for i in range(count):
            if lib.dll.tess_model_get_installed_item(i, buf, 128) == 0:
                results.append(buf.value.decode("utf-8"))
        return results

    @classmethod
    def download(
        cls,
        model_name: str,
        model_type: ModelType = ModelType.FAST,
        progress_callback: Optional[Callable[[str, int, int, int, float, str], bool]] = None
    ) -> bool:
        """
        Download a model synchronously using native Windows WinHTTP with live progress.
        
        Args:
            model_name: Model code (e.g. 'eng', 'fra', 'ara', 'script/Arabic').
            model_type: Repository type (FAST, BEST, STANDARD, SCRIPT).
            progress_callback: Optional callback(model_name, model_type, downloaded, total, pct, msg) -> bool.
                              Return False to abort/cancel download.
        """
        lib = NativeLibrary.get()
        if progress_callback:
            def _thunk(m_name, m_type, downloaded, total, pct, msg, u_data):
                cont = progress_callback(
                    m_name.decode("utf-8") if m_name else "",
                    m_type, downloaded, total, pct,
                    msg.decode("utf-8") if msg else ""
                )
                return 0 if cont else 1

            c_cb = PROGRESS_CALLBACK_TYPE(_thunk)
        else:
            c_cb = PROGRESS_CALLBACK_TYPE()

        res = lib.dll.tess_model_download(
            model_name.encode("utf-8"),
            int(model_type),
            c_cb,
            None
        )

        if res != 0:
            raise ModelDownloadError(f"Failed to download model '{model_name}' (error code: {res}).")
        return True

    @classmethod
    def download_many(
        cls,
        model_names: List[str],
        model_type: ModelType = ModelType.FAST,
        progress_callback: Optional[Callable[[str, int, int, int, float, str], bool]] = None
    ) -> bool:
        """Download multiple models sequentially."""
        for name in model_names:
            cls.download(name, model_type=model_type, progress_callback=progress_callback)
        return True
