# Accsify Tesseract CLI Reference Manual

> **Product:** Accsify Tesseract Standalone CLI  
> **Company:** accsify  
> **Version:** 5.5.0.1  
> **Executable:** `tesseract_cli.exe` (C++ Standalone) & `accsify-tesseract` (Python CLI)  
> **Architecture:** Windows x64 (AMD64) & Windows x86 (Win32)  
> **Runtime Dependencies:** **ZERO** (Static C/C++ Runtime `/MT`)  

---

## 1. Introduction

The **Accsify Tesseract CLI** is a standalone, enterprise-grade command-line tool for performing Optical Character Recognition (OCR), layout hierarchy analysis, orientation/script detection (OSD), and automated language model downloads.

It is available as:
1. **`tesseract_cli.exe`**: Native, compiled Windows binary with zero external dependencies (no MSVC redistributables, no Leptonica DLL, no network libraries).
2. **`accsify-tesseract`**: Official Python command-line utility powered by the monolithic `tesseract_engine.dll`.

Both tools share identical command syntax, argument flags, model storage conventions, and structured JSON output schemas.

---

## 2. Global Command Synopsis

```powershell
# Native C++ CLI:
tesseract_cli.exe <command> [arguments...] [options...]

# Python CLI:
accsify-tesseract <command> [arguments...] [options...]
# or
python -m accsify_tesseract.cli <command> [arguments...] [options...]
```

### Available Sub-Commands

| Sub-Command | Description |
| :--- | :--- |
| `ocr` | Execute OCR on one or multiple images with selectable formats and models |
| `layout` | Inspect geometric layout: words, bounding boxes, directions, deskew angles |
| `osd` | Detect page orientation degrees and writing script |
| `models` | Query catalog, download models with live progress, and manage storage paths |
| `version` | Display engine version, company branding, and build information |

---

## 3. Command: `ocr`

Executes the OCR recognition pipeline on one or more images.

```powershell
tesseract_cli.exe ocr <image1> [image2 ...] [options]
```

### Options

| Flag | Argument | Default | Description |
| :--- | :--- | :--- | :--- |
| `-l`, `--lang` | `<code[+code...]>` | `eng` | Language code (e.g. `eng`, `ara`, `fra`, `ara+eng`, `script/Arabic`) |
| `--flavor` | `fast \| best` | `fast` | Model repository: `fast` (compact ~2MB) or `best` (high-accuracy ~15-40MB) |
| `-o`, `--output` | `<filepath>` | *stdout* | Save recognized text or structured JSON to disk |
| `--format` | `txt \| json \| hocr \| tsv \| box \| unlv` | `txt` | Output document format |
| `--psm` | `<0-13>` | `3` | Page Segmentation Mode (PSM) |
| `--tessdata` | `<directory>` | *DLL dir* | Override active models storage directory path |

---

### Page Segmentation Modes (`--psm`)

| Mode | Name | Description |
| :---: | :--- | :--- |
| **0** | `OSD_ONLY` | Orientation and script detection only |
| **1** | `AUTO_OSD` | Automatic page segmentation with OSD |
| **2** | `AUTO_ONLY` | Automatic page segmentation, no OSD or OCR |
| **3** | `AUTO` | Fully automatic page segmentation (Default) |
| **4** | `SINGLE_COLUMN` | Assume a single column of text of variable sizes |
| **5** | `SINGLE_BLOCK_VERT_TEXT` | Assume a single uniform block of vertically aligned text |
| **6** | `SINGLE_BLOCK` | Assume a single uniform block of text |
| **7** | `SINGLE_LINE` | Treat the image as a single text line |
| **8** | `SINGLE_WORD` | Treat the image as a single word |
| **9** | `CIRCLE_WORD` | Treat the image as a single word in a circle |
| **10** | `SINGLE_CHAR` | Treat the image as a single character |
| **11** | `SPARSE_TEXT` | Find as much text as possible in no particular order |
| **12** | `SPARSE_TEXT_OSD` | Sparse text with orientation and script detection |
| **13** | `RAW_LINE` | Treat the image as a single text line, bypassing hacks |

---

### Output Formats (`--format`)

* **`txt`**: UTF-8 plain text string.
* **`json`**: Structured JSON document containing overall text, mean confidence score, page segmentation mode, and word-level coordinates `[left, top, right, bottom]`, individual confidences, reading directions, and deskew angles.
* **`hocr`**: Standard HOCR HTML representation containing bounding boxes, paragraphs, and words suitable for searchable PDF creation.
* **`tsv`**: Tab-separated values with columns: `level`, `page_num`, `block_num`, `par_num`, `line_num`, `word_num`, `left`, `top`, `width`, `height`, `conf`, `text`.
* **`box`**: Tesseract box character coordinate format (`char left bottom right top page`).
* **`unlv`**: UNLV-compatible output format.

---

### Examples

#### Example 1: Basic OCR
```powershell
tesseract_cli.exe ocr invoice.png
```

#### Example 2: Multi-Language OCR (Arabic + English) with Auto-Download
```powershell
tesseract_cli.exe ocr contract.png -l "ara+eng" --flavor best
```
*If `ara.traineddata` is not present, the CLI automatically downloads it from the official high-accuracy `tessdata_best` repository via native WinHTTP before running recognition.*

