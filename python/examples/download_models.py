"""
Interactive Model Catalog and Downloader Example.
=================================================
Company: accsify
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accsify_tesseract import ModelManager, ModelType


def progress_hook(name, m_type, downloaded, total, pct, msg):
    mb_dl = downloaded / (1024 * 1024)
    mb_tot = total / (1024 * 1024) if total > 0 else 0
    print(f"\r[*] Downloading {name}: {pct:.1f}% ({mb_dl:.2f}/{mb_tot:.2f} MB) - {msg}    ", end="", flush=True)
    if pct >= 100.0:
        print()
    return True


def main():
    print(f"Active Tessdata Path: {ModelManager.get_path()}")

    # 1. List installed models
    installed = ModelManager.list_installed()
    print(f"Installed models: {installed}")

    # 2. Query catalog
    catalog = ModelManager.list_catalog(ModelType.FAST)
    print(f"\nFast models available: {len(catalog)}")
    for item in catalog[:8]:
        status = "Installed" if item.is_installed else "Not Installed"
        print(f"  - {item.name:<12} ({item.display_name:<25}) : {item.file_size_mb:.1f} MB [{status}]")

    # 3. Example download (e.g. French 'fra' fast model)
    target = "fra"
    if not ModelManager.is_installed(target, ModelType.FAST):
        print(f"\nDownloading '{target}' with live callback...")
        ModelManager.download(target, ModelType.FAST, progress_hook)
        print(f"[+] Download of '{target}' completed!")
    else:
        print(f"\nModel '{target}' is already installed.")


if __name__ == "__main__":
    main()
