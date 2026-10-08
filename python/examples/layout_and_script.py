"""
Layout Analysis and Script Direction Example.
=============================================
Company: accsify
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accsify_tesseract import (
    TesseractEngine, PageIteratorLevel, ModelManager, ModelType
)


def main():
    if not ModelManager.is_installed("eng", ModelType.FAST):
        ModelManager.download("eng", ModelType.FAST)

    img_path = Path(__file__).resolve().parent.parent.parent / "Custom Tesseract DLL Buil..._2026-10-08_18-49-35.png"
    if not img_path.exists():
        print(f"[!] Test image not found at {img_path}")
        return

    with TesseractEngine(language="eng") as engine:
        engine.set_image(img_path)

        # 1. Structured Layout Analysis
        print("\n[*] Running Layout Analysis...")
        layout = engine.analyse_layout(level=PageIteratorLevel.WORD)

        print(f"Total Words Detected: {len(layout.words)}")
        print(f"{'Word Text':<25} {'Confidence':<12} {'Bounding Box (L,T,R,B)':<25} {'Writing Direction'}")
        print("-" * 80)

        for w in layout.words[:15]:  # Display first 15 words
            b = w.bbox
            print(f"{w.text:<25} {w.confidence:<12.1f} [{b.left},{b.top},{b.right},{b.bottom}] {w.writing_direction.name}")

        # 2. Orientation & Script Detection (if osd model is present)
        if ModelManager.is_installed("osd", ModelType.FAST):
            try:
                osd = engine.detect_orientation_and_script()
                print(f"\n[+] OSD Result: Orientation={osd.orientation_deg}°, Script={osd.script_name}")
            except Exception as e:
                print(f"[!] OSD note: {e}")


if __name__ == "__main__":
    main()
