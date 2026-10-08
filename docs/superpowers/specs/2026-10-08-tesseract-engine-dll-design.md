# Technical Specification: Monolithic Tesseract Engine DLL (`tesseract_engine.dll`)

**Author:** Antigravity  
**Company:** accsi  
**Date:** 2026-10-08  
**Status:** Approved  

---

## 1. Executive Summary

This project delivers a production-grade, self-contained Windows Dynamic Link Library (`tesseract_engine.dll`) encapsulating the full Tesseract OCR 5.x engine, Leptonica image processing, and a built-in WinHTTP model manager and downloader.

The DLL is built with static MSVC C/C++ runtime (`/MT`), ensuring **zero external runtime dependencies** (no `msvcp140.dll`, `vcruntime140.dll`, `libcurl.dll`, or Leptonica DLLs required on target machines). It builds for both 32-bit (x86) and 64-bit (x64) Windows targets via an automated `build.cmd` script that auto-detects installed Visual Studio environments.

---

## 2. Key Architecture & Constraints

| Attribute | Specification |
|---|---|
| **Output DLL** | `tesseract_engine.dll` (Single monolithic file for x64 and x86) |
| **Import Library** | `tesseract_engine.lib` |
| **Master Header** | `include.h` / `tesseract_engine.h` |
| **Runtime Library** | Static Multi-Threaded (`/MT` Release, `/MTd` Debug) - Zero DLL dependencies |
| **Target Architectures** | Windows x64 (AMD64) and Windows x86 (Win32) |
| **Windows Resource** | `version.rc` with Company: `accsi`, FileDescription, ProductVersion, Copyright |
| **Network Engine** | Native Windows `WinHTTP` (`winhttp.lib`) with TLS 1.2/1.3 and proxy support |
| **Languages Supported** | C/C++ (`include.h`), Python (`tesseract_engine.py` ctypes), C# (`AccsiTesseract.cs`), and any C ABI caller |

---

## 3. Directory Structure

```
d:\projects\c++\tesseract\
├── build.cmd                        # Auto-detects Visual Studio, builds x64 & x86 /MT
├── CMakeLists.txt                   # CMake build system configuring static engine & DLL
├── version.rc                       # Windows resource file branded for "accsi"
├── include/
│   ├── include.h                    # Master include header for all C/C++ consumers
│   ├── tesseract_engine.h           # Complete C ABI exports & definitions
│   └── tesseract_engine_cpp.hpp     # Ergonomic C++ RAII wrapper class
├── src/
│   ├── dllmain.cpp                  # DLL entry point (process attach/detach)
│   ├── engine_api.cpp               # Core OCR, layout analysis, iterators, OSD, text formats
│   ├── model_manager.cpp            # Tessdata path management & installed models inspection
│   ├── downloader_winhttp.cpp       # Native WinHTTP download engine with progress callback
│   └── model_catalog_data.h         # Catalog metadata: fast, best, standard, and script models
├── python/
│   ├── tesseract_engine.py          # Full Python ctypes wrapper
│   ├── example_ocr.py               # Complete OCR, layout analysis, & script detection example
│   └── example_download.py          # Interactive model download with progress bar
├── csharp/
│   └── AccsiTesseract.cs            # C# P/Invoke wrapper class
├── bin/
│   ├── x64/                         # Built 64-bit binaries (tesseract_engine.dll, .lib)
│   └── x86/                         # Built 32-bit binaries (tesseract_engine.dll, .lib)
└── docs/
    └── superpowers/specs/           # Design specifications
```

---

## 4. API Specification (`include.h` / `tesseract_engine.h`)

The exported C ABI functions use `__declspec(dllexport)` with `__cdecl` calling convention:

### 4.1 Lifecycle & Configuration
- `TessEngineHandle tess_create(void);`
- `void tess_destroy(TessEngineHandle handle);`
- `int tess_init(TessEngineHandle handle, const char* datapath, const char* language, int oem_mode);`
- `int tess_set_variable(TessEngineHandle handle, const char* name, const char* value);`
- `int tess_get_variable(TessEngineHandle handle, const char* name, char* buffer, int max_len);`
- `void tess_set_page_seg_mode(TessEngineHandle handle, int psm_mode);`
- `int tess_get_page_seg_mode(TessEngineHandle handle);`

### 4.2 Image Processing
- `int tess_set_image_file(TessEngineHandle handle, const char* filename);`
- `int tess_set_image_bytes(TessEngineHandle handle, const unsigned char* data, int length);`
- `int tess_set_image_raw(TessEngineHandle handle, const unsigned char* image_data, int width, int height, int bytes_per_pixel, int bytes_per_line);`
- `void tess_set_source_resolution(TessEngineHandle handle, int ppi);`

### 4.3 Recognition & Formatted Outputs
- `int tess_recognize(TessEngineHandle handle);`
- `char* tess_get_utf8_text(TessEngineHandle handle);`
- `char* tess_get_hocr_text(TessEngineHandle handle, int page_number);`
- `char* tess_get_tsv_text(TessEngineHandle handle, int page_number);`
- `char* tess_get_box_text(TessEngineHandle handle, int page_number);`
- `char* tess_get_unlv_text(TessEngineHandle handle);`
- `int tess_get_mean_confidence(TessEngineHandle handle);`
- `void tess_free_text(char* text);`

