# Accsify Tesseract OCR Engine - Standalone Monolithic Windows DLL

> **Company:** accsify  
> **Product Version:** 5.5.0.1  
> **Underlying Engine:** Tesseract 5.5.0 & Leptonica 1.84.1  
> **Target Platforms:** Windows x64 (AMD64) & Windows x86 (Win32)  
> **Runtime Dependency:** **ZERO** (Static C/C++ Runtime `/MT` - No Visual C++ Redistributable required)  

---

## 1. Overview & Architecture

**Accsify Tesseract** is an enterprise-grade, standalone single-file dynamic link library (`tesseract_engine.dll`) for Windows that bundles the full Tesseract 5.x OCR engine, Leptonica image processing, embedded image decoders, and a native Windows `WinHTTP` language model manager and downloader.

### Core Distinctions
* **True Single-File Monolithic DLL (`tesseract_engine.dll`)**: Everything is statically compiled into one DLL. You do not need `msvcp140.dll`, `vcruntime140.dll`, `leptonica.dll`, `libpng16.dll`, `zlib.dll`, or `libcurl.dll`.
* **Native Windows WinHTTP Downloader**: Downloads any official Tesseract language model directly from GitHub over HTTPS (TLS 1.2/1.3) with live progress callbacks, cancel tokens, and automatic redirects without third-party network libraries.
* **Complete Layout Analysis & Script Orientation**: Exposes full hierarchical layout (Blocks, Paragraphs, TextLines, Words, Symbols), bounding boxes, confidence scores, textline orders, deskew angles, and writing directions (Left-to-Right, Right-to-Left, Top-to-Bottom).
* **Cross-Language Universal C ABI**: Can be called from C, C++, C#, Python, Rust, Go, Delphi, and any language supporting standard C dynamic loading.
* **Official Modular Python Package**: Comes with a production-grade, object-oriented Python package (`accsify_tesseract`) with typing, dataclasses, context managers, and custom exceptions.
* **Auto-Detecting Visual Studio Build System**: Includes `build.cmd` which automatically locates Visual Studio (2022, 2019, 2017, VS 18) and compiles both 64-bit and 32-bit binaries with one command.

```mermaid
graph TD
    subgraph Client Applications
        PY[Python Package: accsify_tesseract] -->|C ABI| DLL[tesseract_engine.dll]
        CLI[C++ CLI: tesseract_cli.exe] -->|C ABI| DLL
        CS[C# P/Invoke: AccsifyTesseract.cs] -->|C ABI| DLL
        CPP[C++ Client: accsify_tesseract.h] -->|C ABI| DLL
    end

    subgraph "tesseract_engine.dll (/MT Static Monolithic)"
        API[C ABI Export Layer]
        ENG[Tesseract 5.5 LSTM Core]
        LEPT[Leptonica Image Engine]
        STB[Embedded Image Decoders: PNG, JPG, BMP, GIF]
        LAYOUT[Layout & Direction Engine]
        OSD[Orientation & Script Detection]
        MM[Model Manager & Catalog]
        HTTP[WinHTTP Native Downloader]
        RC[version.rc (accsify branding)]

        API --> ENG
        API --> LAYOUT
        API --> OSD
        API --> MM
        ENG --> LEPT
        API --> STB
        MM --> HTTP
    end

    subgraph GitHub Repositories
        HTTP -->|HTTPS| G1[tessdata_fast]
        HTTP -->|HTTPS| G2[tessdata_best]
        HTTP -->|HTTPS| G3[tessdata]
        HTTP -->|HTTPS| G4[script/ models]
    end
```

---

## 2. Directory Layout

