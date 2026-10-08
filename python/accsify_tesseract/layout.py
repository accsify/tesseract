"""
Layout Analysis and Structured OCR Elements Hierarchy.
======================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .types import (
    PageIteratorLevel, WritingDirection, TextlineOrder, BoundingBox
)


@dataclass
class LayoutElement:
    """A generic layout element (block, paragraph, line, word, symbol)."""
    level: PageIteratorLevel
    text: str
    confidence: float
    bbox: BoundingBox
    writing_direction: WritingDirection
    textline_order: TextlineOrder
    deskew_angle: float

    @property
    def is_ltr(self) -> bool:
        return self.writing_direction == WritingDirection.LEFT_TO_RIGHT

    @property
    def is_rtl(self) -> bool:
        return self.writing_direction == WritingDirection.RIGHT_TO_LEFT

    @property
    def is_vertical(self) -> bool:
        return self.writing_direction == WritingDirection.TOP_TO_BOTTOM


@dataclass
class LayoutSymbol(LayoutElement):
    """An individual character or glyph."""
    pass


@dataclass
class LayoutWord(LayoutElement):
    """A recognized word with its symbols."""
    symbols: List[LayoutSymbol] = field(default_factory=list)


@dataclass
class LayoutLine(LayoutElement):
    """A recognized line of text with its words."""
    words: List[LayoutWord] = field(default_factory=list)


@dataclass
class LayoutParagraph(LayoutElement):
    """A paragraph of text with its lines."""
    lines: List[LayoutLine] = field(default_factory=list)


@dataclass
class LayoutBlock(LayoutElement):
    """A high-level layout block (column, heading, block, table)."""
    paragraphs: List[LayoutParagraph] = field(default_factory=list)


@dataclass
class PageLayout:
    """Complete layout analysis of an image."""
    elements: List[LayoutElement] = field(default_factory=list)

    @property
    def words(self) -> List[LayoutElement]:
        return [el for el in self.elements if el.level == PageIteratorLevel.WORD]

    @property
    def lines(self) -> List[LayoutElement]:
        return [el for el in self.elements if el.level == PageIteratorLevel.TEXTLINE]

    @property
    def paragraphs(self) -> List[LayoutElement]:
        return [el for el in self.elements if el.level == PageIteratorLevel.PARA]

    @property
    def blocks(self) -> List[LayoutElement]:
        return [el for el in self.elements if el.level == PageIteratorLevel.BLOCK]

    @property
    def symbols(self) -> List[LayoutElement]:
        return [el for el in self.elements if el.level == PageIteratorLevel.SYMBOL]
