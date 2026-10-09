"""
Unit tests for drop-in pytesseract compatibility layer.
Replicates exact calling patterns from external accsisuite codebase.
=====================================================================
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

from PIL import Image
from accsify_tesseract import compat as pytesseract, generate_sample_document


class TestPytesseractCompatibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_img = generate_sample_document()

    def test_tesseract_cmd_property(self):
        # accsisuite sets pytesseract.pytesseract.tesseract_cmd = path
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        self.assertEqual(pytesseract.pytesseract.tesseract_cmd, r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        # Also directly on module
        pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        self.assertEqual(pytesseract.tesseract_cmd, r"C:\Program Files\Tesseract-OCR\tesseract.exe")

    def test_accsisuite_osd_pattern(self):
        # Exact code from accsisuite tesseract_utils.py line 326-330
        osd_data = pytesseract.image_to_osd(self.sample_img, config='--psm 0')
        rot_match = re.search(r'Rotate:\s*(\d+)', osd_data)
        self.assertIsNotNone(rot_match)
        rot_angle = int(rot_match.group(1))
        self.assertEqual(rot_angle, 0)

    def test_accsisuite_string_psm11(self):
        # Exact code from accsisuite tesseract_utils.py line 452
        text = pytesseract.image_to_string(self.sample_img, config='--psm 11')
        self.assertGreater(len(text), 10)
        self.assertIn("Accsify", text)

    def test_accsisuite_get_languages(self):
        # Exact code from accsisuite tesseract_utils.py line 71
        lngs = pytesseract.get_languages(config='')
        self.assertIn('eng', lngs)

    def test_accsisuite_version(self):
        ver = pytesseract.get_tesseract_version()
        self.assertTrue(len(ver) > 0)

    def test_accsisuite_boxes_and_data(self):
        boxes = pytesseract.image_to_boxes(self.sample_img)
        self.assertIsInstance(boxes, str)
        self.assertGreater(len(boxes), 10)

        data = pytesseract.image_to_data(self.sample_img, output_type=pytesseract.Output.STRING)
        self.assertIn("level\tpage_num", data)

        data_dict = pytesseract.image_to_data(self.sample_img, output_type=pytesseract.Output.DICT)
        self.assertIn("text", data_dict)
        self.assertIn("conf", data_dict)


if __name__ == "__main__":
    unittest.main()