```
d:\projects\c++\tesseract\
├── build.cmd                       # Master build script: auto-detects VS, compiles x64 & x86 /MT
├── update_sources.cmd              # Source updater: checks out or upgrades Tesseract/Leptonica
├── CMakeLists.txt                  # Unified CMake configuration
├── version.rc                      # Windows resource file branded for "accsify"
├── dist/                           # Final distribution artifacts ready for deployment
│   ├── x64/
│   │   ├── tesseract_engine.dll    # 64-bit standalone monolithic DLL (3.2 MB)
│   │   ├── tesseract_engine.lib    # 64-bit import library
│   │   └── tesseract_cli.exe       # 64-bit CLI executable
│   ├── x86/
│   │   ├── tesseract_engine.dll    # 32-bit standalone monolithic DLL (2.7 MB)
│   │   ├── tesseract_engine.lib    # 32-bit import library
│   │   └── tesseract_cli.exe       # 32-bit CLI executable
│   └── include/
│       ├── accsify_tesseract.h     # Primary C/C++ master header
│       ├── tesseract_engine.h      # Complete C ABI function prototypes & types
│       ├── tesseract_engine_cpp.hpp# Modern RAII C++ wrapper classes
│       └── include.h               # Normalized header alias
├── include/                        # Source include headers
│   ├── accsify_tesseract.h
│   ├── tesseract_engine.h
│   ├── tesseract_engine_cpp.hpp
│   └── include.h
├── src/                            # Native C++ source files
│   ├── dllmain.cpp                 # DLL entry point
│   ├── engine_api.cpp              # OCR, layout, OSD, text format exports
│   ├── model_manager.cpp           # Path & catalog management
│   ├── downloader_winhttp.cpp      # Native Windows WinHTTP streaming downloader
│   ├── model_catalog_data.h        # 75+ official language & script models catalog
│   ├── cli_main.cpp                # Native C++ CLI implementation
│   ├── stb_image.h                 # Embedded PNG/JPG/BMP decoders
│   └── stb_image_write.h
├── python/                         # Official Python package & tools
│   ├── accsify_tesseract/          # Modular Python package
│   │   ├── __init__.py             # Public exports & image_to_string()
│   │   ├── core.py                 # Low-level ctypes bindings & DLL loader
│   │   ├── types.py                # Enums (PageSegMode, WritingDirection, etc.)
│   │   ├── exceptions.py           # Custom exception hierarchy
│   │   ├── engine.py               # TesseractEngine OOP context manager
│   │   ├── layout.py               # PageLayout, LayoutWord, BoundingBox
│   │   ├── osd.py                  # OrientationScriptResult
│   │   ├── iterator.py             # TesseractIterator cursor
│   │   ├── models.py               # ModelManager & live downloader
│   │   └── cli.py                  # Python CLI implementation
│   ├── tesseract_cli.py            # CLI entrypoint runner
│   ├── tesseract_engine.py         # Backward-compatibility module
│   ├── setup.py                    # pip installable package definition
│   └── examples/
│       ├── ocr_basic.py            # Basic OCR demo
│       ├── layout_and_script.py    # Layout & script direction demo
│       └── download_models.py      # Model download & catalog demo
├── csharp/
│   └── AccsifyTesseract.cs         # Complete C# .NET P/Invoke wrapper
└── deps/                           # Source dependencies
    ├── tesseract/                  # Tesseract OCR 5.5.0 source
    └── leptonica/                  # Leptonica 1.84.1 source
```

---

## 3. How to Build

### Prerequisites
* Windows 7, 8, 10, 11, or Windows Server.
* Visual Studio (2022, 2019, 2017, or VS 18) with C++ Desktop Development tools installed.
* CMake 3.20 or newer and Ninja (Ninja is bundled with Visual Studio and Android SDK).

### One-Click Build (`build.cmd`)
Open a command prompt in the project root:

```cmd
:: Build both 64-bit and 32-bit standalone DLLs and CLIs:
build.cmd

:: Or build specific architecture:
build.cmd x64
build.cmd x86

:: Clean intermediate build folders:
build.cmd clean
```

The script automatically:
1. Detects your installed Visual Studio suite via `vswhere.exe` or standard directories.
2. Initializes `vcvarsall.bat` for the appropriate architecture.
3. Configures CMake under `build\x64\` and `build\x86\`.
4. Compiles with `/MT` (Static C Runtime) and `/O2` optimizations.
5. Packages all final deliverables into `dist\x64\`, `dist\x86\`, and `dist\include\`.

### Upgrading Tesseract Sources (`update_sources.cmd`)
To update or change the underlying Tesseract or Leptonica version:

```cmd
:: Fetch default releases (Tesseract 5.5.0, Leptonica 1.84.1):
update_sources.cmd

:: Or specify custom git tags/branches:
update_sources.cmd 5.5.0 1.84.1
```

---

## 4. Command-Line Interface (CLI)

Both a **native C++ executable** (`dist\x64\tesseract_cli.exe`) and a **Python CLI** (`python python/tesseract_cli.py`) are provided with identical syntax.

### 4.1 Running OCR
```cmd
:: Basic OCR (defaults to language 'eng'):
tesseract_cli.exe ocr scan.png

:: Specify language and output file:
tesseract_cli.exe ocr document.jpg -l fra -o output.txt

:: Choose output format (txt, hocr, tsv, box, unlv):
tesseract_cli.exe ocr page.png --format hocr -o page.hocr

:: Set Page Segmentation Mode (PSM):
tesseract_cli.exe ocr column.png --psm 4
```

### 4.2 Layout & Reading Direction Analysis
Analyzes text blocks, words, bounding boxes `[left, top, right, bottom]`, and writing direction (Left-to-Right, Right-to-Left, Top-to-Bottom):

```cmd
tesseract_cli.exe layout sample.png
```

### 4.3 Orientation & Script Detection (OSD)
Detects page rotation (0°, 90°, 180°, 270°) and written script (Latin, Arabic, Cyrillic, etc.):

```cmd
tesseract_cli.exe osd rotated_page.png
```

### 4.4 Model Management & Live Downloads
```cmd
:: List all official models available online:
tesseract_cli.exe models list

