"""
Unit tests for OSD detection auto-download, apply_config, and DPI normalization.
================================================================================
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

from PIL import Image
from accsify_tesseract import (
    TesseractEngine,
    PageSegMode,
    generate_sample_document,
)


class TestOsdAndConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.img = generate_sample_document()

    def test_apply_config_psm_and_variables(self):
        with TesseractEngine(language="eng") as engine:
            engine.apply_config("--psm 11 -c tessedit_char_whitelist=0123456789")
            self.assertEqual(engine.get_page_seg_mode(), PageSegMode.SPARSE_TEXT)
            self.assertEqual(engine.get_variable("tessedit_char_whitelist"), "0123456789")

    def test_dpi_normalization(self):
        # Create image without DPI
        img = Image.new("RGB", (300, 100), color="white")
        with TesseractEngine(language="eng") as engine:
            engine.set_image(img)
            # engine_api.cpp auto-normalizes resolution < 70 to 300
            res = engine.get_resolution()
            self.assertGreaterEqual(res, 70)

    def test_set_rectangle_roi(self):
        with TesseractEngine(language="eng") as engine:
            engine.set_image(self.img)
            engine.set_rectangle(10, 10, 200, 50)
            txt = engine.get_text()
            self.assertIsInstance(txt, str)
            engine.clear()

    def test_char_whitelist_and_blacklist(self):
        with TesseractEngine(language="eng") as engine:
            engine.set_char_whitelist("0123456789")
            self.assertEqual(engine.get_variable("tessedit_char_whitelist"), "0123456789")
            engine.set_char_blacklist("xyz")
            self.assertEqual(engine.get_variable("tessedit_char_blacklist"), "xyz")

    def test_osd_detection(self):
        with TesseractEngine(language="osd", auto_download=True) as engine:
            engine.set_page_seg_mode(PageSegMode.OSD_ONLY)
            engine.set_image(self.img)
            osd = engine.detect_orientation_and_script()
            self.assertEqual(osd.orientation_deg, 0)
            self.assertTrue(osd.is_upright)


if __name__ == "__main__":
    unittest.main()
