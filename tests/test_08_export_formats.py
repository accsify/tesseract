"""
Test 08: Multi-Format Document Export Artifacts.
================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

import unittest
import json
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
for cand in (repo_root / "python", repo_root):
    if str(cand) not in sys.path:
        sys.path.insert(0, str(cand))

from accsify_tesseract import (
    TesseractEngine,
    generate_sample_document,
)


class TestExportFormats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_img = generate_sample_document(output_path=None)

    def test_hocr_export(self):
        """Verify hOCR output returns valid HTML with OCR markup."""
        with TesseractEngine(language="eng") as engine:
            engine.set_image(self.sample_img)
            engine.recognize()
            hocr = engine.get_hocr()

            self.assertIsInstance(hocr, str)
            self.assertIn("ocr_page", hocr)
            self.assertIn("bbox", hocr)

    def test_tsv_export(self):
        """Verify TSV output returns valid tab-separated table."""
        with TesseractEngine(language="eng") as engine:
            engine.set_image(self.sample_img)
            engine.recognize()
            tsv = engine.get_tsv()

            lines = tsv.strip().split("\n")
            self.assertGreater(len(lines), 1)
            # Native Tesseract TSV rows contain 12 tab-separated columns
            cols = lines[0].split("\t")
            self.assertGreaterEqual(len(cols), 11)

    def test_box_export(self):
        """Verify Box format returns character lines with coordinate columns."""
        with TesseractEngine(language="eng") as engine:
            engine.set_image(self.sample_img)
            engine.recognize()
            box = engine.get_box()

            lines = box.strip().split("\n")
            self.assertGreater(len(lines), 5)
            # Each box line is formatted: char left bottom right top page
            parts = lines[0].split(" ")
            self.assertGreaterEqual(len(parts), 5)

    def test_json_and_dict_export(self):
        """Verify JSON output produces valid, parseable JSON with coordinates."""
        with TesseractEngine(language="eng") as engine:
            engine.set_image(self.sample_img)
            engine.recognize()

            json_str = engine.get_json()
            data = json.loads(json_str)

            self.assertIn("mean_confidence", data)
            self.assertIn("words", data)
            self.assertGreater(len(data["words"]), 0)


if __name__ == "__main__":
    unittest.main()
