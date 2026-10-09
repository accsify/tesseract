"""
Test 05: Multilingual Bidirectional (BiDi) Arabic & English OCR.
=================================================================
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
    PageIteratorLevel,
    WritingDirection,
    generate_sample_document,
)


class TestMultilingualBidi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for m in ["eng", "ara"]:
            if not ModelManager.is_installed(m, ModelType.FAST):
                ModelManager.download(m, ModelType.FAST)

        cls.sample_img = generate_sample_document(output_path=None)

    def test_bilingual_recognition(self):
        """Verify bilingual OCR recognizes English and Arabic characters with high confidence."""
        with TesseractEngine(language="ara+eng") as engine:
            engine.set_image(self.sample_img)
            engine.recognize()

            text = engine.get_text()
            conf = engine.get_mean_confidence()

            self.assertGreater(conf, 75)
            # Verify English tokens
            self.assertIn("Accsify", text)
            self.assertIn("Tesseract", text)
            # Verify Arabic tokens (e.g. العربية or أكسيفاي or محرك)
            has_arabic = any(("\u0600" <= ch <= "\u06FF") for ch in text)
            self.assertTrue(has_arabic, "Recognized text did not contain Arabic Unicode characters")

    def test_bidi_writing_direction_detection(self):
        """Verify layout analysis identifies word writing directions."""
        with TesseractEngine(language="ara+eng") as engine:
            engine.set_image(self.sample_img)
            layout = engine.analyse_layout(PageIteratorLevel.WORD)

            self.assertGreater(len(layout.words), 20)
            directions = {w.writing_direction for w in layout.words}
            # Should have detected direction
            self.assertTrue(len(directions) > 0)


if __name__ == "__main__":
    unittest.main()
