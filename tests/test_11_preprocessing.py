"""
Test 11: Image Preprocessing and DPI Normalization Suite.
=========================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

import sys
import unittest
from pathlib import Path
from PIL import Image

repo_root = Path(__file__).resolve().parent.parent
python_dir = repo_root / "python"
if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))

from accsify_tesseract.preprocessing import extract_image_dpi, enhance_for_ocr


class TestPreprocessing(unittest.TestCase):
    def test_dpi_extraction(self):
        img = Image.new("RGB", (100, 100), color="white")
        self.assertIsNone(extract_image_dpi(img))

        img.info["dpi"] = (300, 300)
        self.assertEqual(extract_image_dpi(img), 300)

        img.info["dpi"] = (150.4, 150.4)
        self.assertEqual(extract_image_dpi(img), 150)

    def test_enhance_image(self):
        img = Image.new("RGB", (200, 200), color="gray")
        img.info["dpi"] = (300, 300)
        enhanced = enhance_for_ocr(img, auto_contrast=True, sharpen=True, binarize=False)
        self.assertIsNotNone(enhanced)
        self.assertEqual(enhanced.size, (200, 200))
        self.assertEqual(enhanced.info.get("dpi"), (300, 300))

    def test_binarization_mode(self):
        img = Image.new("RGB", (50, 50), color=(100, 100, 100))
        bin_img = enhance_for_ocr(img, binarize=True)
        self.assertIsNotNone(bin_img)
        self.assertEqual(bin_img.size, (50, 50))


if __name__ == "__main__":
    unittest.main()