:: Filter catalog by model type:
tesseract_cli.exe models list --type fast
tesseract_cli.exe models list --type best
tesseract_cli.exe models list --type script

:: Download a model with live console progress bar:
tesseract_cli.exe models download ara
tesseract_cli.exe models download script/Arabic
tesseract_cli.exe models download fra --type best

:: List models installed locally on disk:
tesseract_cli.exe models installed

:: Check or set active tessdata directory:
tesseract_cli.exe models path
tesseract_cli.exe models path C:\MyTessData
```

---

## 5. Python API Reference (`accsify_tesseract`)

### 5.1 Installation & Setup
You can either import the package directly from `python/` or install it:

```bash
cd python
pip install -e .
```

### 5.2 Basic OCR (Context Manager)
```python
from accsify_tesseract import TesseractEngine, PageSegMode

# Engine initializes with RAII cleanup
with TesseractEngine(language="eng") as tess:
    tess.set_image("scan.png")
    tess.recognize()

    # Plain text
    text = tess.get_text()
    print("Recognized text:\n", text)

    # Average confidence (0 - 100%)
    print("Confidence:", tess.get_mean_confidence())

    # Formatted document outputs
    hocr_html = tess.get_hocr(page_num=0)
    tsv_table = tess.get_tsv(page_num=0)
```

### 5.3 One-Line Quick OCR
```python
from accsify_tesseract import image_to_string

text = image_to_string("receipt.jpg", lang="eng")
print(text)
```

### 5.4 Layout Analysis & Writing Direction
```python
from accsify_tesseract import TesseractEngine, PageIteratorLevel, WritingDirection

with TesseractEngine(language="eng") as tess:
    tess.set_image("page.png")
    
    # Inspect all words on the page
    layout = tess.analyse_layout(level=PageIteratorLevel.WORD)
    
    for word in layout.words:
        print(f"Word: '{word.text}'")
        print(f"  Confidence: {word.confidence:.1f}%")
        print(f"  Bounding Box: {word.bbox.left}, {word.bbox.top}, {word.bbox.right}, {word.bbox.bottom}")
        print(f"  Direction: {word.writing_direction.name}")  # LEFT_TO_RIGHT, RIGHT_TO_LEFT, TOP_TO_BOTTOM
```

### 5.5 Orientation & Script Detection (OSD)
```python
from accsify_tesseract import TesseractEngine

with TesseractEngine(language="osd") as tess:
    tess.set_image("document.png")
    res = tess.detect_orientation_and_script()
    
    print(f"Orientation: {res.orientation_deg}° (Confidence: {res.orientation_confidence:.2f})")
    print(f"Script: {res.script_name} (Confidence: {res.script_confidence:.2f})")
```

### 5.6 Model Catalog & Streaming Downloader
```python
from accsify_tesseract import ModelManager, ModelType

# 1. Query online catalog
models = ModelManager.list_catalog(ModelType.FAST)
for m in models[:5]:
    print(f"{m.name}: {m.display_name} ({m.file_size_mb:.1f} MB)")

# 2. Check if installed
if not ModelManager.is_installed("ara"):
    # 3. Live download with progress callback
    def on_progress(name, model_type, downloaded, total, pct, status):
        print(f"\rDownloading {name}: {pct:.1f}% ({status})", end="")
        return True  # Return False to cancel download

    ModelManager.download("ara", ModelType.FAST, on_progress)
```

---

## 6. C/C++ API Reference (`include/accsify_tesseract.h`)

All exported functions use `extern "C" __declspec(dllexport) __cdecl`.

### 6.1 Lifecycle & Configuration
```c
// Version info
const char* tess_version(void);

// Instance management
TessEngineHandle tess_create(void);
void tess_destroy(TessEngineHandle handle);

// Initialize engine with datapath (NULL for default ./tessdata) and language
int tess_init(TessEngineHandle handle, const char* datapath, const char* language, int oem_mode);
int tess_is_initialized(TessEngineHandle handle);

// Parameters and PSM
int tess_set_variable(TessEngineHandle handle, const char* name, const char* value);
int tess_get_variable(TessEngineHandle handle, const char* name, char* buffer, int max_len);
void tess_set_page_seg_mode(TessEngineHandle handle, int psm_mode);
int tess_get_page_seg_mode(TessEngineHandle handle);
void tess_set_source_resolution(TessEngineHandle handle, int ppi);
```

### 6.2 Image Loading
```c
// File path (PNG, JPG, BMP, TIFF, WebP, GIF)
int tess_set_image_file(TessEngineHandle handle, const char* filepath);

