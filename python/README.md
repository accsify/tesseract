# accsify-tesseract

Official high-performance Python package and CLI for the **Accsify Tesseract OCR Engine**.

[![PyPI version](https://img.shields.io/badge/pypi-v1.0.5.1-blue.svg)](https://pypi.org/project/accsify-tesseract/)
[![Python Versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://pypi.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20x64%20%7C%20x86-green.svg)](https://microsoft.com)

---

## 1. Overview

`accsify-tesseract` is a modern, object-oriented Python SDK built on top of the monolithic `tesseract_engine.dll` Windows dynamic link library. It provides thread-safe OCR recognition, 1:1 drop-in `pytesseract` compatibility, automatic background language & OSD model downloading via native Windows WinHTTP, structured document layout hierarchy, zero 0-DPI warning normalization, Pillow preprocessing pipeline, and searchable PDF generation.

### Key Highlights
* **Zero Runtime External Dependencies**: The underlying native engine is statically linked with `/MT` (MSVC C/C++ Static Runtime). No Visual C++ Redistributables, Leptonica, or external runtime DLLs are required.
* **100% Drop-in `pytesseract` Compatibility**: Provides `accsify_tesseract.compat` allowing legacy projects (such as `accsisuite`) to replace classical installed Tesseract with **zero code modifications**.
* **Zero "0 DPI" Warnings**: Native C++ Pix resolution normalization ($\ge 70$, defaulting to 300 DPI) and Pillow DPI extraction completely eliminates legacy `Warning. Invalid resolution 0 dpi. Using 70 instead.` console spam.
* **Automatic OSD Model Downloader**: Detects if `osd.traineddata` is missing and auto-downloads it over HTTPS before running orientation detection, preventing missing model exceptions.
* **Professional Preprocessing Suite**: Built-in Pillow enhancement pipeline (`enhance_for_ocr`) with auto-contrast, unsharp mask sharpening, and Otsu binarization.
* **Advanced Engine Controls**: Built-in Region of Interest (ROI) cropping (`set_rectangle`), character whitelisting & blacklisting, word confidences array, and native searchable PDF generation.
* **Structured JSON & Dictionary Outputs**: Extract full page layout, words, confidences, bounding boxes, textline orders, and writing directions (LTR, RTL, TTB) directly into typed Python dictionaries or JSON.
* **Concurrent Model Flavors**: Download and store both **fast** (`tessdata_fast`) and **best** (`tessdata_best`) models simultaneously in separated subdirectories without file collisions.
* **Multi-Language OCR**: Seamlessly combine languages with `+` (e.g. `ara+eng`), with automatic downloading of missing language components.
* **Multi-Image Batch Processing**: High-throughput processing of image lists with unified structured results via `recognize_batch()`.
* **Universal Image Support**: Directly load file paths (`str`, `Path`), raw encoded bytes (`bytes`, `bytearray`), PIL Images (`PIL.Image`), and NumPy image arrays (OpenCV `ndarray`).

---

## 2. Installation

### From PyPI
```bash
pip install accsify-tesseract
```

### From Wheel Distribution
```bash
# For 64-bit Windows:
pip install dist/accsify_tesseract-1.0.5.1-py3-none-win_amd64.whl

# For 32-bit Windows:
pip install dist/accsify_tesseract-1.0.5.1-py3-none-win32.whl
```

### From Local Source (Editable Development Mode)
```bash
cd d:\projects\c++\tesseract\python
pip install -e .
```

The package automatically discovers and loads `tesseract_engine.dll` from its bundled package lib directory (`lib/x64/` or `lib/x86/`), `dist/`, `build/`, or standard Windows search paths.

---

## 3. Quickstart & One-Liner Helpers

### High-Level One-Liner Functions
```python
import accsify_tesseract as tess

# 1. Plain text OCR
text = tess.image_to_string("invoice.png", lang="eng")
print(text)

# 2. OCR with config flags and Pillow enhancement
text = tess.image_to_string("scanned_doc.png", lang="eng", config="--psm 11", enhance=True)

# 3. Orientation and Script Detection (OSD) - auto-downloads osd.traineddata if missing
osd_text = tess.image_to_osd("rotated_page.png")
print(osd_text)

# 4. Extract character bounding boxes (Box format)
boxes = tess.image_to_boxes("document.png", lang="eng")

# 5. Extract tab-separated values table (TSV format with header)
tsv_data = tess.image_to_data("document.png", lang="eng")

# 6. Extract hOCR HTML markup
hocr_html = tess.image_to_hocr("document.png", lang="eng")

# 7. Generate Searchable PDF directly
tess.image_to_pdf("scanned_page.png", "output_searchable_doc", lang="eng")

# 8. Extract structured JSON string
json_str = tess.image_to_json("document.png", lang="eng")

# 9. Extract structured dictionary with words and bounding boxes
data = tess.image_to_dict("document.png", lang="eng")
print(f"Mean confidence: {data['mean_confidence']}%")
for word in data["words"]:
    print(f"Word: {word['text']}, Box: {word['bbox']}, Conf: {word['confidence']}%")

# 10. Query available installed languages & engine version
print("Installed languages:", tess.get_languages())
print("Engine version:", tess.get_tesseract_version())
```

---

## 4. Drop-in `pytesseract` Replacement

Existing projects using `pytesseract` (such as `accsisuite`) can immediately switch to `accsify-tesseract` without altering any OCR logic or regex parsers:

```python
# Before:
# import pytesseract

# After (Drop-in):
from accsify_tesseract import compat as pytesseract
# Or simply:
# from accsify_tesseract import pytesseract

# 1. Setting tesseract_cmd is supported as a safe no-op:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 2. OSD orientation detection (matches standard Rotate: <angle> regex):
import re
osd_data = pytesseract.image_to_osd("scanned_page.png", config="--psm 0")
rot_match = re.search(r"Rotate:\s*(\d+)", osd_data)
if rot_match:
    angle = int(rot_match.group(1))
    print(f"Detected rotation angle: {angle}°")

# 3. String OCR with custom PSM and variables:
text = pytesseract.image_to_string("document.png", config="--psm 11")

# 4. Multi-language OCR:
text_bilingual = pytesseract.image_to_string("doc.png", lang="ara+eng")

# 5. Bounding boxes & TSV data:
boxes = pytesseract.image_to_boxes("document.png")
tsv_str = pytesseract.image_to_data("document.png", output_type=pytesseract.Output.STRING)
data_dict = pytesseract.image_to_data("document.png", output_type=pytesseract.Output.DICT)

# 6. Languages and version:
languages = pytesseract.get_languages(config="")
version = pytesseract.get_tesseract_version()
```

---

## 5. Image Preprocessing Suite & DPI Normalization

Tesseract performs significantly better when images have clean contrast, sharp character edges, and valid DPI metadata ($\ge 300$). The `accsify_tesseract.preprocessing` module automates this:

```python
from PIL import Image
from accsify_tesseract.preprocessing import enhance_for_ocr, extract_image_dpi
from accsify_tesseract import image_to_string

# Open raw image
img = Image.open("low_contrast_receipt.png")

# 1. Extract resolution from image info
dpi = extract_image_dpi(img)
print("Detected image DPI:", dpi)

# 2. Apply enhancement: auto-contrast, unsharp mask sharpening, optional binarization
enhanced_img = enhance_for_ocr(
    img,
    auto_contrast=True,
    sharpen=True,
    binarize=False,
    max_dimension=4096
)

# 3. OCR on enhanced image with DPI normalization
text = image_to_string(enhanced_img, enhance=True)
print(text)
```

---

## 6. Object-Oriented Engine Interface (`TesseractEngine`)

For advanced pipelines, `TesseractEngine` provides complete control over the native engine via thread-safe RAII context management:

```python
from accsify_tesseract import TesseractEngine, PageSegMode, ModelType

# Open engine with specific language and model flavor
with TesseractEngine(language="eng", flavor=ModelType.FAST) as engine:
    # 1. Configure mode and variables
    engine.set_page_seg_mode(PageSegMode.AUTO)
    engine.set_variable("tessedit_char_whitelist", "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    
    # Or apply standard config string:
    engine.apply_config("--psm 6 -c tessedit_char_whitelist=0123456789")
    
    # 2. Load image (file path, bytes, PIL Image, or OpenCV ndarray)
    engine.set_image("receipt.png", enhance=True)
    
    # 3. Restrict OCR to a bounding rectangle (Region of Interest / ROI)
    engine.set_rectangle(left=50, top=100, width=400, height=80)
    
    # 4. Run recognition
    engine.recognize()
    
    # 5. Retrieve outputs
    roi_text = engine.get_text()
    print("ROI Text:", roi_text)
    
    # 6. Reset ROI to process full image
    engine.clear()
    full_text = engine.get_text()
    
    # 7. Word confidence scores
    confidences = engine.get_all_word_confidences()
    print("Word confidences (0-100):", confidences)
    
    # 8. Generate Searchable PDF
    engine.generate_searchable_pdf("receipt.png", "searchable_receipt")
```

---

## 7. Structured JSON & Layout Hierarchy

`TesseractEngine.get_json()` and `TesseractEngine.get_structured_dict()` return deep structured layout information natively generated by the C++ engine:

```python
with TesseractEngine(language="eng") as engine:
    engine.set_image("sample.png")
    doc = engine.get_structured_dict()
    
    print(f"Total Text: {doc['text']}")
    print(f"Mean Confidence: {doc['mean_confidence']}%")
    print(f"PSM: {doc['psm']}")
    
    for w in doc["words"]:
        print(f"Word: {w['text']:<20} Conf: {w['confidence']:<6.1f} Box: {w['bbox']} Direction: {w['direction']}")
```

### JSON Output Format
```json
{
  "text": "Full extracted UTF-8 document text...",
  "mean_confidence": 94,
  "psm": 3,
  "words": [
    {
      "text": "Accsify",
      "confidence": 98.4,
      "bbox": [120, 45, 230, 78],
      "direction": "LeftToRight",
      "order": "LTR",
      "deskew_angle": 0.00012
    }
  ]
}
```

---

## 8. Multi-Image Batch Processing

Process dozens or hundreds of images in a single session without recreating the engine:

```python
from accsify_tesseract import TesseractEngine

images = ["page1.png", "page2.png", "page3.png"]

with TesseractEngine(language="eng") as engine:
    batch_results = engine.recognize_batch(images)
    
    for res in batch_results:
        print(f"\n--- Result for: {res.image_path} ---")
        print(f"Confidence: {res.mean_confidence}% | Words: {res.words_count}")
        print(res.text[:100], "...")
```

---

## 9. Model Management & WinHTTP Streaming Downloader

Manage and download models directly from official repositories:

```python
from accsify_tesseract import ModelManager, ModelType

# 1. List installed models
installed = ModelManager.get_installed_models()
print("Installed:", [m.name for m in installed])

# 2. Query available catalog models
catalog = ModelManager.list_catalog(ModelType.FAST)
for m in catalog[:5]:
    print(f"{m.name:<15} {m.display_name:<30} {m.file_size_mb:.1f} MB (Installed: {m.is_installed})")

# 3. Live progress callback
def my_progress(name, model_type, downloaded, total, pct, status):
    print(f"\rDownloading {name}: {pct:.1f}% ({downloaded / 1024 / 1024:.2f} MB)", end="")
    return True  # return False to cancel download

# 4. Download fast Arabic model
ModelManager.download("ara", model_type=ModelType.FAST, progress_callback=my_progress)

# 5. Download best Arabic model (stored in tessdata/best/ without overwriting fast!)
ModelManager.download("ara", model_type=ModelType.BEST, progress_callback=my_progress)

# 6. Configure custom storage directory
ModelManager.set_path("D:/my_models/tessdata")
```

---

## 10. Layout Analysis & Geometry

Analyze page geometry across 5 hierarchy levels: `BLOCK`, `PARA`, `TEXTLINE`, `WORD`, `SYMBOL`:

```python
from accsify_tesseract import TesseractEngine, PageIteratorLevel, WritingDirection

with TesseractEngine(language="ara+eng") as engine:
    engine.set_image("mixed_layout.png")
    layout = engine.analyse_layout(level=PageIteratorLevel.WORD)
    
    print(f"Discovered {len(layout.words)} words, {len(layout.lines)} lines")
    
    for word in layout.words:
        b = word.bbox
        is_rtl = word.writing_direction == WritingDirection.RIGHT_TO_LEFT
        dir_label = "RTL (Arabic)" if is_rtl else "LTR (Latin)"
        print(f"[{b.left}, {b.top}, {b.right}, {b.bottom}] {word.text:<25} Conf: {word.confidence:.1f}% Dir: {dir_label}")
```

---

## 11. Command-Line Interface (CLI)

The package provides the `accsify-tesseract` console script:

```bash
# 1. OCR a single image
accsify-tesseract ocr invoice.png -l eng

# 2. Batch OCR multiple images to structured JSON
accsify-tesseract ocr page1.png page2.png page3.png -l eng --format json -o batch_result.json

# 3. Multi-language OCR with high-accuracy 'best' model
accsify-tesseract ocr contract.png -l "ara+eng" --flavor best

# 4. Detailed layout inspection
accsify-tesseract layout document.png -l eng --format json

# 5. Detect page orientation and script
accsify-tesseract osd scanned.png

# 6. List and download models
accsify-tesseract models list --type fast
accsify-tesseract models download ara --type best
accsify-tesseract models installed
accsify-tesseract models path --set-path "D:\tessdata"
```

---

## 12. Exception Hierarchy

```python
from accsify_tesseract import (
    TesseractError,         # Base exception for all errors
    EngineInitError,        # Failed to initialize engine (missing traineddata, invalid path)
    ImageLoadError,         # Image file missing or corrupted
    RecognitionError,       # OCR recognition failure
    ModelDownloadError,     # Network / WinHTTP download failure
    ModelNotFoundError      # Requested model not found in catalog
)
```

---

## 13. License

Distributed under the **MIT License**. Copyright (C) 2026 **accsify**. All rights reserved.
