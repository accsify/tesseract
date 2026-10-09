"""
Example 02: Multilingual Bidirectional (BiDi) OCR (Arabic & English)
=====================================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.

Demonstrates:
  1. Multilingual Arabic (RTL) and English (LTR) OCR using 'ara+eng'.
  2. Automatic verification and WinHTTP download of both models.
  3. Automatic synthetic generation of a dual-script test document.
  4. Per-word writing direction analysis (RIGHT_TO_LEFT vs LEFT_TO_RIGHT).
  5. Clean UTF-8 multilingual console reporting.
"""

import sys
from pathlib import Path

# Enable UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accsify_tesseract import (
    TesseractEngine,
    ModelManager,
    ModelType,
    PageIteratorLevel,
    WritingDirection,
    generate_sample_document,
)


def main():
    print("=" * 75)
    print("Accsify Tesseract - Example 02: Multilingual Arabic & English (BiDi)")
    print("=" * 75)

    # 1. Ensure both 'ara' and 'eng' models are downloaded
    required_models = ["eng", "ara"]
    for m in required_models:
        if not ModelManager.is_installed(m, ModelType.FAST):
            print(f"[*] Downloading required language model '{m}'...")
            ModelManager.download(m, ModelType.FAST)
            print(f"[+] '{m}' model installed successfully.")
        else:
            print(f"[+] Model '{m}' is verified.")

    # 2. Ensure test image exists (auto-generate bilingual document)
    sample_img = Path(__file__).resolve().parent / "sample_bilingual_doc.png"
    if not sample_img.is_file():
        print("[*] Generating bilingual RTL/LTR document...")
        generate_sample_document(sample_img)
        print(f"[+] Saved sample image: {sample_img}")

    # 3. Initialize Engine with combined models: 'ara+eng'
    print("\n[*] Initializing TesseractEngine(language='ara+eng')...")
    with TesseractEngine(language="ara+eng") as engine:
        engine.set_image(sample_img)
        engine.recognize()

        mean_conf = engine.get_mean_confidence()
        full_text = engine.get_text()

        print(f"[+] Mean Document Confidence: {mean_conf}%")
        print("\n" + "=" * 30 + " Recognized Text " + "=" * 30)
        print(full_text.strip())
        print("=" * 77)

        # 4. Word-level Direction and Confidence Inspection
        print("\n[*] Inspecting Word-level Script Directions:")
        layout = engine.analyse_layout(level=PageIteratorLevel.WORD)

        rtl_count = sum(1 for w in layout.words if w.writing_direction == WritingDirection.RIGHT_TO_LEFT)
        ltr_count = sum(1 for w in layout.words if w.writing_direction == WritingDirection.LEFT_TO_RIGHT)

        print(f"[+] Total Words Extracted : {len(layout.words)}")
        print(f"[+] Right-To-Left Words    : {rtl_count}")
        print(f"[+] Left-To-Right Words     : {ltr_count}")
        print("\nSample Extracted Words:")
        print(f"{'Text':<30} {'Confidence':<12} {'Direction':<18} {'Box (L, T, R, B)'}")
        print("-" * 75)

        for w in layout.words[:16]:
            dir_str = "RTL (Arabic)" if w.writing_direction == WritingDirection.RIGHT_TO_LEFT else "LTR (English)"
            b = w.bbox
            box_str = f"[{b.left}, {b.top}, {b.right}, {b.bottom}]"
            print(f"{w.text:<30} {w.confidence:<12.1f} {dir_str:<18} {box_str}")


if __name__ == "__main__":
    main()