### 4.4 Advanced Layout Analysis, Script & Orientation Detection
- `int tess_detect_orientation_script(TessEngineHandle handle, int* orient_deg, float* orient_conf, char* script_name, int script_name_max_len, float* script_conf);`
- `TessPageIteratorHandle tess_analyse_layout(TessEngineHandle handle);`
- `TessResultIteratorHandle tess_get_iterator(TessEngineHandle handle);`
- `int tess_iterator_next(TessIteratorHandle iter, int level);`
- `int tess_iterator_get_bounding_box(TessIteratorHandle iter, int level, int* left, int* top, int* right, int* bottom);`
- `char* tess_iterator_get_text(TessIteratorHandle iter, int level);`
- `float tess_iterator_get_confidence(TessIteratorHandle iter, int level);`
- `int tess_iterator_get_writing_direction(TessIteratorHandle iter, int* direction);` (0=LTR, 1=RTL, 2=TTB)
- `int tess_iterator_get_textline_order(TessIteratorHandle iter, int* order);`
- `int tess_iterator_get_deskew_angle(TessIteratorHandle iter, float* angle);`
- `void tess_iterator_destroy(TessIteratorHandle iter);`

### 4.5 Model Management & WinHTTP Downloader
- `int tess_model_set_path(const char* path);`
- `int tess_model_get_path(char* buffer, int max_len);`
- `int tess_model_get_default_path(char* buffer, int max_len);`
- `int tess_model_is_installed(const char* model_name, int model_type);`
- `int tess_model_get_catalog_count(int model_type);`
- `int tess_model_get_catalog_item(int model_type, int index, TessModelInfo* out_info);`
- `int tess_model_download(const char* model_name, int model_type, TessDownloadProgressCallback callback, void* user_data);`
- `int tess_model_download_async(const char* model_name, int model_type, TessDownloadProgressCallback callback, void* user_data, TessDownloadHandle* out_handle);`
- `int tess_model_cancel_download(TessDownloadHandle handle);`

---

## 5. Model Catalog Details

The built-in catalog supports all official Tesseract repositories:
1. `TESS_MODEL_TYPE_FAST` (`tessdata_fast`): Fast LSTM models (~1–5 MB each), optimized for speed and light memory footprint.
2. `TESS_MODEL_TYPE_BEST` (`tessdata_best`): High-accuracy LSTM models (~15–40 MB each).
3. `TESS_MODEL_TYPE_STANDARD` (`tessdata`): Standard release models.
4. `TESS_MODEL_TYPE_SCRIPT` (`script/` models): Specialized writing script models (`Arabic`, `Cyrillic`, `Devanagari`, `Latin`, `HanS`, `HanT`, `Japanese`, `Hebrew`, etc.).
5. Helper models: `osd.traineddata` (orientation & script detection) and `pdf.ttf`.

---

## 6. Build & Automation (`build.cmd`)

`build.cmd` features:
1. Automated discovery of Visual Studio (via `vswhere.exe` or standard directory probe: 2022, 2019, 2017, VS 18 Community/Enterprise/Professional).
2. Auto-initializes `vcvarsall.bat x64` for 64-bit and `vcvarsall.bat x86` for 32-bit.
3. Configures static runtime `/MT` to eliminate runtime VC redistributable dependencies.
4. Generates both MSVC Visual Studio solution files (`.sln` / `.vcxproj`) and compiles the standalone DLLs via CMake/Ninja/MSBuild.
5. Copies outputs into `bin/x64/` and `bin/x86/`.

---

## 7. Python Wrapper (`tesseract_engine.py`)

- Pure `ctypes` wrapper requiring no external pip packages (uses standard library `ctypes`).
- Dynamic bitness detection: loads `bin/x64/tesseract_engine.dll` on 64-bit Python and `bin/x86/tesseract_engine.dll` on 32-bit Python.
- Provides high-level Pythonic APIs:
  - `TesseractEngine(datapath, language)` context manager.
  - `recognize_file(image_path)` -> string
  - `analyse_layout(image_path)` -> structured hierarchy of `Block`, `Paragraph`, `Line`, `Word`, `Symbol` with bounding boxes, confidences, and writing directions.
  - `detect_orientation_and_script(image_path)` -> `OrientationScriptResult`.
  - `ModelManager` class with `.list_catalog()`, `.is_installed()`, `.download(model_name, progress_fn)`.

---

## 8. Verification & Acceptance Criteria

1. Both `bin/x64/tesseract_engine.dll` and `bin/x86/tesseract_engine.dll` are successfully compiled.
2. Binary inspection via `dumpbin /dependents` verifies **zero** third-party DLL dependencies (only core Windows OS system DLLs: `KERNEL32.dll`, `USER32.dll`, `WINHTTP.dll`, `WS2_32.dll`, `SHLWAPI.dll`).
3. Model catalog queries return valid models for fast, best, and scripts.
4. Model downloader successfully retrieves `osd.traineddata` and `eng.traineddata` with live progress reporting into the tessdata directory.
5. OCR and Layout Analysis successfully recognize text, bounding boxes, writing direction, and script from test images.
6. Python test scripts execute without error.
