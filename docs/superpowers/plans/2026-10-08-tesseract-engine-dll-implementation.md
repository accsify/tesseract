# Monolithic Tesseract Engine DLL Implementation Plan

> **Note:** Direct execution by primary agent as explicitly instructed by the user ("don't use sub ajents you wark all").

**Goal:** Build a production-grade, zero-dependency (`/MT`) monolithic Windows DLL (`tesseract_engine.dll`) for x64 and x86 containing the full Tesseract 5.x engine, Leptonica, layout analysis, script/orientation detection, WinHTTP model downloader, version metadata (`version.rc` for "accsi"), multi-arch `build.cmd`, master `include.h`, and a complete Python ctypes wrapper.

**Architecture:**
A unified C-ABI layer (`tesseract_engine.h`) wraps Tesseract 5.x and Leptonica, statically linked with Windows system libraries (`winhttp.lib`, `ws2_32.lib`, `shlwapi.lib`, `user32.lib`) and compiled with `/MT` (Static C Runtime). A native Windows WinHTTP streaming downloader provides zero-dependency HTTPS model downloads with progress callbacks. An auto-detecting `build.cmd` locates Visual Studio and compiles both x64 and x86 binaries.

**Architecture Diagram:**

```mermaid
graph TD
    subgraph Client Applications
        PY[Python Wrapper ctypes] -->|C ABI| DLL[tesseract_engine.dll]
        CS[C# P/Invoke] -->|C ABI| DLL
        CPP[C/C++ include.h] -->|C ABI| DLL
    end

    subgraph "tesseract_engine.dll (/MT Static Monolithic)"
        API[C Export Interface]
        ENG[Tesseract 5.x Core Engine]
        LEPT[Leptonica Image Engine]
        LAYOUT[Layout Analysis & Iterators]
        OSD[Orientation & Script Detection]
        MM[Model Manager & Catalog]
        HTTP[WinHTTP Native Downloader]
        RC[version.rc (accsi)]

        API --> ENG
        API --> LAYOUT
        API --> OSD
        API --> MM
        ENG --> LEPT
        MM --> HTTP
    end

    subgraph GitHub Traineddata Repositories
        HTTP -->|HTTPS GET| GH1[tessdata_fast]
        HTTP -->|HTTPS GET| GH2[tessdata_best]
        HTTP -->|HTTPS GET| GH3[tessdata / scripts]
    end
```

**Tech Stack:** C++17, C ABI, CMake 3.22+, MSVC `/MT` (Static CRT), WinHTTP, Windows RC, Python 3 (ctypes).  
**Spec:** [docs/superpowers/specs/2026-10-08-tesseract-engine-dll-design.md](file:///d:/projects/c++/tesseract/docs/superpowers/specs/2026-10-08-tesseract-engine-dll-design.md)  

## Global Constraints
- **Zero dynamic runtime dependencies**: Target binary must NOT require `msvcp140.dll`, `vcruntime140.dll`, `libcurl.dll`, or Leptonica DLLs.
- **Single monolithic DLL**: Name must be `tesseract_engine.dll`.
- **Architectures**: Both x64 and x86 supported.
- **Branding**: Company: `accsi`, Product: `Accsi Tesseract OCR Engine`.
- **Build tool**: `build.cmd` auto-detecting Visual Studio.

---

### Task 1: Project Header Interfaces & Version Resource
- Create `include/tesseract_engine.h` with full C ABI declarations, types, error codes, and progress callback prototypes.
- Create `include/include.h` as master include file.
- Create `include/tesseract_engine_cpp.hpp` as modern C++ header-only wrapper.
- Create `version.rc` with Company: "accsi", Version 5.5.0.1, FileDescription, Copyright.

### Task 2: Model Catalog & WinHTTP Downloader
- Create `src/model_catalog_data.h` containing comprehensive models: `tessdata_fast`, `tessdata_best`, `tessdata`, and `script/` models.
- Create `src/downloader_winhttp.cpp` implementing TLS 1.2/1.3 streaming downloads, redirect handling, progress callbacks, and cancel tokens.
- Create `src/model_manager.cpp` handling path resolution, catalog queries, installed model checks, and disk operations.

### Task 3: Core Tesseract & Layout Analysis Engine Implementation
- Create `src/dllmain.cpp` for DLL process attach/detach handling.
- Create `src/engine_api.cpp` implementing:
  - Lifecycle: `tess_create`, `tess_destroy`, `tess_init`, `tess_set_variable`.
  - Image Loading: file, memory buffer, raw pixels.
  - Recognition: text, HOCR, TSV, Box, UNLV, confidence.
  - Layout & Direction: blocks, lines, words, symbols, bboxes, writing direction (LTR/RTL/TTB), line order, deskew angle, OSD script detection.
  - Downloader C-API: `tess_model_download`, `tess_model_download_async`, `tess_model_cancel_download`.

### Task 4: CMake & Auto-Detecting `build.cmd`
- Create `CMakeLists.txt` configuring static CRT (`/MT`), Tesseract and Leptonica static linking, and Windows system libraries.
- Create `build.cmd` with automatic detection of Visual Studio (VS 2022, 2019, 2017, VS 18) using `vswhere.exe` and fallback directory probes, supporting `build.cmd x64`, `build.cmd x86`, and `build.cmd all`.

### Task 5: Python Wrapper & C# P/Invoke Interface
- Create `python/tesseract_engine.py`: comprehensive ctypes wrapper class.
- Create `python/example_ocr.py`: OCR and layout analysis example.
- Create `python/example_download.py`: Model manager & download demonstration.
- Create `csharp/AccsiTesseract.cs`: C# P/Invoke wrapper.

### Task 6: Build, Verification & Testing
- Execute `build.cmd` to compile the DLL.
- Verify binary dependencies using `dumpbin /dependents` (confirming zero external C runtime DLLs).
- Verify model catalog querying and model download.
- Execute OCR test and layout analysis test to confirm functionality.
