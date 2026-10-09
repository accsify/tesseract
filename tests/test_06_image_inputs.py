"""
Test 06: Multi-Source Image Inputs and Memory Buffers.
======================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

import io
import unittest
import sys
import tempfile
from pathlib import Path
from PIL import Image

repo_root = Path(__file__).resolve().parent.parent
for cand in (repo_root / "python", repo_root):
    if str(cand) not in sys.path:
        sys.path.insert(0, str(cand))

from accsify_tesseract import (
    TesseractEngine,
    ImageLoadError,
    generate_sample_document,
)


class TestImageInputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pil_img = generate_sample_document(output_path=None, width=800, height=400)
        # Create memory PNG bytes
        bio = io.BytesIO()
        cls.pil_img.save(bio, format="PNG")
        cls.png_bytes = bio.getvalue()

    def test_pil_image_input(self):
        """Verify engine accepts PIL.Image.Image instance directly."""
        with TesseractEngine(language="eng") as engine:
            engine.set_image(self.pil_img)
            engine.recognize()
            txt = engine.get_text()
            self.assertIn("Accsify", txt)

    def test_raw_bytes_input(self):
        """Verify engine accepts compressed image bytes in memory."""
        with TesseractEngine(language="eng") as engine:
            engine.set_image(self.png_bytes)
            engine.recognize()
            txt = engine.get_text()
            self.assertIn("Accsify", txt)

    def test_file_path_input(self):
        """Verify engine accepts string and Path file paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "test_input.png"
            self.pil_img.save(str(tmp_path))

            with TesseractEngine(language="eng") as engine:
                # Test Path object
                engine.set_image(tmp_path)
                engine.recognize()
                txt_path = engine.get_text()

                # Test str
                engine.set_image(str(tmp_path))
                engine.recognize()
                txt_str = engine.get_text()

                self.assertEqual(txt_path, txt_str)

    def test_nonexistent_file_error(self):
        """Verify non-existent file path raises ImageLoadError."""
        with TesseractEngine(language="eng") as engine:
            with self.assertRaises(ImageLoadError):
                engine.set_image("C:/non_existent_folder_abc/missing_image_xyz.png")


if __name__ == "__main__":
    unittest.main()
