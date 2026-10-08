"""
Low-Level Layout and Result Iterator OOP Wrapper.
================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

import ctypes
from ctypes import c_int, c_float
from typing import Optional

from .core import NativeLibrary
from .types import (
    PageIteratorLevel, WritingDirection, TextlineOrder, BoundingBox
)


class TesseractIterator:
    """Cursor iterator over page layout components (blocks, paragraphs, lines, words, symbols)."""

    def __init__(self, handle: ctypes.c_void_p, lib: Optional[NativeLibrary] = None):
        self._handle = handle
        self._lib = lib or NativeLibrary.get()

    def __del__(self):
        self.close()

    def close(self):
        if self._handle:
            self._lib.dll.tess_iterator_destroy(self._handle)
            self._handle = None

    @property
    def is_valid(self) -> bool:
        return self._handle is not None

    def next(self, level: PageIteratorLevel = PageIteratorLevel.WORD) -> bool:
        """Advance iterator to next element at given level. Returns False at end of page."""
        if not self._handle:
            return False
        return self._lib.dll.tess_iterator_next(self._handle, int(level)) != 0

    def is_at_beginning_of(self, level: PageIteratorLevel) -> bool:
        """Check if current position marks the beginning of an element at given level."""
        if not self._handle:
            return False
        return self._lib.dll.tess_iterator_is_at_beginning_of(self._handle, int(level)) != 0

    def get_bounding_box(self, level: PageIteratorLevel = PageIteratorLevel.WORD) -> Optional[BoundingBox]:
        """Get bounding box coordinates for current element."""
        if not self._handle:
            return None
        l, t, r, b = c_int(), c_int(), c_int(), c_int()
        res = self._lib.dll.tess_iterator_get_bounding_box(
            self._handle, int(level),
            ctypes.byref(l), ctypes.byref(t), ctypes.byref(r), ctypes.byref(b)
        )
        if res == 0:
            return None
        return BoundingBox(l.value, t.value, r.value, b.value)

    def get_text(self, level: PageIteratorLevel = PageIteratorLevel.WORD) -> str:
        """Get recognized text for current element."""
        if not self._handle:
            return ""
        ptr = self._lib.dll.tess_iterator_get_text(self._handle, int(level))
        if not ptr:
            return ""
        try:
            return ctypes.string_at(ptr).decode("utf-8", errors="replace")
        finally:
            self._lib.dll.tess_free_text(ptr)

    def get_confidence(self, level: PageIteratorLevel = PageIteratorLevel.WORD) -> float:
        """Get recognition confidence (0.0 to 100.0) for current element."""
        if not self._handle:
            return 0.0
        return float(self._lib.dll.tess_iterator_get_confidence(self._handle, int(level)))

    def get_writing_direction(self) -> WritingDirection:
        """Get writing direction of current block/line (Left-to-Right, Right-to-Left, Top-to-Bottom)."""
        if not self._handle:
            return WritingDirection.LEFT_TO_RIGHT
        wdir = c_int()
        self._lib.dll.tess_iterator_get_writing_direction(self._handle, ctypes.byref(wdir))
        return WritingDirection(wdir.value)

    def get_textline_order(self) -> TextlineOrder:
        """Get reading order of text lines in the block."""
        if not self._handle:
            return TextlineOrder.LEFT_TO_RIGHT
        order = c_int()
        self._lib.dll.tess_iterator_get_textline_order(self._handle, ctypes.byref(order))
        return TextlineOrder(order.value)

    def get_deskew_angle(self) -> float:
        """Get deskew angle in radians (-pi/4 <= angle <= pi/4)."""
        if not self._handle:
            return 0.0
        angle = c_float()
        self._lib.dll.tess_iterator_get_deskew_angle(self._handle, ctypes.byref(angle))
        return float(angle.value)
