"""
Accsify Tesseract Examples & Interactive Tutorial Suite.
========================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.

Provides bundled runnable tutorials, bilingual test assets, and scaffolding utilities.
"""

import sys
import shutil
from pathlib import Path
from typing import List


def get_examples_dir() -> Path:
    """Return the absolute path to the bundled examples directory."""
    return Path(__file__).resolve().parent


def list_examples() -> List[str]:
    """Return list of available example script names."""
    edir = get_examples_dir()
    return sorted([f.name for f in edir.glob("*.py") if f.name != "__init__.py"])


def copy_examples(destination: str = ".") -> List[Path]:
    """
    Copy all bundled tutorial scripts and sample test images into a destination folder.
    
    Args:
        destination: Target folder path (default: current working directory).
        
    Returns:
        List of Path objects for copied files.
    """
    dest_path = Path(destination).resolve()
    dest_path.mkdir(parents=True, exist_ok=True)
    src_dir = get_examples_dir()
    copied = []

    for item in src_dir.iterdir():
        if item.name == "__init__.py" or item.name == "__pycache__":
            continue
        target_file = dest_path / item.name
        if item.is_file():
            shutil.copy2(item, target_file)
            copied.append(target_file)

    return copied


def run_demo() -> int:
    """Run the built-in bilingual Arabic & English OCR demonstration."""
    from . import __path__
    demo_script = get_examples_dir() / "02_multilingual_bidi_ocr.py"
    if not demo_script.is_file():
        demo_script = get_examples_dir() / "01_basic_ocr.py"

    import runpy
    runpy.run_path(str(demo_script), run_name="__main__")
    return 0


__all__ = [
    "get_examples_dir",
    "list_examples",
    "copy_examples",
    "run_demo",
]
