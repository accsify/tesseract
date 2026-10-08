/**
 * @file cli_main.cpp
 * @brief Standalone Command-Line Interface (CLI) for Accsify Tesseract OCR Engine.
 * @company accsify
 * @copyright Copyright (C) 2026 accsify. All rights reserved.
 */

#include "accsify_tesseract.h"
#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>
#include <fstream>
#include <cstring>

static void print_banner() {
    std::cout << "=====================================================================\n";
    std::cout << "  Accsify Tesseract OCR CLI Tool v5.5.0\n";
    std::cout << "  Company: accsify | Engine: " << tess_version() << "\n";
    std::cout << "=====================================================================\n";
}

static void print_usage() {
    print_banner();
    std::cout << "Usage:\n";
    std::cout << "  tesseract_cli ocr <image1> [image2 ...] [options]\n";
    std::cout << "      -l, --lang <lang>       Language code (e.g. eng, ara, ara+eng, fra)\n";
    std::cout << "      --flavor <fast|best>    Model flavor: fast (compact) or best (high accuracy)\n";
    std::cout << "      -o, --output <file>     Write recognized text/JSON to file\n";
    std::cout << "      --format <fmt>          Output format: txt, json, hocr, tsv, box, unlv (default: txt)\n";
    std::cout << "      --psm <0-13>            Page segmentation mode (default: 3 AUTO)\n";
    std::cout << "      --tessdata <dir>        Custom tessdata directory path\n\n";
    std::cout << "  tesseract_cli layout <image_path> [options]\n";
    std::cout << "      Inspect layout: blocks, words, bounding boxes, writing directions\n\n";
    std::cout << "  tesseract_cli osd <image_path>\n";
    std::cout << "      Detect page orientation degrees, script and confidences\n\n";
    std::cout << "  tesseract_cli models list [--type <fast|best|standard|script|all>]\n";
    std::cout << "      List available models in online repository catalog\n\n";
    std::cout << "  tesseract_cli models download <model_name> [--type <fast|best|standard|script>]\n";
    std::cout << "      Download traineddata model with live progress bar\n\n";
    std::cout << "  tesseract_cli models installed\n";
    std::cout << "      List all models currently installed on disk\n\n";
    std::cout << "  tesseract_cli models path [new_path]\n";
    std::cout << "      Get or set active tessdata directory path\n\n";
    std::cout << "  tesseract_cli version\n";
    std::cout << "      Print engine version and build info\n";
    std::cout << "=====================================================================\n";
}

static int progress_callback(
    const char* model_name,
    int model_type,
    int64_t bytes_downloaded,
    int64_t total_bytes,
    double percentage,
    const char* status_message,
    void* user_data
) {
    (void)model_type;
    (void)user_data;

    const int bar_width = 35;
    std::cout << "\r[*] " << model_name << " [";
    int pos = static_cast<int>(bar_width * (percentage / 100.0));
    for (int i = 0; i < bar_width; ++i) {
        if (i < pos) std::cout << "=";
        else if (i == pos) std::cout << ">";
        else std::cout << " ";
    }
    std::cout << "] " << std::fixed << std::setprecision(1) << percentage << "% ";

    double dl_mb = (double)bytes_downloaded / (1024.0 * 1024.0);
    if (total_bytes > 0) {
        double tot_mb = (double)total_bytes / (1024.0 * 1024.0);
        std::cout << "(" << std::fixed << std::setprecision(2) << dl_mb << "/" << tot_mb << " MB) ";
    } else {
        std::cout << "(" << std::fixed << std::setprecision(2) << dl_mb << " MB) ";
    }
    std::cout << status_message << "   " << std::flush;

    if (percentage >= 100.0) {
        std::cout << "\n";
    }
    return 0;
}

