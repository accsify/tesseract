#!/usr/bin/env python3
"""
Accsify Tesseract - Centralized Version Manager
================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.

Single Command / Single Source of Truth version manager.
Synchronizes version across C++ engine, CMake, Windows RC resources,
headers, Python packages, release scripts, and CI workflows.
"""

import sys
import re
from pathlib import Path


def get_root_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def read_current_version(root_dir: Path) -> str:
    ver_file = root_dir / "VERSION"
    if ver_file.is_file():
        return ver_file.read_text(encoding="utf-8").strip()
    return "5.5.0.1"


def parse_version_tuple(ver_str: str):
    parts = ver_str.strip().split(".")
    while len(parts) < 4:
        parts.append("0")
    return tuple(int(p) if p.isdigit() else 0 for p in parts[:4])


def check_status(root_dir: Path):
    curr = read_current_version(root_dir)
    print("=" * 72)
    print("  Accsify Tesseract - Version Synchronization Status")
    print(f"  Current Canonical Version (VERSION): {curr}")
    print("=" * 72)

    files_to_check = [
        ("VERSION", root_dir / "VERSION", r"^(.*)$"),
        ("python/VERSION", root_dir / "python" / "VERSION", r"^(.*)$"),
        ("python/pyproject.toml", root_dir / "python" / "pyproject.toml", r'version\s*=\s*"([^"]+)"'),
        ("python/setup.cfg", root_dir / "python" / "setup.cfg", r'version\s*=\s*([0-9a-zA-Z\.]+)'),
        ("python/accsify_tesseract/__init__.py", root_dir / "python" / "accsify_tesseract" / "__init__.py", r'return\s*"([^"]+)"'),
        ("CMakeLists.txt", root_dir / "CMakeLists.txt", r'set\(ACCSIFY_PROJECT_VERSION\s+"([^"]+)"\)'),
        ("version.rc", root_dir / "version.rc", r'VER_FILEVERSION_STR\s+"([^\\"\s]+)'),
        ("docs/CLI_README.md", root_dir / "docs" / "CLI_README.md", r'Version:\*\*\s+([0-9a-zA-Z\.]+)'),
        (".github/workflows/build-and-release.yml", root_dir / ".github" / "workflows" / "build-and-release.yml", r"default:\s*'v([^']+)'"),
    ]

    all_in_sync = True
    for label, path, pattern in files_to_check:
        if not path.is_file():
            print(f"  [-] {label:42} [NOT FOUND]")
            all_in_sync = False
            continue
        content = path.read_text(encoding="utf-8")
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            v = match.group(1).strip()
            match_status = "[OK]" if v == curr else f"[MISMATCH: {v}]"
            if v != curr:
                all_in_sync = False
            print(f"  {match_status:12} {label:38} : {v}")
        else:
            print(f"  [?] {label:42} : Pattern not matched")

    print("-" * 72)
    if all_in_sync:
        print(f"  Result: All components are 100% in sync with version {curr}!")
    else:
        print(f"  Result: Some components mismatch. Run 'version.cmd {curr}' to synchronize.")
    print("=" * 72)


