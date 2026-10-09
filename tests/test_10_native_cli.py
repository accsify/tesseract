"""
Test 10: Bundled Standalone CLI Executable Verification.
========================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

import unittest
import subprocess
import sys
import tempfile
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
for cand in (repo_root / "python", repo_root):
    if str(cand) not in sys.path:
        sys.path.insert(0, str(cand))

from accsify_tesseract import (
    get_native_cli_path,
    generate_sample_document,
)


class TestNativeCli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cli_path = get_native_cli_path()

    def test_cli_exists(self):
        """Verify the CLI executable path points to a valid on-disk binary."""
        self.assertIsNotNone(self.cli_path)
        self.assertTrue(Path(self.cli_path).is_file())

    def test_cli_version(self):
        """Verify running 'tesseract_cli version' returns expected company and version banner."""
        res = subprocess.run([self.cli_path, "version"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Accsify Tesseract OCR CLI Tool", res.stdout)
        self.assertIn("5.5.0", res.stdout)

    def test_cli_models_installed(self):
        """Verify running 'tesseract_cli models installed' lists installed models."""
        res = subprocess.run([self.cli_path, "models", "installed"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Installed Models in", res.stdout)
        self.assertIn("eng", res.stdout)

    def test_cli_ocr_execution(self):
        """Verify running 'tesseract_cli ocr <img_path> -l eng' extracts text."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sample_img = Path(tmpdir) / "test_cli.png"
            generate_sample_document(sample_img)

            res = subprocess.run(
                [self.cli_path, "ocr", str(sample_img), "-l", "eng"],
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            self.assertEqual(res.returncode, 0)
            self.assertIn("Accsify Tesseract Native OCR Engine", res.stdout)


if __name__ == "__main__":
    unittest.main()