int handle_ocr(int argc, char* argv[]) {
    std::vector<std::string> image_paths;
    std::string lang = "eng";
    std::string output_file = "";
    std::string format = "txt";
    std::string custom_tessdata = "";
    std::string flavor_str = "fast";
    int psm = 3;

    for (int i = 2; i < argc; ++i) {
        std::string arg = argv[i];
        if ((arg == "-l" || arg == "--lang") && i + 1 < argc) {
            lang = argv[++i];
        } else if ((arg == "-o" || arg == "--output") && i + 1 < argc) {
            output_file = argv[++i];
        } else if ((arg == "--format") && i + 1 < argc) {
            format = argv[++i];
        } else if ((arg == "--psm") && i + 1 < argc) {
            psm = std::stoi(argv[++i]);
        } else if ((arg == "--tessdata") && i + 1 < argc) {
            custom_tessdata = argv[++i];
        } else if ((arg == "--flavor" || arg == "--type") && i + 1 < argc) {
            flavor_str = argv[++i];
        } else if (arg.rfind("-", 0) != 0) {
            image_paths.push_back(arg);
        }
    }

    if (image_paths.empty()) {
        std::cerr << "[ERROR] Missing input image path(s) for OCR command.\n";
        print_usage();
        return 1;
    }

    if (!custom_tessdata.empty()) {
        tess_model_set_path(custom_tessdata.c_str());
    }

    int model_flavor = (flavor_str == "best") ? TESS_MODEL_TYPE_BEST :
                       ((flavor_str == "standard") ? TESS_MODEL_TYPE_STANDARD :
                       ((flavor_str == "script") ? TESS_MODEL_TYPE_SCRIPT : TESS_MODEL_TYPE_FAST));
    tess_model_set_flavor(model_flavor);

    // Split languages by '+' and verify each one is installed (e.g. "ara+eng")
    std::vector<std::string> sub_langs;
    {
        std::stringstream ss(lang);
        std::string token;
        while (std::getline(ss, token, '+')) {
            if (!token.empty()) sub_langs.push_back(token);
        }
    }

    for (const auto& sl : sub_langs) {
        if (!tess_model_is_installed(sl.c_str(), model_flavor)) {
            std::cout << "[INFO] Model '" << sl << "' (" << flavor_str << ") is not installed. Downloading automatically...\n";
            int dl_res = tess_model_download(sl.c_str(), model_flavor, progress_callback, nullptr);
            if (dl_res != 0) {
                std::cerr << "[ERROR] Failed to download model '" << sl << "'.\n";
                return 1;
            }
        }
    }

    TessEngineHandle eng = tess_create();
    if (!eng) {
        std::cerr << "[ERROR] Failed to allocate engine handle.\n";
        return 1;
    }

    int init_res = tess_init(eng, custom_tessdata.empty() ? nullptr : custom_tessdata.c_str(), lang.c_str(), TESS_OEM_DEFAULT);
    if (init_res != 0) {
        char current_path[512] = {0};
        tess_model_get_path(current_path, sizeof(current_path));
        std::cerr << "[ERROR] Failed to initialize Tesseract engine with language '" << lang << "'.\n";
        std::cerr << "        Active tessdata directory: " << current_path << "\n";
        tess_destroy(eng);
        return 1;
    }

    tess_set_page_seg_mode(eng, psm);

    std::ostringstream combined_output;
    bool is_batch = (image_paths.size() > 1);

    if (format == "json" && is_batch) {
        combined_output << "[\n";
    }

    for (size_t idx = 0; idx < image_paths.size(); ++idx) {
        const std::string& img_path = image_paths[idx];
        if (tess_set_image_file(eng, img_path.c_str()) != 0) {
            std::cerr << "[ERROR] Failed to load image: " << img_path << "\n";
            continue;
        }

        std::cout << "[*] Processing (" << (idx + 1) << "/" << image_paths.size() << "): "
                  << img_path << " (Lang: " << lang << ", Flavor: " << flavor_str << ", PSM: " << psm << ")...\n";
        tess_recognize(eng);

        char* text_ptr = nullptr;
        if (format == "json") {
            text_ptr = tess_get_json_text(eng);
        } else if (format == "hocr") {
            text_ptr = tess_get_hocr_text(eng, 0);
        } else if (format == "tsv") {
            text_ptr = tess_get_tsv_text(eng, 0);
        } else if (format == "box") {
            text_ptr = tess_get_box_text(eng, 0);
        } else if (format == "unlv") {
            text_ptr = tess_get_unlv_text(eng);
        } else {
            text_ptr = tess_get_utf8_text(eng);
        }

        std::string page_text = text_ptr ? text_ptr : "";
        if (text_ptr) tess_free_text(text_ptr);

        int mean_conf = tess_get_mean_confidence(eng);
        std::cout << "    [+] Mean Confidence: " << mean_conf << "%\n";

        if (format == "json" && is_batch) {
            if (idx > 0) combined_output << ",\n";
            // Prepend image path into the JSON block
            combined_output << "  {\n    \"image\": \"" << img_path << "\",\n    \"result\": " << page_text << "\n  }";
        } else if (is_batch && format == "txt") {
            combined_output << "=== Image: " << img_path << " (Confidence: " << mean_conf << "%) ===\n";
            combined_output << page_text << "\n\n";
        } else {
            combined_output << page_text;
        }
    }

    if (format == "json" && is_batch) {
        combined_output << "\n]";
    }

    std::string final_result = combined_output.str();

    if (!output_file.empty()) {
        std::ofstream out(output_file);
        if (out.is_open()) {
            out << final_result;
            std::cout << "[OK] Recognized result successfully saved to: " << output_file << "\n";
        } else {
            std::cerr << "[ERROR] Cannot write to output file: " << output_file << "\n";
        }
    } else {
        std::cout << "\n----------------------- Recognized Output -----------------------\n";
        std::cout << final_result << "\n";
        std::cout << "-----------------------------------------------------------------\n";
    }

    tess_destroy(eng);
    return 0;
}

