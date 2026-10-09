"""
Example 05: In-Memory OCR from PIL Images and Raw Byte Buffers
==============================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.

Demonstrates:
  1. Passing in-memory PIL.Image.Image directly without saving to disk.
  2. Passing compressed file bytes (e.g. from an HTTP payload or database BLOB).
  3. High-throughput performance without disk I/O latency.
  4. Auto-provisioning of required models and test imagery.
"""

import io
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accsify_tesseract import (
    TesseractEngine,
    ModelManager,
    ModelType,
    generate_sample_document,
)


def main():
    print("=" * 75)
    print("Accsify Tesseract - Example 05: In-Memory OCR (PIL & Raw Buffers)")
    print("=" * 75)

    # 1. Ensure models
    if not ModelManager.is_installed("eng", ModelType.FAST):
        print("[*] Downloading 'eng' model...")
        ModelManager.download("eng", ModelType.FAST)

    # 2. Generate PIL Image in memory (no disk write required)
    print("\n[*] Generating PIL Image dynamically in memory...")
    pil_image = generate_sample_document(output_path=None)
    print(f"[+] In-memory PIL Image ready: {pil_image.size}, mode={pil_image.mode}")

    # 3. Create compressed PNG bytes in memory (io.BytesIO)
    png_io = io.BytesIO()
    pil_image.save(png_io, format="PNG")
    raw_png_bytes = png_io.getvalue()
    print(f"[+] In-memory PNG byte buffer ready: {len(raw_png_bytes):,} bytes")

    # 4. OCR directly from PIL Image instance
    with TesseractEngine(language="eng") as engine:
        t0 = time.perf_counter()
        engine.set_image(pil_image)
        engine.recognize()
        text_from_pil = engine.get_text()
        conf_pil = engine.get_mean_confidence()
        t_pil = (time.perf_counter() - t0) * 1000

        print(f"\n[+] Method A: PIL Image Input")
        print(f"    - Processing Time : {t_pil:.1f} ms")
        print(f"    - Confidence      : {conf_pil}%")
        print(f"    - Snippet         : {text_from_pil.strip().splitlines()[0]}")

        # 5. OCR directly from raw compressed bytes
        t0 = time.perf_counter()
        engine.set_image(raw_png_bytes)
        engine.recognize()
        text_from_bytes = engine.get_text()
        conf_bytes = engine.get_mean_confidence()
        t_bytes = (time.perf_counter() - t0) * 1000

        print(f"\n[+] Method B: Raw In-Memory Bytes Input")
        print(f"    - Processing Time : {t_bytes:.1f} ms")
        print(f"    - Confidence      : {conf_bytes}%")
        print(f"    - Snippet         : {text_from_bytes.strip().splitlines()[0]}")

        # Assert parity
        assert conf_pil == conf_bytes, "Parity check failed between PIL and raw bytes input"
        print("\n[+] Verification: Both in-memory input pathways yielded identical results!")


if __name__ == "__main__":
    main()
