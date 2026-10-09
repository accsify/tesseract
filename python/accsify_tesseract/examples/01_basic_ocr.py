"""
Example 01: Basic OCR and Automatic Model & Image Provisioning
==============================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.

Demonstrates:
  1. Automatic download of 'eng' model if not installed.
  2. Automatic generation of bilingual test image if missing.
  3. One-line helper 'image_to_string' and OOP 'TesseractEngine'.
  4. Mean confidence scoring and plain text retrieval.
"""

import sys
from pathlib import Path

# Fix Windows console UTF-8 output encoding for multilingual text
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure local package is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accsify_tesseract import (
    TesseractEngine,
    ModelManager,
    ModelType,
    image_to_string,
    generate_sample_document,
)


def main():
    print("=" * 70)
    print("Accsify Tesseract - Example 01: Basic OCR")
    print("=" * 70)
    print(f"[*] Engine Native Version : {TesseractEngine.version()}")
    print(f"[*] Active Tessdata Path  : {ModelManager.get_path()}")

    # 1. Ensure English model is available (auto-download if missing)
    if not ModelManager.is_installed("eng", ModelType.FAST):
        print("[*] 'eng' model not detected locally. Downloading via WinHTTP...")
        ModelManager.download("eng", ModelType.FAST)
        print("[+] 'eng' model successfully downloaded and verified!")
    else:
        print("[+] 'eng' model is ready.")

    # 2. Ensure test image exists (auto-generate bilingual image if missing)
    sample_img_path = Path(__file__).resolve().parent / "sample_bilingual_doc.png"
    if not sample_img_path.is_file():
        print("[*] Sample image not found. Auto-generating bilingual test image...")
        generate_sample_document(sample_img_path)
        print(f"[+] Generated test image at: {sample_img_path}")
    else:
        print(f"[+] Using existing test image: {sample_img_path.name}")

    # 3. Convenient One-Line OCR Helper
    print("\n--- Running One-Line image_to_string() ---")
    quick_text = image_to_string(sample_img_path, lang="eng")
    print(f"Quick extraction (first 150 chars):\n{quick_text[:150].strip()}...\n")

    # 4. Object-Oriented TesseractEngine with RAII Context Manager
    print("--- Running OOP TesseractEngine ---")
    with TesseractEngine(language="eng") as engine:
        engine.set_image(sample_img_path)
        engine.recognize()

        full_text = engine.get_text()
        confidence = engine.get_mean_confidence()

        print(f"[+] OCR Mean Confidence: {confidence}%")
        print("\n--- Recognized Text Output ---")
        print(full_text.strip())
        print("-" * 70)


if __name__ == "__main__":
    main()
