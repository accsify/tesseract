"""
Example 03: Page Layout Analysis and Structured JSON Export
===========================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.

Demonstrates:
  1. Hierarchical page decomposition (Blocks -> Paragraphs -> Lines -> Words).
  2. Exact pixel bounding boxes (left, top, right, bottom).
  3. Orientation and Script Detection (OSD).
  4. Native structured JSON export (get_json and get_structured_dict).
  5. Auto-provisioning of 'eng', 'ara', and 'osd' models.
"""

import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accsify_tesseract import (
    TesseractEngine,
    PageIteratorLevel,
    ModelManager,
    ModelType,
    generate_sample_document,
)


def main():
    print("=" * 75)
    print("Accsify Tesseract - Example 03: Layout Analysis and JSON Export")
    print("=" * 75)

    # 1. Ensure required models
    for m in ["eng", "ara", "osd"]:
        if not ModelManager.is_installed(m, ModelType.FAST):
            print(f"[*] Downloading '{m}' model...")
            ModelManager.download(m, ModelType.FAST)

    # 2. Ensure test image
    img_path = Path(__file__).resolve().parent / "sample_bilingual_doc.png"
    if not img_path.is_file():
        print("[*] Generating bilingual test image...")
        generate_sample_document(img_path)

    # 3. Analyze Page Structure
    with TesseractEngine(language="ara+eng") as engine:
        engine.set_image(img_path)
        engine.recognize()

        # Run layout analysis
        print("\n[*] Analyzing Hierarchical Layout...")
        layout = engine.analyse_layout(level=PageIteratorLevel.WORD)

        print(f"[+] Total Detected Words : {len(layout.words)}")
        print(f"[+] Total Lines          : {len(layout.lines)}")
        print(f"[+] Total Paragraphs     : {len(layout.paragraphs)}")
        print(f"[+] Total Blocks         : {len(layout.blocks)}")

        # Display first 8 words with coordinates
        print("\nSample Word Elements with Bounding Boxes:")
        print(f"{'Word':<25} {'Confidence':<12} {'Bounding Box [L,T,R,B]':<26} {'Direction'}")
        print("-" * 75)
        for w in layout.words[:8]:
            b = w.bbox
            print(f"{w.text:<25} {w.confidence:<12.1f} [{b.left:4d},{b.top:4d},{b.right:4d},{b.bottom:4d}]  {w.writing_direction.name}")

        # 4. Orientation & Script Detection
        try:
            osd = engine.detect_orientation_and_script()
            print(f"\n[+] OSD Result: Orientation={osd.orientation_deg}°, Script='{osd.script_name}' (conf: {osd.script_confidence:.1f})")
        except Exception as e:
            print(f"[-] OSD Note: {e}")

        # 5. Native JSON Export
        print("\n[*] Generating Structured JSON...")
        doc_dict = engine.get_structured_dict()
        out_json_path = Path(__file__).resolve().parent / "sample_analysis.json"
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(doc_dict, f, ensure_ascii=False, indent=2)

        print(f"[+] Saved structured analysis to: {out_json_path.name}")
        print(f"    - Mean Confidence : {doc_dict.get('mean_confidence')}%")
        print(f"    - Total Words in JSON : {len(doc_dict.get('words', []))}")


if __name__ == "__main__":
    main()
