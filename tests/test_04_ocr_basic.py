"""
Test 04: English OCR Recognition and One-Line Helpers.
======================================================
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
    ModelManager,
    ModelType,
    image_to_string,
    image_to_json,
    image_to_dict,
    generate_sample_document,
)


class TestBasicOcr(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not ModelManager.is_installed("eng", ModelType.FAST):
            ModelManager.download("eng", ModelType.FAST)

        cls.sample_img = generate_sample_document(output_path=None)

    def test_engine_recognize_text(self):
        """Verify engine recognizes English text with valid confidence."""
        with TesseractEngine(language="eng") as engine:
            engine.set_image(self.sample_img)
            engine.recognize()

            text = engine.get_text()
            conf = engine.get_mean_confidence()

            self.assertIn("Accsify", text)
            self.assertIn("Tesseract", text)
            self.assertGreater(conf, 50)

    def test_image_to_string_helper(self):
        """Verify one-line image_to_string helper returns valid text."""
        txt = image_to_string(self.sample_img, lang="eng")
        self.assertIsInstance(txt, str)
        self.assertIn("Accsify", txt)

    def test_image_to_json_helper(self):
        """Verify one-line image_to_json helper returns valid JSON string."""
        raw_json = image_to_json(self.sample_img, lang="eng")
        self.assertIsInstance(raw_json, str)
        self.assertTrue(raw_json.strip().startswith("{"))
        self.assertIn('"mean_confidence"', raw_json)

    def test_image_to_dict_helper(self):
        """Verify one-line image_to_dict helper returns parsed dict."""
        d = image_to_dict(self.sample_img, lang="eng")
        self.assertIsInstance(d, dict)
        self.assertIn("mean_confidence", d)
        self.assertIn("words", d)


if __name__ == "__main__":
    unittest.main()
