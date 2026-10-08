"""
Layout Analysis and Structured OCR Elements Hierarchy.
======================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.name,
            "text": self.text,
            "confidence": round(self.confidence, 2),
            "bbox": self.bbox.to_dict(),
            "writing_direction": self.writing_direction.name,
            "textline_order": self.textline_order.name,
            "deskew_angle": round(self.deskew_angle, 6),
        }

    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


@dataclass
class LayoutSymbol(LayoutElement):
    """An individual character or glyph."""
    pass


@dataclass
class LayoutWord(LayoutElement):
    """A recognized word with its symbols."""
    symbols: List[LayoutSymbol] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        if self.symbols:
            d["symbols"] = [s.to_dict() for s in self.symbols]
        return d


@dataclass
class LayoutLine(LayoutElement):
    """A recognized line of text with its words."""
    words: List[LayoutWord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        if self.words:
            d["words"] = [w.to_dict() for w in self.words]
        return d


@dataclass
class LayoutParagraph(LayoutElement):
    """A paragraph of text with its lines."""
    lines: List[LayoutLine] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        if self.lines:
            d["lines"] = [l.to_dict() for l in self.lines]
        return d


@dataclass
class LayoutBlock(LayoutElement):
    """A high-level layout block (column, heading, block, table)."""
    paragraphs: List[LayoutParagraph] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        if self.paragraphs:
            d["paragraphs"] = [p.to_dict() for p in self.paragraphs]
        return d


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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_elements": len(self.elements),
            "words_count": len(self.words),
            "lines_count": len(self.lines),
            "paragraphs_count": len(self.paragraphs),
            "blocks_count": len(self.blocks),
            "words": [w.to_dict() for w in self.words],
            "lines": [l.to_dict() for l in self.lines],
            "elements": [e.to_dict() for e in self.elements],
        }

    def to_json(self, indent: Optional[int] = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