#### Example 3: Structured JSON Output to File
```powershell
tesseract_cli.exe ocr document.png --format json -o output.json
```

#### Example 4: Multi-Image Batch Processing
```powershell
tesseract_cli.exe ocr page1.png page2.png page3.png -l eng --format json -o batch_output.json
```

Output format for batch JSON:
```json
[
  {
    "image": "page1.png",
    "result": {
      "text": "Extracted text of page 1...",
      "mean_confidence": 92,
      "psm": 3,
      "words": [
        {
          "text": "Accsify",
          "confidence": 97.2,
          "bbox": [100, 50, 190, 75],
          "direction": "LeftToRight",
          "order": "LTR",
          "deskew_angle": 0.0
        }
      ]
    }
  },
  {
    "image": "page2.png",
    "result": { ... }
  }
]
```

---

## 4. Command: `layout`

Analyzes and displays the geometric layout of an image, showing word bounding boxes, recognition confidence, textline reading orders, and writing directions.

```powershell
tesseract_cli.exe layout <image_path> [-l <lang>]
```

### Example
```powershell
tesseract_cli.exe layout sample.png -l eng
```

Output:
```
=== Page Layout Analysis: Words, Boxes & Writing Direction ===
Text                           Conf       Bounding Box (L,T,R,B)    Direction       Order
------------------------------------------------------------------------------------
Accsify                        98.4       [120,45,230,78]           Left-to-Right   LTR
Tesseract                      96.1       [240,45,350,78]           Left-to-Right   LTR
OCR                            99.0       [360,45,410,78]           Left-to-Right   LTR
```

Writing directions returned:
* `Left-to-Right` (Latin, Cyrillic, Greek)
* `Right-to-Left` (Arabic, Hebrew)
* `Top-to-Bottom` (East Asian vertical)

---

## 5. Command: `osd`

Detects orientation angle (0°, 90°, 180°, 270°) and script type (e.g. Latin, Arabic, Cyrillic, Han, Devanagari).

```powershell
tesseract_cli.exe osd <image_path>
```

*Note: Requires `osd.traineddata`. If missing, the tool automatically downloads it.*

### Example
```powershell
tesseract_cli.exe osd scanned_page.png
```

Output:
```
=== Orientation & Script Detection (OSD) Result ===
  Detected Orientation : 0 degrees (Confidence: 15.25)
  Detected Script      : Latin (Confidence: 24.80)
```

---

## 6. Command: `models`

Provides catalog exploration, disk queries, and live streaming downloads.

### 6.1. List Available Models in Online Catalog
```powershell
# List all models
tesseract_cli.exe models list

# Filter by type: fast, best, standard, script
tesseract_cli.exe models list --type best
```

Output:
```
Available Models in Catalog (75 entries):
Code / Name          Display Name                   Type         Size        Installed?
---------------------------------------------------------------------------------
eng                  English (Fast)                 Fast         3.9 MB      [YES]
ara                  Arabic (Fast)                  Fast         2.3 MB      [YES]
eng                  English (Best)                 Best         14.7 MB     [YES]
ara                  Arabic (Best)                  Best         11.9 MB      No
script/Arabic        Arabic Script                  Script       4.1 MB       No
```

---

### 6.2. Download a Model
```powershell
# Download fast model (default)
tesseract_cli.exe models download fra

# Download best high-accuracy model (stored in tessdata/best/ara.traineddata)
tesseract_cli.exe models download ara --type best

# Download script model
tesseract_cli.exe models download script/Arabic --type script
```

Output displays live visual progress:
```
[*] Downloading model: ara...
[*] ara [==================================>] 100.0% (11.92/11.92 MB) Completed   
[OK] Download completed successfully.
```

---

### 6.3. List Installed Models
```powershell
tesseract_cli.exe models installed
```

Output:
```
Installed Models in: D:\projects\c++\tesseract\bin\x64\tessdata (6 installed):
  - eng
  - ara
  - fast/eng
  - fast/ara
  - best/eng
  - script/Arabic
```

---

### 6.4. Get or Set Tessdata Path
```powershell
# Display active directory path
tesseract_cli.exe models path

# Set new persistent path
tesseract_cli.exe models path "D:\production_models\tessdata"
```

---

## 7. Command: `version`

Displays the engine build information, company branding, and version.

```powershell
tesseract_cli.exe version
```

Output:
```
=====================================================================
  Accsify Tesseract OCR CLI Tool v5.5.0
  Company: accsify | Engine: 5.5.0
=====================================================================
```

---

## 8. Exit Codes

| Code | Meaning |
| :---: | :--- |
| `0` | Success |
| `1` | Error (Missing file, invalid arguments, initialization failure, download abort) |

---

## 9. Performance & Architecture Notes

1. **Zero External Runtime Dependencies**: Built with `/MT` (Static MSVC CRT). Runs cleanly on fresh Windows 10, 11, and Windows Server machines without installing redistributable packages.
2. **WinHTTP Native Streaming**: Uses Windows native `WinHTTP` with streaming chunks (64 KB buffers) for fast, secure downloads over HTTPS directly from official GitHub releases.
3. **Thread Safety**: Engine handles are completely isolated, allowing multi-threaded CLI and server pipelines to process documents concurrently.