int handle_layout(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "[ERROR] Missing image path for layout analysis.\n";
        return 1;
    }

    std::string image_path = argv[2];
    std::string lang = "eng";
    for (int i = 3; i < argc; ++i) {
        std::string arg = argv[i];
        if ((arg == "-l" || arg == "--lang") && i + 1 < argc) {
            lang = argv[++i];
        }
    }

    TessEngineHandle eng = tess_create();
    if (tess_init(eng, nullptr, lang.c_str(), TESS_OEM_DEFAULT) != 0) {
        std::cerr << "[ERROR] Failed to initialize engine for layout analysis with language: " << lang << "\n";
        tess_destroy(eng);
        return 1;
    }

    if (tess_set_image_file(eng, image_path.c_str()) != 0) {
        std::cerr << "[ERROR] Failed to load image: " << image_path << "\n";
        tess_destroy(eng);
        return 1;
    }

    tess_recognize(eng);
    TessIteratorHandle iter = tess_get_iterator(eng);
    if (!iter) {
        std::cerr << "[ERROR] No layout elements found.\n";
        tess_destroy(eng);
        return 1;
    }

    std::cout << "\n=== Page Layout Analysis: Words, Boxes & Writing Direction ===\n";
    std::cout << std::left << std::setw(30) << "Text"
              << std::setw(10) << "Conf"
              << std::setw(25) << "Bounding Box (L,T,R,B)"
              << std::setw(15) << "Direction"
              << "Order\n";
    std::cout << "------------------------------------------------------------------------------------\n";

    do {
        char* txt = tess_iterator_get_text(iter, TESS_LEVEL_WORD);
        float conf = tess_iterator_get_confidence(iter, TESS_LEVEL_WORD);
        int l, t, r, b;
        tess_iterator_get_bounding_box(iter, TESS_LEVEL_WORD, &l, &t, &r, &b);
        int wdir = 0, torder = 0;
        tess_iterator_get_writing_direction(iter, &wdir);
        tess_iterator_get_textline_order(iter, &torder);

        std::string dir_str = (wdir == 0) ? "Left-to-Right" : ((wdir == 1) ? "Right-to-Left" : "Top-to-Bottom");
        std::string order_str = (torder == 0) ? "LTR" : ((torder == 1) ? "RTL" : "TTB");
        std::string box_str = "[" + std::to_string(l) + "," + std::to_string(t) + "," + std::to_string(r) + "," + std::to_string(b) + "]";

        if (txt && strlen(txt) > 0) {
            std::cout << std::left << std::setw(30) << (txt ? txt : "")
                      << std::fixed << std::setprecision(1) << std::setw(10) << conf
                      << std::setw(25) << box_str
                      << std::setw(15) << dir_str
                      << order_str << "\n";
        }
        if (txt) tess_free_text(txt);
    } while (tess_iterator_next(iter, TESS_LEVEL_WORD));

    tess_iterator_destroy(iter);
    tess_destroy(eng);
    return 0;
}

int handle_osd(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "[ERROR] Missing image path for OSD.\n";
        return 1;
    }

    std::string image_path = argv[2];
    TessEngineHandle eng = tess_create();
    if (tess_init(eng, nullptr, "osd", TESS_OEM_DEFAULT) != 0) {
        if (!tess_model_is_installed("osd", TESS_MODEL_TYPE_FAST)) {
            std::cout << "[INFO] 'osd.traineddata' is not installed. Downloading automatically...\n";
            tess_model_download("osd", TESS_MODEL_TYPE_FAST, progress_callback, nullptr);
            tess_init(eng, nullptr, "osd", TESS_OEM_DEFAULT);
        }
    }

    tess_set_page_seg_mode(eng, TESS_PSM_OSD_ONLY);
    if (tess_set_image_file(eng, image_path.c_str()) != 0) {
        std::cerr << "[ERROR] Failed to load image: " << image_path << "\n";
        tess_destroy(eng);
        return 1;
    }

    int orient_deg = 0;
    float orient_conf = 0.0f;
    char script_name[64] = {0};
    float script_conf = 0.0f;

    if (tess_detect_orientation_script(eng, &orient_deg, &orient_conf, script_name, sizeof(script_name), &script_conf) == 0) {
        std::cout << "\n=== Orientation & Script Detection (OSD) Result ===\n";
        std::cout << "  Detected Orientation : " << orient_deg << " degrees (Confidence: " << orient_conf << ")\n";
        std::cout << "  Detected Script      : " << script_name << " (Confidence: " << script_conf << ")\n";
    } else {
        std::cerr << "[ERROR] Failed to detect orientation and script.\n";
    }

    tess_destroy(eng);
    return 0;
}

