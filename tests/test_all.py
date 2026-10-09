"""
Root Test Runner for Accsify Tesseract.
=======================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

import sys
import unittest
from pathlib import Path

# Add python directory to sys.path
repo_root = Path(__file__).resolve().parent.parent
python_dir = repo_root / "python"
if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))


def suite():
    tests_dir = Path(__file__).resolve().parent
    loader = unittest.TestLoader()
    return loader.discover(start_dir=str(tests_dir), pattern="test_*.py")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
