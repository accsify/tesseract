"""
Example 07: Native CLI Executable Integration from Python
=========================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.

Demonstrates:
  1. Locating the bundled 'tesseract_cli.exe' binary via get_native_cli_path().
  2. Executing CLI commands with subprocess:
     - Version and compilation info (version)
     - List installed languages (models installed)
     - Full OCR extraction to stdout (ocr <image> -l eng).
"""

import sys
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accsify_tesseract import (
    get_native_cli_path,
    generate_sample_document,
)


def run_cli(*args):
    cli = get_native_cli_path()
    cmd = [cli] + list(args)
    print(f"\n[>] Executing: {' '.join(str(c) for c in cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return res


def main():
    print("=" * 75)
    print("Accsify Tesseract - Example 07: Native CLI Integration")
    print("=" * 75)

    cli_path = get_native_cli_path()
    print(f"[*] Native CLI Binary : {cli_path}")
    print(f"[*] Binary Exists     : {Path(cli_path).exists()}")

    # 1. Check version
    res = run_cli("version")
    print("--- CLI Version Output ---")
    print(res.stdout.strip())

    # 2. List installed languages
    res = run_cli("models", "installed")
    print("--- CLI Installed Languages ---")
    print(res.stdout.strip())

    # 3. Perform OCR via CLI on generated test image
    img_path = Path(__file__).resolve().parent / "sample_bilingual_doc.png"
    if not img_path.is_file():
        generate_sample_document(img_path)

    res = run_cli("ocr", str(img_path), "-l", "eng")
    print("--- CLI OCR Output ---")
    print(res.stdout[:400].strip())
    print("...")


if __name__ == "__main__":
    main()