int handle_models(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "[ERROR] Missing models sub-command: list, download, installed, path\n";
        return 1;
    }

    std::string sub = argv[2];
    if (sub == "list") {
        int filter_type = -1;
        if (argc >= 5 && std::string(argv[3]) == "--type") {
            std::string t = argv[4];
            if (t == "fast") filter_type = TESS_MODEL_TYPE_FAST;
            else if (t == "best") filter_type = TESS_MODEL_TYPE_BEST;
            else if (t == "standard") filter_type = TESS_MODEL_TYPE_STANDARD;
            else if (t == "script") filter_type = TESS_MODEL_TYPE_SCRIPT;
        }

        int count = tess_model_get_catalog_count(filter_type);
        std::cout << "\nAvailable Models in Catalog (" << count << " entries):\n";
        std::cout << std::left << std::setw(20) << "Code / Name"
                  << std::setw(30) << "Display Name"
                  << std::setw(12) << "Type"
                  << std::setw(12) << "Size"
                  << "Installed?\n";
        std::cout << "---------------------------------------------------------------------------------\n";

        TessModelInfo info;
        for (int i = 0; i < count; ++i) {
            if (tess_model_get_catalog_item(filter_type, i, &info) == 0) {
                std::string type_name = "Fast";
                if (info.model_type == TESS_MODEL_TYPE_BEST) type_name = "Best";
                else if (info.model_type == TESS_MODEL_TYPE_STANDARD) type_name = "Standard";
                else if (info.model_type == TESS_MODEL_TYPE_SCRIPT) type_name = "Script";

                double mb = (double)info.file_size / (1024.0 * 1024.0);
                std::stringstream ss;
                ss << std::fixed << std::setprecision(1) << mb << " MB";

                std::cout << std::left << std::setw(20) << info.name
                          << std::setw(30) << info.display_name
                          << std::setw(12) << type_name
                          << std::setw(12) << ss.str()
                          << (info.is_installed ? "[YES]" : " No") << "\n";
            }
        }
        return 0;
    } else if (sub == "download") {
        if (argc < 4) {
            std::cerr << "[ERROR] Specify model name to download. e.g.: tesseract_cli models download ara\n";
            return 1;
        }
        std::string model_name = argv[3];
        int m_type = TESS_MODEL_TYPE_FAST;
        if (argc >= 6 && std::string(argv[4]) == "--type") {
            std::string t = argv[5];
            if (t == "best") m_type = TESS_MODEL_TYPE_BEST;
            else if (t == "standard") m_type = TESS_MODEL_TYPE_STANDARD;
            else if (t == "script") m_type = TESS_MODEL_TYPE_SCRIPT;
        }

        std::cout << "[*] Downloading model: " << model_name << "...\n";
        int res = tess_model_download(model_name.c_str(), m_type, progress_callback, nullptr);
        if (res == 0) {
            std::cout << "[OK] Download completed successfully.\n";
        } else {
            std::cerr << "[ERROR] Download failed or aborted.\n";
            return 1;
        }
        return 0;
    } else if (sub == "installed") {
        int count = tess_model_get_installed_count();
        char cur_path[512] = {0};
        tess_model_get_path(cur_path, sizeof(cur_path));
        std::cout << "\nInstalled Models in: " << cur_path << " (" << count << " installed):\n";
        char name[128] = {0};
        for (int i = 0; i < count; ++i) {
            if (tess_model_get_installed_item(i, name, sizeof(name)) == 0) {
                std::cout << "  - " << name << "\n";
            }
        }
        return 0;
    } else if (sub == "path") {
        if (argc >= 4) {
            tess_model_set_path(argv[3]);
            std::cout << "[OK] Tessdata path set to: " << argv[3] << "\n";
        }
        char p[512] = {0};
        tess_model_get_path(p, sizeof(p));
        std::cout << "Active Tessdata Directory: " << p << "\n";
        return 0;
    }

    std::cerr << "[ERROR] Unknown models command: " << sub << "\n";
    return 1;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        print_usage();
        return 0;
    }

    std::string cmd = argv[1];
    if (cmd == "ocr") {
        return handle_ocr(argc, argv);
    } else if (cmd == "layout") {
        return handle_layout(argc, argv);
    } else if (cmd == "osd") {
        return handle_osd(argc, argv);
    } else if (cmd == "models") {
        return handle_models(argc, argv);
    } else if (cmd == "version" || cmd == "-v" || cmd == "--version") {
        print_banner();
        return 0;
    } else {
        std::cerr << "[ERROR] Unknown command: " << cmd << "\n\n";
        print_usage();
        return 1;
    }
}