// Encoded memory buffer
int tess_set_image_bytes(TessEngineHandle handle, const unsigned char* data, size_t length);

// Raw uncompressed pixels
int tess_set_image_raw(TessEngineHandle handle, const unsigned char* image_data,
                       int width, int height, int bytes_per_pixel, int bytes_per_line);
```

### 6.3 Recognition & Outputs
```c
int tess_recognize(TessEngineHandle handle);

// Must be freed with tess_free_text()
char* tess_get_utf8_text(TessEngineHandle handle);
char* tess_get_hocr_text(TessEngineHandle handle, int page_number);
char* tess_get_tsv_text(TessEngineHandle handle, int page_number);
char* tess_get_box_text(TessEngineHandle handle, int page_number);
char* tess_get_unlv_text(TessEngineHandle handle);

int tess_get_mean_confidence(TessEngineHandle handle);
void tess_free_text(char* text);
```

### 6.4 Layout, Direction & Iterators
```c
// OSD Detection
int tess_detect_orientation_script(
    TessEngineHandle handle,
    int* orient_deg, float* orient_conf,
    char* script_name, int script_name_max_len, float* script_conf
);

// Iterators
TessIteratorHandle tess_get_iterator(TessEngineHandle handle);
int tess_iterator_next(TessIteratorHandle iter, int level);
int tess_iterator_is_at_beginning_of(TessIteratorHandle iter, int level);
int tess_iterator_get_bounding_box(TessIteratorHandle iter, int level, int* left, int* top, int* right, int* bottom);
char* tess_iterator_get_text(TessIteratorHandle iter, int level);
float tess_iterator_get_confidence(TessIteratorHandle iter, int level);
int tess_iterator_get_writing_direction(TessIteratorHandle iter, int* direction); // 0=LTR, 1=RTL, 2=TTB
int tess_iterator_get_textline_order(TessIteratorHandle iter, int* order);
int tess_iterator_get_deskew_angle(TessIteratorHandle iter, float* angle);
void tess_iterator_destroy(TessIteratorHandle iter);
```

### 6.5 Model Downloader & Manager
```c
int tess_model_set_path(const char* path);
int tess_model_get_path(char* buffer, int max_len);
int tess_model_get_default_path(char* buffer, int max_len);
int tess_model_is_installed(const char* model_name, int model_type);

// Online catalog
int tess_model_get_catalog_count(int model_type);
int tess_model_get_catalog_item(int model_type, int index, TessModelInfo* out_info);

// WinHTTP download
int tess_model_download(
    const char* model_name,
    int model_type,
    TessDownloadProgressCallback callback,
    void* user_data
);
```

---

## 7. C# .NET Integration (`csharp/AccsifyTesseract.cs`)

Simply copy `csharp/AccsifyTesseract.cs` into your Visual Studio .NET project:

```csharp
using System;
using Accsify.Tesseract;

class Program
{
    static void Main()
    {
        Console.WriteLine($"Engine: {TesseractEngine.Version}");

        // Auto-download model if missing
        if (!ModelManager.IsInstalled("eng"))
        {
            ModelManager.Download("eng", ModelType.Fast, (name, type, dl, total, pct, msg, udata) => {
                Console.Write($"\rDownloading {name}: {pct:F1}%");
                return 0; // 0 to continue
            });
            Console.WriteLine();
        }

        using (var engine = new TesseractEngine(language: "eng"))
        {
            engine.SetImage("document.png");
            engine.Recognize();

            string text = engine.GetText();
            Console.WriteLine($"Text:\n{text}");
            Console.WriteLine($"Confidence: {engine.MeanConfidence}%");
        }
    }
}
```

---

## 8. Model Types Comparison

| Model Type | Repository | Size Per Lang | RAM Usage | Best For |
|---|---|---|---|---|
| `FAST` (`0`) | `tessdata_fast` | 1 – 5 MB | Low (~20 MB) | Real-time OCR, Mobile, Embedded, Low latency |
| `BEST` (`1`) | `tessdata_best` | 15 – 45 MB | Higher (~100 MB) | Maximum accuracy, Archival scans, Complex typography |
| `STANDARD` (`2`) | `tessdata` | 15 – 25 MB | Medium (~50 MB) | Standard compatibility with legacy workflows |
| `SCRIPT` (`3`) | `tessdata_fast/script` | 3 – 12 MB | Medium | Specialized writing scripts (Arabic, Cyrillic, Devanagari, Han, etc.) |

---

## 9. License & Attribution

* **Branding:** Accsify (Copyright (C) 2026 accsify. All rights reserved).
* **Tesseract OCR:** Apache License 2.0 (Google Inc. / Tesseract contributors).
* **Leptonica:** BSD 2-Clause License (Dan Bloomberg).
* **stb_image:** Public Domain / MIT (Sean Barrett).
