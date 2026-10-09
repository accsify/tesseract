# Accsify Tesseract - Tutorials & Documentation
**Company:** accsify  
**Copyright (C) 2026 accsify. All rights reserved.**

Welcome to the official tutorial and example suite for `accsify-tesseract`. This package provides high-performance, thread-safe OCR with zero external runtime dependencies on Windows, full bidirectional (BiDi) multi-language support (Arabic & English), and native WinHTTP model downloading.

---

## Table of Contents
1. [Interactive Scaffolding & Quick Demo](#1-interactive-scaffolding--quick-demo)
2. [Python SDK Usage Guide](#2-python-sdk-usage-guide)
   - [One-Line OCR Extraction](#one-line-ocr-extraction)
   - [OOP Engine Lifecycle (RAII)](#oop-engine-lifecycle-raii)
   - [Multilingual Arabic & English (BiDi) OCR](#multilingual-arabic--english-bidi-ocr)
   - [Hierarchical Layout Analysis & Coordinates](#hierarchical-layout-analysis--coordinates)
   - [In-Memory Image & Buffer OCR](#in-memory-image--buffer-ocr)
   - [Multi-Format Document Exports](#multi-format-document-exports)
   - [Automated Model Management](#automated-model-management)
3. [CLI Tool Usage Guide](#3-cli-tool-usage-guide)
   - [Python CLI (`accsify-tesseract`)](#python-cli-accsify-tesseract)
   - [Native Standalone CLI (`tesseract_cli.exe`)](#native-standalone-cli-tesseract_cliexe)
4. [Tutorial Script Index](#4-tutorial-script-index)

---

## 1. Interactive Scaffolding & Quick Demo

When `accsify-tesseract` is installed via `pip install accsify-tesseract`, you can immediately run an end-to-end demo or copy all tutorial scripts into your current project folder:

```bash
# Run the built-in bilingual OCR demo:
accsify-tesseract demo

# Or copy all tutorial scripts and test images into your current directory:
accsify-tesseract init-examples
```

Or from Python:
```python
from accsify_tesseract.examples import copy_examples, run_demo

# Run the live demo
run_demo()

# Copy tutorial scripts into a local folder
copied_files = copy_examples("./my_ocr_tutorials")
print(f"Copied {len(copied_files)} tutorial files!")
```

---

## 2. Python SDK Usage Guide

### One-Line OCR Extraction
For quick text, JSON, or Python dictionary extraction without boilerplate:

```python
from accsify_tesseract import image_to_string, image_to_json, image_to_dict

# Extract plain text
text = image_to_string("invoice.png", lang="eng")
print(text)

# Extract structured JSON with word bounding boxes
json_data = image_to_json("document.png", lang="eng")

# Extract parsed Python dictionary
data = image_to_dict("document.png", lang="eng")
print("Mean Confidence:", data["mean_confidence"])
```

---

### OOP Engine Lifecycle (RAII)
The `TesseractEngine` class provides full control over the native OCR pipeline with safe RAII resource cleanup:

```python
from accsify_tesseract import TesseractEngine, PageSegMode

# Engine initializes and releases native C++ resources automatically
with TesseractEngine(language="eng") as engine:
    engine.set_page_seg_mode(PageSegMode.AUTO)
    engine.set_image("sample.png")
    engine.recognize()

    print("Recognized Text:")
    print(engine.get_text())
    print(f"Confidence: {engine.get_mean_confidence()}%")
```

---

### Multilingual Arabic & English (BiDi) OCR
Accsify Tesseract natively handles mixed Latin (LTR) and Arabic (RTL) scripts with proper Unicode rendering:

```python
from accsify_tesseract import TesseractEngine, ModelManager, ModelType

# Ensure models are downloaded
for lang in ["eng", "ara"]:
    if not ModelManager.is_installed(lang, ModelType.FAST):
        ModelManager.download(lang, ModelType.FAST)

# Initialize with combined language code
with TesseractEngine(language="ara+eng") as engine:
    engine.set_image("bilingual_receipt.png")
    engine.recognize()

    text = engine.get_text()
    print("Bilingual Output:\n", text)
```

---

### Hierarchical Layout Analysis & Coordinates
Extract blocks, paragraphs, lines, and individual words with exact bounding boxes and writing direction:

```python
from accsify_tesseract import TesseractEngine, PageIteratorLevel, WritingDirection

with TesseractEngine(language="ara+eng") as engine:
    engine.set_image("sample_bilingual_doc.png")
    
    # Run word-level layout analysis
    layout = engine.analyse_layout(level=PageIteratorLevel.WORD)

    for word in layout.words:
        box = word.bbox  # left, top, right, bottom
        is_rtl = (word.writing_direction == WritingDirection.RIGHT_TO_LEFT)
        print(f"Word: {word.text:<20} Conf: {word.confidence:5.1f}% Box: [{box.left},{box.top},{box.right},{box.bottom}] RTL: {is_rtl}")
```

---

### In-Memory Image & Buffer OCR
Pass images directly from `PIL.Image`, raw byte streams, or database BLOBs with zero disk I/O:

```python
from PIL import Image
from accsify_tesseract import TesseractEngine

# 1. From PIL Image instance
pil_img = Image.open("photo.jpg").convert("RGB")
with TesseractEngine(language="eng") as engine:
    engine.set_image(pil_img)
    print(engine.get_text())

# 2. From raw bytes (e.g. downloaded from network or read from DB)
with open("photo.jpg", "rb") as f:
    raw_bytes = f.read()

with TesseractEngine(language="eng") as engine:
    engine.set_image(raw_bytes)
    print(engine.get_text())
```

---

### Multi-Format Document Exports
Export recognized results in all industry-standard formats:

```python
with TesseractEngine(language="eng") as engine:
    engine.set_image("document.png")
    engine.recognize()

    plain_text = engine.get_text()     # Plain UTF-8 text
    hocr_html  = engine.get_hocr()     # HTML with bounding boxes
    tsv_table  = engine.get_tsv()      # TSV spreadsheet format (12 columns)
    box_format = engine.get_box()      # Tesseract character box coordinates
    unlv_text  = engine.get_unlv()     # UNLV format
    json_doc   = engine.get_json()     # Native structured document JSON
```

---

### Automated Model Management
Query the 100+ language online catalog, inspect installed models, and download models via Windows WinHTTP:

```python
from accsify_tesseract import ModelManager, ModelType

# List installed models on disk
installed = ModelManager.list_installed()
print("Installed:", installed)

# Query online catalog
catalog = ModelManager.list_catalog(ModelType.FAST)
for item in catalog[:5]:
    print(f"{item.name}: {item.display_name} ({item.file_size_mb:.1f} MB)")

# Download model with progress hook
def on_progress(name, mtype, dl, total, pct, msg):
    print(f"\rDownloading {name}: {pct:.1f}%", end="")
    return True

ModelManager.download("fra", ModelType.FAST, progress_callback=on_progress)
```

---

## 3. CLI Tool Usage Guide

### Python CLI (`accsify-tesseract`)
The package registers `accsify-tesseract` in your PATH upon `pip install`:

```bash
# Print version and engine details
accsify-tesseract version

# Run basic OCR on an image
accsify-tesseract ocr document.png -l eng

# Run bilingual Arabic & English OCR and save to structured JSON
accsify-tesseract ocr invoice.png -l ara+eng --format json -o invoice.json

# Batch OCR on multiple images to hOCR format
accsify-tesseract ocr page1.png page2.png page3.png -l eng --format hocr

# Inspect document layout (words, bounding boxes, writing direction)
accsify-tesseract layout document.png -l ara+eng

# Detect page orientation and script (requires 'osd' model)
accsify-tesseract osd document.png

# Model catalog & downloads
accsify-tesseract models list
accsify-tesseract models installed
accsify-tesseract models download ara --type fast

# Interactive demo and scaffolding
accsify-tesseract demo
accsify-tesseract init-examples
```

---

### Native Standalone CLI (`tesseract_cli.exe`)
The package also includes the ultra-fast C++ monolithic binary `tesseract_cli.exe`. You can locate it from Python or execute it directly:

```python
from accsify_tesseract import get_native_cli_path

cli_path = get_native_cli_path()
print("Native CLI location:", cli_path)
```

Execute directly from the command prompt:
```bash
# Version info
tesseract_cli version

# List installed models
tesseract_cli models installed

# Run OCR to stdout
tesseract_cli ocr document.png -l eng

# Run bilingual OCR to file
tesseract_cli ocr receipt.png -l ara+eng --format json -o output.json
```

---

## 4. Tutorial Script Index

| Script | Purpose & Demonstrated Features |
|---|---|
| [`01_basic_ocr.py`](01_basic_ocr.py) | Basic OCR, one-line `image_to_string` helper, OOP engine, confidence scoring, auto-provisioning. |
| [`02_multilingual_bidi_ocr.py`](02_multilingual_bidi_ocr.py) | Multilingual Arabic & English recognition (`ara+eng`), per-word writing directions (`RIGHT_TO_LEFT` vs `LEFT_TO_RIGHT`). |
| [`03_layout_and_json.py`](03_layout_and_json.py) | Deep page decomposition into blocks, lines, words, coordinates `[L,T,R,B]`, and JSON export. |
| [`04_batch_and_export_formats.py`](04_batch_and_export_formats.py) | Batch processing and exporting Plain Text, hOCR, TSV (12 columns), Box, UNLV, and JSON. |
| [`05_memory_and_pil_buffer.py`](05_memory_and_pil_buffer.py) | Zero disk I/O OCR directly from `PIL.Image.Image` and in-memory compressed byte buffers. |
| [`06_model_catalog_and_flavors.py`](06_model_catalog_and_flavors.py) | Exploring the catalog, checking installed models, live progress bar, flavor switching (`FAST` vs `BEST`). |
| [`07_cli_tool_integration.py`](07_cli_tool_integration.py) | Locating and executing the native `tesseract_cli.exe` executable directly via Python `subprocess`. |
