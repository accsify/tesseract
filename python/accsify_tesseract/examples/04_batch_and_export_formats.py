"""
Example 04: Batch OCR Processing and Multi-Format Exports
=========================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.

Demonstrates:
  1. Processing a batch of multiple images with different layouts.
  2. Generating all supported Tesseract export formats:
     - Plain UTF-8 Text
     - hOCR (HTML standard with bounding boxes)
     - TSV (Tab-Separated Values table)
     - Box Format (Character bounding coordinates)
     - UNLV Format
     - Structured Native JSON
  3. Automatic image generation and model provisioning.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accsify_tesseract import (
    TesseractEngine,
    ModelManager,
    ModelType,
    generate_sample_document,
    generate_sample_receipt,
)


def main():
    print("=" * 75)
    print("Accsify Tesseract - Example 04: Batch OCR & Multi-Format Exports")
    print("=" * 75)

    # 1. Ensure models
    for m in ["eng", "ara"]:
        if not ModelManager.is_installed(m, ModelType.FAST):
            print(f"[*] Downloading '{m}' model...")
            ModelManager.download(m, ModelType.FAST)

    # 2. Prepare test images
    doc_path = Path(__file__).resolve().parent / "sample_bilingual_doc.png"
    receipt_path = Path(__file__).resolve().parent / "sample_receipt_mixed.png"

    if not doc_path.is_file():
        generate_sample_document(doc_path)
    if not receipt_path.is_file():
        generate_sample_receipt(receipt_path)

    image_batch = [doc_path, receipt_path]

    # 3. Process Batch
    with TesseractEngine(language="ara+eng") as engine:
        for idx, img_p in enumerate(image_batch, 1):
            print(f"\n[{idx}/{len(image_batch)}] Processing: {img_p.name}...")
            engine.set_image(img_p)
            engine.recognize()

            conf = engine.get_mean_confidence()
            print(f"    Confidence : {conf}%")

            # A. Plain Text
            txt = engine.get_text()
            print(f"    Text Length: {len(txt)} chars")

            # B. hOCR snippet
            hocr = engine.get_hocr()
            print(f"    hOCR Length: {len(hocr)} chars (valid HTML: {hocr.startswith('<?xml') or '<html' in hocr})")

            # C. TSV line count
            tsv = engine.get_tsv()
            tsv_lines = tsv.strip().split("\n")
            print(f"    TSV Rows   : {len(tsv_lines)} items")

            # D. Box format line count
            box = engine.get_box()
            box_lines = box.strip().split("\n")
            print(f"    Box Glyphs : {len(box_lines)} characters")

            # E. UNLV format
            unlv = engine.get_unlv()
            print(f"    UNLV Length: {len(unlv)} chars")

            # F. JSON format
            json_str = engine.get_json()
            print(f"    JSON Length: {len(json_str)} bytes")

            # Save sample exports for the second image (receipt)
            if idx == 2:
                export_dir = Path(__file__).resolve().parent / "sample_exports"
                export_dir.mkdir(exist_ok=True)
                (export_dir / "receipt.txt").write_text(txt, encoding="utf-8")
                (export_dir / "receipt.hocr").write_text(hocr, encoding="utf-8")
                (export_dir / "receipt.tsv").write_text(tsv, encoding="utf-8")
                (export_dir / "receipt.box").write_text(box, encoding="utf-8")
                (export_dir / "receipt.json").write_text(json_str, encoding="utf-8")
                print(f"\n[+] Exported all 5 format artifacts to: {export_dir}")


if __name__ == "__main__":
    main()
