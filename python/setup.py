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


def sync_native_libraries(arch_target: str = "all"):
    """
    Ensure standalone native libraries (DLL, LIB, CLI) are copied from dist/ or bin/
    into accsify_tesseract/lib/ for target architecture ('x64', 'x86', or 'all').
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

    all_archs = ("x64", "x86")
    active_archs = (arch_target,) if arch_target in all_archs else all_archs

    # Remove binaries of non-target architecture from wheel workspace (preserve tessdata!)
    if arch_target in all_archs:
        for other in all_archs:
            if other != arch_target:
                other_dir = pkg_dir / "lib" / other
                if other_dir.is_dir():
                    for fname in ("tesseract_engine.dll", "tesseract_cli.exe", "tesseract_engine.lib"):
                        bfile = other_dir / fname
                        if bfile.is_file():
                            bfile.unlink()

    for arch in active_archs:
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
                        print(f"[setup.py] Bundled native binary ({arch}): {src_file.name} -> {dst_lib_file.relative_to(python_dir)}")


# Synchronize binaries immediately upon loading setup.py
sync_native_libraries("all")


class BuildPyCommand(_build_py):
    """Custom build_py command that guarantees native libraries are synchronized and included."""
    def run(self):
        super().run()
        # Synchronize lib directory strictly matching pkg_dir/lib
        pkg_dir = Path(__file__).resolve().parent / "accsify_tesseract"
        build_pkg = Path(self.build_lib) / "accsify_tesseract"
        src_sub = pkg_dir / "lib"
        dst_sub = build_pkg / "lib"
        if dst_sub.is_dir():
            shutil.rmtree(dst_sub, ignore_errors=True)
        if src_sub.is_dir():
            shutil.copytree(src_sub, dst_sub, dirs_exist_ok=True)


def sync_tests_for_packaging():
    """Temporarily mirror unified ../tests into python/tests when building sdist."""
    python_dir = Path(__file__).resolve().parent
    repo_tests = python_dir.parent / "tests"
    target_tests = python_dir / "tests"
    if repo_tests.is_dir() and repo_tests.resolve() != target_tests.resolve():
        shutil.copytree(repo_tests, target_tests, dirs_exist_ok=True)


def clean_tests_after_packaging():
    """Clean up ephemeral tests folder after sdist packaging to keep repo pristine."""
    python_dir = Path(__file__).resolve().parent
    target_tests = python_dir / "tests"
    if target_tests.is_dir():
        shutil.rmtree(target_tests, ignore_errors=True)


class SdistCommand(_sdist):
    """Custom sdist command that guarantees native libraries and tests are packaged into source distribution."""
    def run(self):
        sync_native_libraries("all")
        sync_tests_for_packaging()
        try:
            super().run()
        finally:
            clean_tests_after_packaging()


cmdclass = {
    "build_py": BuildPyCommand,
    "sdist": SdistCommand,
}

if _bdist_wheel is not None:
    class BDistWheelCommand(_bdist_wheel):
        """Custom bdist_wheel command that packages ONLY the target architecture's native binaries."""
        def run(self):
            plat = getattr(self, "plat_name", "") or ""
            target_arch = "x64" if ("amd64" in plat or "x86_64" in plat) else ("x86" if ("win32" in plat or "x86" in plat) else "all")
            sync_native_libraries(arch_target=target_arch)

            # Wipe build directory so stale files from prior architectures are never packaged
            build_dir = Path(__file__).resolve().parent / "build"
            if build_dir.is_dir():
                shutil.rmtree(build_dir, ignore_errors=True)

            try:
                super().run()
            finally:
                # Always restore all architectures for local dev environment
                sync_native_libraries(arch_target="all")

    cmdclass["bdist_wheel"] = BDistWheelCommand


# Read version from VERSION file (Single Source of Truth)
def get_package_version() -> str:
    for cand in (
        Path(__file__).resolve().parent / "VERSION",
        Path(__file__).resolve().parent.parent / "VERSION",
        Path.cwd() / "VERSION",
    ):
        if cand.is_file():
            v = cand.read_text(encoding="utf-8").strip()
            if v:
                return v
    return "5.5.0.1"


pkg_version = get_package_version()

# Read long description from README.md
readme_path = Path(__file__).resolve().parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.is_file() else ""

setup(
    name="accsify-tesseract",
    version=pkg_version,
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
            "examples/*",
            "examples/*.png",
            "examples/*.md",
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
