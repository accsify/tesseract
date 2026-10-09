"""
Unit tests for Top-Level Helper Functions in accsify_tesseract.
===============================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

import unittest
import sys
import re
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
for cand in (repo_root / "python", repo_root):
    if str(cand) not in sys.path:
        sys.path.insert(0, str(cand))

from accsify_tesseract import (
    image_to_string,
    image_to_osd,
    image_to_boxes,
    image_to_data,
    image_to_hocr,
    get_languages,
    get_tesseract_version,
    generate_sample_document,
)


class TestTopLevelHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.img = generate_sample_document()

    def test_image_to_string_with_config(self):
        txt = image_to_string(self.img, lang="eng", config="--psm 3")
        self.assertIn("Accsify", txt)

    def test_image_to_osd_format(self):
        osd_out = image_to_osd(self.img)
        self.assertRegex(osd_out, r"Orientation in degrees:\s*\d+")
        self.assertRegex(osd_out, r"Rotate:\s*\d+")
        self.assertRegex(osd_out, r"Script:\s*\w+")

    def test_image_to_boxes(self):
        boxes = image_to_boxes(self.img, lang="eng")
        self.assertIsInstance(boxes, str)
        self.assertGreater(len(boxes), 10)

    def test_image_to_data(self):
        data = image_to_data(self.img, lang="eng")
        self.assertIn("level\tpage_num\tblock_num", data)

    def test_image_to_hocr(self):
        hocr = image_to_hocr(self.img, lang="eng")
        self.assertIn("ocr_page", hocr)

    def test_get_languages(self):
        langs = get_languages()
        self.assertIn("eng", langs)

    def test_get_tesseract_version(self):
        ver = get_tesseract_version()
        self.assertTrue(len(ver) > 0)
        self.assertTrue(ver.startswith("5."))


if __name__ == "__main__":
    unittest.main()
