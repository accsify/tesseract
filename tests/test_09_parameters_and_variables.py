"""
Test 09: Engine Variables, PSM Modes, and Resolution Tuning.
============================================================
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
    PageSegMode,
    generate_sample_document,
)


class TestParametersAndVariables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_img = generate_sample_document(output_path=None)

    def test_page_seg_mode(self):
        """Verify setting and getting Page Segmentation Mode."""
        with TesseractEngine(language="eng") as engine:
            engine.set_page_seg_mode(PageSegMode.SINGLE_BLOCK)
            self.assertEqual(engine.get_page_seg_mode(), PageSegMode.SINGLE_BLOCK)

            engine.set_page_seg_mode(PageSegMode.AUTO)
            self.assertEqual(engine.get_page_seg_mode(), PageSegMode.AUTO)

    def test_set_and_get_variable(self):
        """Verify setting and retrieving internal Tesseract engine variables."""
        with TesseractEngine(language="eng") as engine:
            # Set whitelist
            res = engine.set_variable("tessedit_char_whitelist", "0123456789")
            self.assertTrue(res)

            val = engine.get_variable("tessedit_char_whitelist")
            self.assertEqual(val, "0123456789")

    def test_set_resolution(self):
        """Verify setting explicit DPI source resolution."""
        with TesseractEngine(language="eng") as engine:
            # Should not raise exception
            engine.set_resolution(300)


if __name__ == "__main__":
    unittest.main()
