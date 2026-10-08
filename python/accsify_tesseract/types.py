"""
Types and Enums for Accsify Tesseract OCR Engine.
=================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Optional


class PageSegMode(IntEnum):
    """Page Segmentation Modes (PSM) supported by Tesseract."""
    OSD_ONLY = 0                #: Orientation and script detection only.
    AUTO_OSD = 1                #: Automatic page segmentation with orientation and script detection.
    AUTO_ONLY = 2               #: Automatic page segmentation, but no OSD or OCR.
    AUTO = 3                    #: Fully automatic page segmentation, but no OSD. (Default)
    SINGLE_COLUMN = 4           #: Assume a single column of text of variable sizes.
    SINGLE_BLOCK_VERT_TEXT = 5  #: Assume a single uniform block of vertically aligned text.
    SINGLE_BLOCK = 6            #: Assume a single uniform block of text.
    SINGLE_LINE = 7             #: Treat the image as a single text line.
    SINGLE_WORD = 8             #: Treat the image as a single word.
    CIRCLE_WORD = 9             #: Treat the image as a single word in a circle.
    SINGLE_CHAR = 10            #: Treat the image as a single character.
    SPARSE_TEXT = 11            #: Find as much text as possible in no particular order.
    SPARSE_TEXT_OSD = 12        #: Sparse text with orientation and script detection.
    RAW_LINE = 13               #: Treat the image as a single text line, bypassing hacks.


class OcrEngineMode(IntEnum):
    """OCR Engine Modes (OEM)."""
    TESSERACT_ONLY = 0          #: Legacy Tesseract engine only.
    LSTM_ONLY = 1               #: Neural nets LSTM engine only.
    TESSERACT_LSTM_COMBINED = 2 #: Legacy + LSTM combined.
    DEFAULT = 3                 #: Default, based on what is available in the model.


class PageIteratorLevel(IntEnum):
    """Hierarchy levels for page layout analysis."""
    BLOCK = 0                   #: Block of text, table, or graphic.
    PARA = 1                    #: Paragraph within a block.
    TEXTLINE = 2                #: Text line within a paragraph.
    WORD = 3                    #: Word within a text line.
    SYMBOL = 4                  #: Individual symbol/glyph within a word.


class WritingDirection(IntEnum):
    """Writing direction of text."""
    LEFT_TO_RIGHT = 0           #: Left-to-right (e.g. Latin, Cyrillic, Greek).
    RIGHT_TO_LEFT = 1           #: Right-to-left (e.g. Arabic, Hebrew).
    TOP_TO_BOTTOM = 2           #: Top-to-bottom (e.g. traditional East Asian).


class TextlineOrder(IntEnum):
    """Reading order of text lines."""
    LEFT_TO_RIGHT = 0           #: Left-to-right.
    RIGHT_TO_LEFT = 1           #: Right-to-left.
    TOP_TO_BOTTOM = 2           #: Top-to-bottom.


class ModelType(IntEnum):
    """Traineddata repository models."""
    FAST = 0                    #: tessdata_fast (~1-5 MB compact models, high performance).
    BEST = 1                    #: tessdata_best (~15-40 MB high-precision models).
    STANDARD = 2                #: tessdata (standard compatible release models).
    SCRIPT = 3                  #: script models (Arabic, Cyrillic, Latin, Han, etc.).


@dataclass(frozen=True)
class BoundingBox:
    """Bounding box coordinates on an image."""
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return max(0, self.right - self.left)

    @property
    def height(self) -> int:
        return max(0, self.bottom - self.top)

    def as_tuple(self) -> tuple:
        return (self.left, self.top, self.right, self.bottom)
