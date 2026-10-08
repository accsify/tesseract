#!/usr/bin/env python3
"""
Setup script for accsify-tesseract Python package.
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

import os
import sys
import shutil
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist

try:
    from setuptools.command.bdist_wheel import bdist_wheel as _bdist_wheel
except ImportError:
    try:
        from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    except ImportError:
        _bdist_wheel = None


def sync_native_libraries():
    """
    Ensure standalone native libraries (DLL, LIB, CLI) are copied from dist/ or bin/
    into accsify_tesseract/lib/ (and bin/) for x64 and x86 architectures.
    """
    python_dir = Path(__file__).resolve().parent
    pkg_dir = python_dir / "accsify_tesseract"
    repo_root = python_dir.parent

    # Candidate source directories in order of preference
    source_candidates = [
        repo_root / "dist",
        repo_root / "bin",
        Path.cwd() / "dist",
        Path.cwd() / "bin",
    ]

    for arch in ("x64", "x86"):
        target_lib_dir = pkg_dir / "lib" / arch
        target_lib_dir.mkdir(parents=True, exist_ok=True)

        found_src = None
        for cand in source_candidates:
            cand_arch = cand / arch
            if (cand_arch / "tesseract_engine.dll").is_file():
                found_src = cand_arch
                break

        if found_src:
            for fname in ("tesseract_engine.dll", "tesseract_cli.exe", "tesseract_engine.lib"):
                src_file = found_src / fname
                if src_file.is_file():
                    dst_lib_file = target_lib_dir / fname
                    # Copy if missing or different in size / mtime
                    if not dst_lib_file.exists() or src_file.stat().st_mtime > dst_lib_file.stat().st_mtime or src_file.stat().st_size != dst_lib_file.stat().st_size:
                        shutil.copy2(src_file, dst_lib_file)
                        print(f"[setup.py] Bundled native binary: {src_file.name} -> {dst_lib_file.relative_to(python_dir)}")


# Synchronize binaries immediately upon loading setup.py
sync_native_libraries()


class BuildPyCommand(_build_py):
    """Custom build_py command that guarantees native libraries are synchronized and included."""
    def run(self):
        sync_native_libraries()
        super().run()
        # Ensure build directory also receives lib folder
        pkg_dir = Path(__file__).resolve().parent / "accsify_tesseract"
        build_pkg = Path(self.build_lib) / "accsify_tesseract"
        src_sub = pkg_dir / "lib"
        dst_sub = build_pkg / "lib"
        if src_sub.is_dir():
            shutil.copytree(src_sub, dst_sub, dirs_exist_ok=True)
            print(f"[setup.py] Copied native lib tree to build/lib directory.")


class SdistCommand(_sdist):
    """Custom sdist command that guarantees native libraries are packaged into source distribution."""
    def run(self):
        sync_native_libraries()
        super().run()


cmdclass = {
    "build_py": BuildPyCommand,
    "sdist": SdistCommand,
}

if _bdist_wheel is not None:
    class BDistWheelCommand(_bdist_wheel):
        """Custom bdist_wheel command that guarantees native libraries are included in wheel."""
        def run(self):
            sync_native_libraries()
            super().run()

    cmdclass["bdist_wheel"] = BDistWheelCommand


# Read long description from README.md
readme_path = Path(__file__).resolve().parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.is_file() else ""

setup(
    name="accsify-tesseract",
    version="5.5.0.1",
    author="accsify",
    author_email="support@accsify.com",
    description="Official Python SDK and CLI for the Accsify Monolithic Tesseract OCR Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/accsify/tesseract",
    project_urls={
        "Documentation": "https://github.com/accsify/tesseract#readme",
        "Bug Tracker": "https://github.com/accsify/tesseract/issues",
    },
    packages=find_packages(),
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        "accsify_tesseract": [
            "py.typed",
            "lib/x64/*",
            "lib/x86/*",
        ],
    },
    entry_points={
        "console_scripts": [
            "accsify-tesseract=accsify_tesseract.cli:main",
        ],
    },
    cmdclass=cmdclass,
    zip_safe=False,
)
