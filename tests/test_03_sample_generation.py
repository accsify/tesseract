"""
Test 03: Synthetic Bilingual Image Generation.
==============================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

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
    generate_sample_document,
    generate_sample_receipt,
)


class TestSampleGeneration(unittest.TestCase):
    def test_generate_document_in_memory(self):
        """Verify document generator returns valid RGB PIL Image."""
        img = generate_sample_document(output_path=None, width=1000, height=600)
        self.assertIsInstance(img, Image.Image)
        self.assertEqual(img.size, (1000, 600))
        self.assertEqual(img.mode, "RGB")

    def test_generate_document_save_to_disk(self):
        """Verify document generator saves image file to disk properly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "test_doc.png"
            img = generate_sample_document(output_path=out_file)
            self.assertTrue(out_file.is_file())
            self.assertGreater(out_file.stat().st_size, 5000)

    def test_generate_receipt(self):
        """Verify receipt generator returns valid RGB PIL Image and writes to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "test_receipt.png"
            img = generate_sample_receipt(output_path=out_file, width=800, height=900)
            self.assertIsInstance(img, Image.Image)
            self.assertEqual(img.size, (800, 900))
            self.assertTrue(out_file.is_file())


if __name__ == "__main__":
    unittest.main()
