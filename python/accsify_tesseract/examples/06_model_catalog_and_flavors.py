"""
Example 06: Model Catalog, Flavors (FAST vs BEST), and Live Downloader
======================================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.

Demonstrates:
  1. Inspecting locally installed traineddata models.
  2. Querying the online catalog of 100+ languages and scripts.
  3. Live progress reporting hooks for GUI/CLI download bars.
  4. Switching model flavors between FAST (integer LSTM) and BEST (float LSTM).
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accsify_tesseract import ModelManager, ModelType


def progress_hook(name, m_type, downloaded, total, pct, msg):
    mb_dl = downloaded / (1024 * 1024)
    mb_tot = total / (1024 * 1024) if total > 0 else 0
    bar_len = 30
    filled = int(bar_len * pct / 100.0)
    bar = "=" * filled + "-" * (bar_len - filled)
    print(f"\r[*] [{bar}] {pct:5.1f}% ({mb_dl:5.2f}/{mb_tot:5.2f} MB) {name} : {msg}   ", end="", flush=True)
    if pct >= 100.0:
        print()
    return True


def main():
    print("=" * 75)
    print("Accsify Tesseract - Example 06: Model Catalog & WinHTTP Downloader")
    print("=" * 75)
    print(f"[*] Tessdata Storage Path: {ModelManager.get_path()}")

    # 1. List currently installed models
    installed = ModelManager.list_installed()
    print(f"\n[+] Installed Models Count: {len(installed)}")
    for m in installed:
        print(f"    - {m}")

    # 2. Query available models in FAST catalog
    catalog = ModelManager.list_catalog(ModelType.FAST)
    print(f"\n[+] Total Available in Fast Catalog: {len(catalog)}")
    print("\nSample Catalog Entries:")
    print(f"{'Code':<10} {'Language / Script':<30} {'Size':<10} {'Status'}")
    print("-" * 65)

    sample_codes = ["eng", "ara", "fra", "deu", "spa", "chi_sim", "jpn", "rus"]
    for item in catalog:
        if item.name in sample_codes:
            st = "INSTALLED" if item.is_installed else "Available"
            print(f"{item.name:<10} {item.display_name:<30} {item.file_size_mb:5.1f} MB  [{st}]")

    # 3. Interactive Download Test (e.g. 'deu' or 'fra')
    target = "fra"
    if not ModelManager.is_installed(target, ModelType.FAST):
        print(f"\n[*] Downloading '{target}' (French) with live progress bar:")
        ModelManager.download(target, ModelType.FAST, progress_hook)
        print(f"[+] Download of '{target}' completed successfully!")
    else:
        print(f"\n[+] '{target}' model is already installed locally.")


if __name__ == "__main__":
    main()
