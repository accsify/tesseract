# Accsify Tesseract - Licensing & Compliance Audit

This document details the legal licensing architecture, third-party software attribution, and static linking compliance for the **Accsify Monolithic Tesseract Engine** distribution.

---

## 1. Executive Summary

| Component | Source / Origin | License | Linking Type | Commercial Use | Source Disclosure Required? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Accsify Tesseract** | Accsify | **MIT** | Top-level | Allowed | No |
| **Tesseract OCR** | Upstream (Google / Tesseract) | **Apache-2.0** | Static (`libtesseract.lib`) | Allowed | No |
| **Leptonica** | Upstream (Dan Bloomberg) | **BSD-2-Clause** | Static (`leptonica.lib`) | Allowed | No |
| **stb_image** | Upstream (Sean Barrett) | **Public Domain / MIT** | Inlined Header | Allowed | No |
| **MSVC C/C++ Runtime** | Microsoft Visual Studio | **MSVC EULA (REDIST)** | Static (`/MT`) | Allowed | No |
| **Windows APIs (WinHTTP)** | Microsoft Windows OS | **Windows SDK License** | Dynamic System Link | Allowed | No |

> [!IMPORTANT]
> **No GPL, AGPL, or LGPL code is statically linked or incorporated.**
> The entire monolithic distribution is licensed under **100% permissive open-source licenses** (MIT, Apache-2.0, BSD-2-Clause).

---

## 2. Permissive License Compatibility Matrix

### Apache License 2.0 (Tesseract OCR)
* **Permissions**: Commercial use, modification, distribution, sublicense, private use.
* **Requirements** (Section 4 of Apache-2.0):
  1. Retain the copyright notice and license text in all distributions. *(Complied: included in root `LICENSE` and `python/LICENSE`)*.
  2. State changes made to source files. *(Complied: upstream `deps/tesseract` is kept pristine; our custom code resides in `src/` and `include/`)*.
  3. Include NOTICE if present.

### BSD 2-Clause (Leptonica)
* **Permissions**: Commercial use, modification, distribution, private use.
* **Requirements**:
  1. Retain copyright notice and disclaimer in source code.
  2. Reproduce copyright notice and disclaimer in documentation or distribution materials. *(Complied: included in root `LICENSE` and `python/LICENSE`)*.

### MIT License (Accsify Wrapper & Engine)
* Compatible with both Apache-2.0 and BSD-2-Clause. The combined work can be distributed as a unified product under permissive terms.

---

## 3. Static Linking (`/MT`) Analysis

* The C++ engine is compiled with `/MT` (MSVC static runtime).
* Microsoft Visual Studio allows distributing the statically linked MSVC runtime libraries as part of an end-user binary or library.
* External copyleft image libraries (e.g. `libarchive`, `libcurl`) are **explicitly disabled** in `CMakeLists.txt`:
  * `DISABLE_CURL ON`: Our HTTP downloader uses native Microsoft `WinHTTP.dll` (standard Windows OS system library).
  * `DISABLE_ARCHIVE ON`: No archive decompression libraries linked.
  * `DISABLE_TIFF ON` (built-in minimal codecs via Leptonica).
  * `GRAPHICS_DISABLED ON`: ScrollView graphics dependencies disabled.

---

## 4. Upstream Dependency Isolation Policy

* All external third-party repositories live strictly in `deps/`:
  * `deps/tesseract` (Upstream Tesseract source)
  * `deps/leptonica` (Upstream Leptonica source)
* **Our build tools, release packagers, and `version.cmd` NEVER modify files in `deps/`**.
* The version number (e.g. `5.5.0.1`) represents the **Accsify Tesseract distribution version**, while the core Tesseract engine reports its native version (`5.5.0`) via `tess_version()`.
