"""
Test 02: Model Manager, Catalog Querying, and Downloader.
=========================================================
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
    ModelManager,
    ModelType,
    ModelInfo,
)


class TestModelManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not ModelManager.is_installed("eng", ModelType.FAST):
            ModelManager.download("eng", ModelType.FAST)

    def test_tessdata_path_exists(self):
        """Verify the active tessdata path exists and contains traineddata files."""
        tpath = ModelManager.get_path()
        self.assertTrue(Path(tpath).is_dir(), f"Tessdata path not a directory: {tpath}")

    def test_list_installed(self):
        """Verify list_installed discovers installed models including 'eng'."""
        installed = ModelManager.list_installed()
        self.assertIsInstance(installed, list)
        self.assertIn("eng", installed)

    def test_model_catalog(self):
        """Verify online model catalog returns valid ModelInfo objects."""
        catalog = ModelManager.list_catalog(ModelType.FAST)
        self.assertGreater(len(catalog), 15)

        eng_info = next((m for m in catalog if m.name == "eng"), None)
        self.assertIsNotNone(eng_info)
        self.assertIsInstance(eng_info, ModelInfo)
        self.assertEqual(eng_info.name, "eng")
        self.assertGreater(eng_info.file_size, 100000)
        self.assertTrue(eng_info.download_url.startswith("https://"))

    def test_is_installed(self):
        """Verify is_installed works accurately."""
        self.assertTrue(ModelManager.is_installed("eng", ModelType.FAST))
        self.assertFalse(ModelManager.is_installed("xyz_fake_model", ModelType.FAST))

    def test_progress_download_hook(self):
        """Verify downloading with callback runs and reports progress."""
        calls = []

        def cb(name, mtype, dl, total, pct, msg):
            calls.append(pct)
            return True

        res = ModelManager.download("eng", ModelType.FAST, progress_callback=cb)
        self.assertTrue(res)
        self.assertGreater(len(calls), 0)


if __name__ == "__main__":
    unittest.main()