def set_version(root_dir: Path, new_ver: str):
    # Validate format: e.g. 5.5.0 or 5.5.0.1
    if not re.match(r"^\d+\.\d+\.\d+(\.\d+)?$", new_ver):
        print(f"[ERROR] Invalid version format '{new_ver}'. Expected format: X.Y.Z or X.Y.Z.W (e.g. 5.5.0.2)")
        sys.exit(1)

    v_major, v_minor, v_patch, v_build = parse_version_tuple(new_ver)
    rc_ver_tuple = f"{v_major},{v_minor},{v_patch},{v_build}"

    print("=" * 72)
    print(f"  Accsify Tesseract - Updating Project Version to {new_ver}")
    print("=" * 72)

    # 1. Root VERSION
    (root_dir / "VERSION").write_text(f"{new_ver}\n", encoding="utf-8")
    print(f"  [OK] Updated VERSION -> {new_ver}")

    # 2. python/VERSION
    (root_dir / "python" / "VERSION").write_text(f"{new_ver}\n", encoding="utf-8")
    print(f"  [OK] Updated python/VERSION -> {new_ver}")

    # 3. python/pyproject.toml
    pyproject_path = root_dir / "python" / "pyproject.toml"
    if pyproject_path.is_file():
        text = pyproject_path.read_text(encoding="utf-8")
        text = re.sub(r'version\s*=\s*"[^"]+"', f'version = "{new_ver}"', text, count=1)
        pyproject_path.write_text(text, encoding="utf-8")
        print(f"  [OK] Updated python/pyproject.toml -> {new_ver}")

    # 4. python/setup.cfg
    setup_cfg_path = root_dir / "python" / "setup.cfg"
    if setup_cfg_path.is_file():
        text = setup_cfg_path.read_text(encoding="utf-8")
        text = re.sub(r'version\s*=\s*[0-9a-zA-Z\.]+', f'version = {new_ver}', text, count=1)
        setup_cfg_path.write_text(text, encoding="utf-8")
        print(f"  [OK] Updated python/setup.cfg -> {new_ver}")

    # 5. python/accsify_tesseract/__init__.py
    init_path = root_dir / "python" / "accsify_tesseract" / "__init__.py"
    if init_path.is_file():
        text = init_path.read_text(encoding="utf-8")
        text = re.sub(r'return\s*"[0-9a-zA-Z\.]+"', f'return "{new_ver}"', text, count=1)
        init_path.write_text(text, encoding="utf-8")
        print(f"  [OK] Updated python/accsify_tesseract/__init__.py -> {new_ver}")

    # 6. version.rc
    rc_path = root_dir / "version.rc"
    if rc_path.is_file():
        text = rc_path.read_text(encoding="utf-8")
        text = re.sub(r'#define\s+VER_FILEVERSION\s+[0-9,]+', f'#define VER_FILEVERSION             {rc_ver_tuple}', text)
        text = re.sub(r'#define\s+VER_FILEVERSION_STR\s+"[^"]+"', f'#define VER_FILEVERSION_STR         "{new_ver}\\\\0"', text)
        text = re.sub(r'#define\s+VER_PRODUCTVERSION\s+[0-9,]+', f'#define VER_PRODUCTVERSION          {rc_ver_tuple}', text)
        text = re.sub(r'#define\s+VER_PRODUCTVERSION_STR\s+"[^"]+"', f'#define VER_PRODUCTVERSION_STR      "{new_ver}\\\\0"', text)
        rc_path.write_text(text, encoding="utf-8")
        print(f"  [OK] Updated version.rc -> {new_ver} ({rc_ver_tuple})")

    # 7. CMakeLists.txt
    cmake_path = root_dir / "CMakeLists.txt"
    if cmake_path.is_file():
        text = cmake_path.read_text(encoding="utf-8")
        text = re.sub(r'set\(ACCSIFY_PROJECT_VERSION\s+"[^"]+"\)', f'set(ACCSIFY_PROJECT_VERSION "{new_ver}")', text, count=1)
        cmake_path.write_text(text, encoding="utf-8")
        print(f"  [OK] Updated CMakeLists.txt -> {new_ver}")

    # 8. docs/CLI_README.md & dist/CLI_README.md
    for doc in (root_dir / "docs" / "CLI_README.md", root_dir / "dist" / "CLI_README.md"):
        if doc.is_file():
            text = doc.read_text(encoding="utf-8")
            text = re.sub(r'Version:\*\*\s+[0-9a-zA-Z\.]+', f'Version:** {new_ver}', text)
            doc.write_text(text, encoding="utf-8")
            print(f"  [OK] Updated {doc.relative_to(root_dir)} -> {new_ver}")

    # 9. .github/workflows/build-and-release.yml
    workflow_path = root_dir / ".github" / "workflows" / "build-and-release.yml"
    if workflow_path.is_file():
        text = workflow_path.read_text(encoding="utf-8")
        text = re.sub(r"default:\s*'v[^']+'", f"default: 'v{new_ver}'", text)
        workflow_path.write_text(text, encoding="utf-8")
        print(f"  [OK] Updated .github/workflows/build-and-release.yml -> v{new_ver}")

    print("=" * 72)
    print(f"  SUCCESS: All files successfully synchronized to v{new_ver}!")
    print("=" * 72)


def main():
    root_dir = get_root_dir()
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        if arg.startswith("v"):
            arg = arg[1:]
        if arg in ("--help", "-h"):
            print("Usage:")
            print("  version.cmd               Display current version synchronization status")
            print("  version.cmd <NEW_VERSION> Set and synchronize version across all files (e.g. 5.5.0.2)")
            sys.exit(0)
        set_version(root_dir, arg)
    else:
        check_status(root_dir)


if __name__ == "__main__":
    main()
