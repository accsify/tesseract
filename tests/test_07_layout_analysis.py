"""
Test 07: Page Layout Analysis and Bounding Boxes.
=================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

import unittest
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
for cand in (repo_root / "python", repo_root):
    if str(cand) not in sys.path:
        sys.path.insert(0, str(cand))

from accsify_tesseract import (
    TesseractEngine,
    PageIteratorLevel,
    generate_sample_document,
)


class TestLayoutAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_img = generate_sample_document(output_path=None)

    def test_word_layout_elements(self):
        """Verify layout analysis returns word elements with valid coordinates."""
        with TesseractEngine(language="eng") as engine:
            engine.set_image(self.sample_img)
            layout = engine.analyse_layout(PageIteratorLevel.WORD)

            self.assertGreater(len(layout.words), 10)
            for w in layout.words:
                self.assertIsNotNone(w.text)
                self.assertGreaterEqual(w.confidence, 0.0)
                self.assertLessEqual(w.confidence, 100.0)
                b = w.bbox
                self.assertLess(b.left, b.right)
                self.assertLess(b.top, b.bottom)
                self.assertGreaterEqual(b.left, 0)
                self.assertGreaterEqual(b.top, 0)

    def test_layout_to_dict(self):
        """Verify layout object converts to Python dictionary and JSON."""
        with TesseractEngine(language="eng") as engine:
            engine.set_image(self.sample_img)
            layout = engine.analyse_layout(PageIteratorLevel.WORD)
            d = layout.to_dict()

            self.assertIsInstance(d, dict)
            self.assertIn("words", d)
            self.assertGreater(len(d["words"]), 0)


if __name__ == "__main__":
    unittest.main()
