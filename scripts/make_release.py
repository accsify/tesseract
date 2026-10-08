#!/usr/bin/env python3
"""
Accsify Tesseract - GitHub Release Packager
===========================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.

Packages compiled standalone binaries, C ABI headers, documentation,
and Python wheels into official GitHub release ZIP archives and computes SHA256 checksums.
"""

import os
import sys
import shutil
import hashlib
import zipfile
import subprocess
from pathlib import Path


VERSION = "5.5.0.1"
COMPANY = "accsify"


def sha256_file(path: Path) -> str:
    """Calculate the SHA256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    root_dir = Path(__file__).resolve().parent.parent
    dist_dir = root_dir / "dist"
    release_dir = root_dir / "release"
    python_dist_dir = root_dir / "python" / "dist"
    include_dir = root_dir / "include"

    print("=" * 72)
    print(f"  Accsify Tesseract v{VERSION} - GitHub Release Packager")
    print(f"  Company: {COMPANY}")
    print("=" * 72)

    # 1. Verify native binaries exist
    x64_dll = dist_dir / "x64" / "tesseract_engine.dll"
    x86_dll = dist_dir / "x86" / "tesseract_engine.dll"

    if not x64_dll.is_file() or not x86_dll.is_file():
        print("[ERROR] Compiled binaries missing in dist/x64 or dist/x86!")
        print("        Please run build.cmd first to compile standalone DLLs.")
        sys.exit(1)

    # 2. Verify or trigger Python packaging if python/dist is empty
    if not python_dist_dir.is_dir() or not list(python_dist_dir.glob("*.whl")):
        print("[*] Python distribution packages not found. Building them now...")
        build_pkg_cmd = root_dir / "python" / "build_package.cmd"
        if build_pkg_cmd.is_file():
            ret = subprocess.call(["cmd.exe", "/c", str(build_pkg_cmd)], cwd=str(root_dir / "python"))
            if ret != 0:
                print("[WARNING] Python packaging exited with non-zero code.")

    # 3. Clean and prepare release directory
    if release_dir.is_dir():
        shutil.rmtree(release_dir)
    release_dir.mkdir(parents=True, exist_ok=True)

    # Common documentation and license files
    docs_files = []
    readme_file = root_dir / "README.md"
    if readme_file.is_file():
        docs_files.append((readme_file, "README.md"))
    cli_readme = root_dir / "docs" / "CLI_README.md"
    if cli_readme.is_file():
        docs_files.append((cli_readme, "CLI_README.md"))
    license_file = root_dir / "LICENSE"
    if not license_file.is_file():
        license_file = root_dir / "python" / "LICENSE"
    if license_file.is_file():
        docs_files.append((license_file, "LICENSE"))

    # Header files
    header_files = []
    for h in include_dir.glob("*.h"):
        header_files.append((h, f"include/{h.name}"))

    created_zips = []

    # -------------------------------------------------------------------------
    # Bundle 1: Windows x64 (AMD64) Standalone SDK & CLI
    # -------------------------------------------------------------------------
    zip_x64_name = f"accsify-tesseract-v{VERSION}-windows-x64.zip"
    zip_x64_path = release_dir / zip_x64_name
    print(f"[*] Packaging {zip_x64_name}...")
    with zipfile.ZipFile(zip_x64_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        # Binaries
        for bin_name in ("tesseract_engine.dll", "tesseract_cli.exe", "tesseract_engine.lib"):
            src = dist_dir / "x64" / bin_name
            if src.is_file():
                z.write(src, arcname=bin_name)
        # Headers
        for src, arc in header_files:
            z.write(src, arcname=arc)
        # Docs
        for src, arc in docs_files:
            z.write(src, arcname=arc)
    created_zips.append(zip_x64_path)

    # -------------------------------------------------------------------------
    # Bundle 2: Windows x86 (Win32) Standalone SDK & CLI
    # -------------------------------------------------------------------------
    zip_x86_name = f"accsify-tesseract-v{VERSION}-windows-x86.zip"
    zip_x86_path = release_dir / zip_x86_name
    print(f"[*] Packaging {zip_x86_name}...")
    with zipfile.ZipFile(zip_x86_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        # Binaries
        for bin_name in ("tesseract_engine.dll", "tesseract_cli.exe", "tesseract_engine.lib"):
            src = dist_dir / "x86" / bin_name
            if src.is_file():
                z.write(src, arcname=bin_name)
        # Headers
        for src, arc in header_files:
            z.write(src, arcname=arc)
        # Docs
        for src, arc in docs_files:
            z.write(src, arcname=arc)
    created_zips.append(zip_x86_path)

    # -------------------------------------------------------------------------
    # Bundle 3: Windows Complete SDK (x64 + x86 + Headers + Tools)
    # -------------------------------------------------------------------------
    zip_all_name = f"accsify-tesseract-v{VERSION}-windows-all.zip"
    zip_all_path = release_dir / zip_all_name
    print(f"[*] Packaging {zip_all_name}...")
    with zipfile.ZipFile(zip_all_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        # x64
        for bin_name in ("tesseract_engine.dll", "tesseract_cli.exe", "tesseract_engine.lib"):
            src = dist_dir / "x64" / bin_name
            if src.is_file():
                z.write(src, arcname=f"x64/{bin_name}")
        # x86
        for bin_name in ("tesseract_engine.dll", "tesseract_cli.exe", "tesseract_engine.lib"):
            src = dist_dir / "x86" / bin_name
            if src.is_file():
                z.write(src, arcname=f"x86/{bin_name}")
        # Headers
        for src, arc in header_files:
            z.write(src, arcname=arc)
        # Docs
        for src, arc in docs_files:
            z.write(src, arcname=arc)
    created_zips.append(zip_all_path)

    # -------------------------------------------------------------------------
    # Bundle 4: Copy Python Wheels and Sdist into Release Folder
    # -------------------------------------------------------------------------
    python_artifacts = []
    if python_dist_dir.is_dir():
        for py_pkg in python_dist_dir.glob("*"):
            if py_pkg.suffix in (".whl", ".gz"):
                dest = release_dir / py_pkg.name
                shutil.copy2(py_pkg, dest)
                python_artifacts.append(dest)
                print(f"[*] Included Python package: {py_pkg.name}")

    # -------------------------------------------------------------------------
    # Generate SHA256SUMS.txt
    # -------------------------------------------------------------------------
    print("[*] Generating SHA256SUMS.txt...")
    all_release_files = sorted(
        [p for p in release_dir.iterdir() if p.is_file() and p.name != "SHA256SUMS.txt"],
        key=lambda x: x.name
    )

    checksum_lines = []
    for f in all_release_files:
        digest = sha256_file(f)
        size_mb = f.stat().st_size / (1024 * 1024)
        checksum_lines.append(f"{digest}  {f.name}")
        print(f"    {f.name:50} [{size_mb:.2f} MB] SHA256: {digest[:16]}...")

    sums_file = release_dir / "SHA256SUMS.txt"
    sums_file.write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    # -------------------------------------------------------------------------
    # Generate Ready-to-Publish RELEASE_NOTES.md
    # -------------------------------------------------------------------------
    notes_content = f"""# Accsify Tesseract OCR v{VERSION}

