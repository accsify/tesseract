"""
Test 01: Engine Lifecycle, Versioning, and Resource Safety.
===========================================================
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
    EngineInitError,
    get_native_dll_path,
    get_native_cli_path,
)


class TestEngineLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not ModelManager.is_installed("eng", ModelType.FAST):
            ModelManager.download("eng", ModelType.FAST)

    def test_version_string(self):
        """Verify native engine version is non-empty and starts with 5."""
        v = TesseractEngine.version()
        self.assertIsInstance(v, str)
        self.assertTrue(v.startswith("5."), f"Expected version 5.x, got '{v}'")

    def test_binary_paths(self):
        """Verify native DLL and CLI binary paths are discovered and exist."""
        dll_path = get_native_dll_path()
        self.assertIsNotNone(dll_path)
        self.assertTrue(Path(dll_path).is_file(), f"DLL not found at: {dll_path}")

        cli_path = get_native_cli_path()
        self.assertIsNotNone(cli_path)
        self.assertTrue(Path(cli_path).is_file(), f"CLI not found at: {cli_path}")

    def test_context_manager_raii(self):
        """Verify engine RAII context manager cleanly allocates and releases."""
        with TesseractEngine(language="eng") as engine:
            self.assertTrue(engine.is_valid)
        self.assertFalse(engine.is_valid)

    def test_manual_close_and_double_close(self):
        """Verify manual close() works and double closing does not crash."""
        engine = TesseractEngine(language="eng")
        self.assertTrue(engine.is_valid)
        engine.close()
        self.assertFalse(engine.is_valid)
        # Calling close again should be safe no-op
        engine.close()

    def test_invalid_language_error(self):
        """Verify that an invalid/non-existent language raises EngineInitError."""
        with self.assertRaises(EngineInitError):
            TesseractEngine(language="non_existent_fake_language_12345")


if __name__ == "__main__":
    unittest.main()
