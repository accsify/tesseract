"""
Command-Line Interface Module for Accsify Tesseract.
====================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List

from .types import PageSegMode, ModelType, PageIteratorLevel, WritingDirection, TextlineOrder
from .engine import TesseractEngine
from .models import ModelManager


def print_banner():
    print("=====================================================================")
    print("  Accsify Tesseract OCR Python CLI Tool")
    print(f"  Company: accsify | Engine Version: {TesseractEngine.version()}")
    print("=====================================================================")


def progress_printer(model_name: str, model_type: int, downloaded: int, total: int, pct: float, status: str) -> bool:
    bar_width = 35
    pos = int(bar_width * (pct / 100.0))
    bar = "=" * pos + (">" if pos < bar_width else "") + " " * (bar_width - pos - 1)
    dl_mb = downloaded / (1024 * 1024)
    tot_mb = total / (1024 * 1024) if total > 0 else 0.0

    size_str = f"({dl_mb:.2f}/{tot_mb:.2f} MB)" if total > 0 else f"({dl_mb:.2f} MB)"
    print(f"\r[*] {model_name} [{bar[:bar_width]}] {pct:.1f}% {size_str} {status}   ", end="", flush=True)
    if pct >= 100.0:
        print()
    return True


def cmd_ocr(args):
    images = [Path(p) for p in args.images]
    for img in images:
        if not img.exists():
            print(f"[ERROR] Image file not found: {img}")
            return 1

    flavor = ModelType.BEST if args.flavor == "best" else ModelType.FAST
    ModelManager.set_flavor(flavor)

    # Check and auto-download all sub-languages (e.g. "ara+eng")
    sub_langs = [l.strip() for l in args.lang.split("+") if l.strip()]
    for sl in sub_langs:
        if not ModelManager.is_installed(sl, flavor):
            print(f"[*] Model '{sl}' ({flavor.name}) is not installed locally. Downloading automatically...")
            ok = ModelManager.download(sl, flavor, progress_printer)
            if not ok:
                print(f"[ERROR] Failed to download model '{sl}'.")
                return 1

    psm = PageSegMode(args.psm)
    fmt = args.format.lower()
    is_batch = len(images) > 1

    with TesseractEngine(datapath=args.tessdata, language=args.lang, flavor=flavor) as tess:
        tess.set_page_seg_mode(psm)

        batch_results = []
        text_outputs = []

        for idx, img_path in enumerate(images):
            print(f"[*] Processing ({idx + 1}/{len(images)}): {img_path} (Lang: {args.lang}, Flavor: {flavor.name}, PSM: {psm.value})...")
            tess.set_image(img_path)
            tess.recognize()

            mean_conf = tess.get_mean_confidence()
            print(f"    [+] Mean Confidence: {mean_conf}%")

            if fmt == "json":
                structured = tess.get_structured_dict()
                if is_batch:
                    batch_results.append({
                        "image": str(img_path),
                        "result": structured
                    })
                else:
                    batch_results = structured
            elif fmt == "hocr":
                text_outputs.append(tess.get_hocr())
            elif fmt == "tsv":
                text_outputs.append(tess.get_tsv())
            elif fmt == "box":
                text_outputs.append(tess.get_box())
            elif fmt == "unlv":
                text_outputs.append(tess.get_unlv())
            else:
                txt = tess.get_text()
                if is_batch:
                    text_outputs.append(f"=== Image: {img_path} (Confidence: {mean_conf}%) ===\n{txt}")
                else:
                    text_outputs.append(txt)

        if fmt == "json":
            final_output = json.dumps(batch_results, ensure_ascii=False, indent=2)
        else:
            final_output = "\n\n".join(text_outputs)

        if args.output:
            out_p = Path(args.output)
            out_p.write_text(final_output, encoding="utf-8")
            print(f"[OK] Saved output to: {out_p}")
        else:
            print("\n----------------------- Recognized Output -----------------------")
            print(final_output)
            print("-----------------------------------------------------------------")
    return 0


def cmd_layout(args):
    img_path = Path(args.image)
    if not img_path.exists():
        print(f"[ERROR] Image file not found: {img_path}")
        return 1

    with TesseractEngine(datapath=args.tessdata, language=args.lang) as tess:
        tess.set_image(img_path)
        layout = tess.analyse_layout(level=PageIteratorLevel.WORD)

        if args.format == "json":
            print(layout.to_json(indent=2))
            return 0

        print("\n=== Page Layout Analysis: Words, Boxes & Writing Direction ===")
        print(f"{'Text':<30} {'Conf':<10} {'Bounding Box (L,T,R,B)':<25} {'Direction':<15} Order")
        print("-" * 88)

        for el in layout.words:
            if not el.text:
                continue
            dir_str = "Left-to-Right" if el.writing_direction == WritingDirection.LEFT_TO_RIGHT else (
                "Right-to-Left" if el.writing_direction == WritingDirection.RIGHT_TO_LEFT else "Top-to-Bottom"
            )
            order_str = "LTR" if el.textline_order == TextlineOrder.LEFT_TO_RIGHT else (
                "RTL" if el.textline_order == TextlineOrder.RIGHT_TO_LEFT else "TTB"
            )
            b = el.bbox
            box_str = f"[{b.left},{b.top},{b.right},{b.bottom}]"

            print(f"{el.text:<30} {el.confidence:<10.1f} {box_str:<25} {dir_str:<15} {order_str}")
    return 0


def cmd_osd(args):
    img_path = Path(args.image)
    if not img_path.exists():
        print(f"[ERROR] Image file not found: {img_path}")
        return 1

    if not ModelManager.is_installed("osd", ModelType.FAST):
        print("[*] 'osd.traineddata' is not installed locally. Downloading automatically...")
        ModelManager.download("osd", ModelType.FAST, progress_printer)

    with TesseractEngine(datapath=args.tessdata, language="osd") as tess:
        tess.set_page_seg_mode(PageSegMode.OSD_ONLY)
        tess.set_image(img_path)
        res = tess.detect_orientation_and_script()

        if getattr(args, "format", "txt") == "json":
            print(res.to_json(indent=2))
            return 0

        print("\n=== Orientation & Script Detection (OSD) Result ===")
        print(f"  Detected Orientation : {res.orientation_deg} degrees (Confidence: {res.orientation_confidence:.2f})")
        print(f"  Detected Script      : {res.script_name} (Confidence: {res.script_confidence:.2f})")
    return 0


def cmd_models(args):
    sub = args.models_action
    if sub == "list":
        type_filter = None
        if args.type == "fast":
            type_filter = ModelType.FAST
        elif args.type == "best":
            type_filter = ModelType.BEST
        elif args.type == "standard":
            type_filter = ModelType.STANDARD
        elif args.type == "script":
            type_filter = ModelType.SCRIPT

        catalog = ModelManager.list_catalog(type_filter)
        print(f"\nAvailable Models in Catalog ({len(catalog)} entries):")
        print(f"{'Code / Name':<20} {'Display Name':<30} {'Type':<12} {'Size':<12} Installed?")
        print("-" * 81)

        for item in catalog:
            size_str = f"{item.file_size_mb:.1f} MB"
            installed_str = "[YES]" if item.is_installed else " No"
            type_name = item.model_type.name.capitalize()
            print(f"{item.name:<20} {item.display_name:<30} {type_name:<12} {size_str:<12} {installed_str}")

    elif sub == "download":
        m_type = ModelType.FAST
        if args.type == "best":
            m_type = ModelType.BEST
        elif args.type == "standard":
            m_type = ModelType.STANDARD
        elif args.type == "script":
            m_type = ModelType.SCRIPT

        print(f"[*] Downloading model: {args.model_name} ({m_type.name})...")
        ok = ModelManager.download(args.model_name, m_type, progress_printer)
        if ok:
            print("[OK] Download completed successfully.")
        else:
            print("[ERROR] Download failed.")

    elif sub == "installed":
        installed = ModelManager.list_installed()
        cur_path = ModelManager.get_path()
        print(f"\nInstalled Models in: {cur_path} ({len(installed)} installed):")
        for name in installed:
            print(f"  - {name}")

    elif sub == "path":
        if args.set_path:
            ModelManager.set_path(args.set_path)
            print(f"[OK] Tessdata path set to: {args.set_path}")
        print(f"Active Tessdata Directory: {ModelManager.get_path()}")

    return 0


def main():
    parser = argparse.ArgumentParser(description="Accsify Tesseract OCR CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # OCR
    p_ocr = subparsers.add_parser("ocr", help="Run OCR on one or multiple images")
    p_ocr.add_argument("images", nargs="+", help="One or more image paths to process")
    p_ocr.add_argument("-l", "--lang", default="eng", help="OCR language code (e.g. eng, ara, ara+eng, fra)")
    p_ocr.add_argument("--flavor", default="fast", choices=["fast", "best"], help="Model flavor: fast or best (default: fast)")
    p_ocr.add_argument("-o", "--output", help="Write output text or JSON to file")
    p_ocr.add_argument("--format", default="txt", choices=["txt", "json", "hocr", "tsv", "box", "unlv"], help="Output format (default: txt)")
    p_ocr.add_argument("--psm", type=int, default=3, help="Page segmentation mode (default: 3 AUTO)")
    p_ocr.add_argument("--tessdata", help="Custom tessdata directory path")

    # Layout
    p_layout = subparsers.add_parser("layout", help="Inspect layout: words, boxes, writing direction")
    p_layout.add_argument("image", help="Path to input image")
    p_layout.add_argument("-l", "--lang", default="eng", help="OCR language code")
    p_layout.add_argument("--format", default="txt", choices=["txt", "json"], help="Output format (default: txt)")
    p_layout.add_argument("--tessdata", help="Custom tessdata directory path")

    # OSD
    p_osd = subparsers.add_parser("osd", help="Detect orientation and script")
    p_osd.add_argument("image", help="Path to input image")
    p_osd.add_argument("--format", default="txt", choices=["txt", "json"], help="Output format (default: txt)")
    p_osd.add_argument("--tessdata", help="Custom tessdata directory path")

    # Models
    p_models = subparsers.add_parser("models", help="Model catalog and downloader")
    p_m_sub = p_models.add_subparsers(dest="models_action", help="Models sub-action")

    p_m_list = p_m_sub.add_parser("list", help="List catalog models")
    p_m_list.add_argument("--type", choices=["fast", "best", "standard", "script", "all"], default="all")

    p_m_dl = p_m_sub.add_parser("download", help="Download a model")
    p_m_dl.add_argument("model_name", help="Name of model (e.g. eng, ara, script/Arabic)")
    p_m_dl.add_argument("--type", choices=["fast", "best", "standard", "script"], default="fast")

    p_m_inst = p_m_sub.add_parser("installed", help="List installed models")

    p_m_path = p_m_sub.add_parser("path", help="Get or set tessdata path")
    p_m_path.add_argument("--set-path", help="Set active tessdata path")

    # Version
    subparsers.add_parser("version", help="Show engine version")

    # Demo
    subparsers.add_parser("demo", help="Run the built-in bilingual Arabic & English OCR demonstration")

    # Init-examples / Scaffolding
    p_init = subparsers.add_parser("init-examples", help="Copy bundled tutorial scripts and sample images to local folder")
    p_init.add_argument("-d", "--dest", default=".", help="Target destination directory (default: current directory)")

    args = parser.parse_args()
    if not args.command:
        print_banner()
        parser.print_help()
        return 0

    if args.command == "version":
        print_banner()
        return 0
    elif args.command == "demo":
        from .examples import run_demo
        return run_demo()
    elif args.command == "init-examples":
        from .examples import copy_examples
        copied = copy_examples(args.dest)
        print(f"[OK] Successfully copied {len(copied)} tutorial files to: {Path(args.dest).resolve()}")
        for f in copied:
            print(f"  -> {f.name}")
        return 0
    elif args.command == "ocr":
        return cmd_ocr(args)
    elif args.command == "layout":
        return cmd_layout(args)
    elif args.command == "osd":
        return cmd_osd(args)
    elif args.command == "models":
        return cmd_models(args)


if __name__ == "__main__":
    sys.exit(main())