Official high-performance release of the **Accsify Monolithic Tesseract OCR Engine**, standalone CLI, and Python SDK for Windows.

## Highlights
- **Zero Runtime Dependencies**: Fully static `/MT` MSVC C/C++ build. Runs on any Windows system without external redistributables.
- **Monolithic Architecture**: Single unified `tesseract_engine.dll` bundling Tesseract 5.5, Leptonica 1.84, LibTIFF, LibJPEG, LibPNG, Zlib, OpenMP, and WinHTTP.
- **Standalone CLI**: `tesseract_cli.exe` with structured JSON, hOCR, TSV, Box, UNLV, and plain text output.
- **Automatic Model Manager**: Integrated WinHTTP downloader for fast and best LSTM models (`ara`, `eng`, `osd`, etc.) with real-time download progress.
- **Official Python Package**: PyPI-ready `accsify-tesseract` with pre-bundled x64 and x86 native engines.

## Assets & Checksums (SHA-256)
```
{chr(10).join(checksum_lines)}
```

## Quick Start
```bash
# Extract x64 or x86 archive and run:
tesseract_cli.exe -i document.png -l eng --format json

# Or install via Python wheel:
pip install accsify_tesseract-{VERSION}-py3-none-any.whl
```
"""
    notes_file = release_dir / "RELEASE_NOTES.md"
    notes_file.write_text(notes_content, encoding="utf-8")

    print("\n" + "=" * 72)
    print("  RELEASE PACKAGING COMPLETE!")
    print("=" * 72)
    print(f"  Artifacts directory: {release_dir}")
    print(f"  Total packages generated: {len(all_release_files)}")
    print(f"  Checksum file: {sums_file}")
    print(f"  Release notes template: {notes_file}")
    print("\n  To publish via GitHub CLI:")
    print(f"    gh release create v{VERSION} release/* --title \"Accsify Tesseract v{VERSION}\" --notes-file release/RELEASE_NOTES.md")
    print("=" * 72)


if __name__ == "__main__":
    main()
