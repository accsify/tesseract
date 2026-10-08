"""
Basic OCR Example using Accsify Tesseract Python Package.
=========================================================
Company: accsify
"""

import sys
from pathlib import Path

# Add parent directory to path for development testing
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accsify_tesseract import TesseractEngine, ModelManager, ModelType


def main():
    print(f"[*] Accsify Tesseract Engine Version: {TesseractEngine.version()}")

    # Ensure English model is downloaded
    if not ModelManager.is_installed("eng", ModelType.FAST):
        print("[*] Downloading 'eng' model...")
        ModelManager.download("eng", ModelType.FAST)

    # Path to test image
    img_path = Path(__file__).resolve().parent.parent.parent / "Custom Tesseract DLL Buil..._2026-10-08_18-49-35.png"
    if not img_path.exists():
        print(f"[!] Test image not found at {img_path}")
        return

    # Initialize Engine (RAII Context Manager)
    with TesseractEngine(language="eng") as engine:
        engine.set_image(img_path)
        engine.recognize()

        text = engine.get_text()
        conf = engine.get_mean_confidence()

        print(f"\n[+] Recognition Confidence: {conf}%")
        print("\n--- Recognized Text Snippet (first 400 chars) ---")
        print(text[:400])
        print("-------------------------------------------------")


if __name__ == "__main__":
    main()
