/**
 * @file engine_api.cpp
 * @brief Complete C ABI implementation for Tesseract OCR, Layout Analysis, OSD, and Formatting.
 * @company accsify
 * @copyright Copyright (C) 2026 accsify. All rights reserved.
 */

#include "tesseract_engine.h"

// Define STB image loader
#define STB_IMAGE_IMPLEMENTATION
#define STBI_NO_STDIO
#include "stb_image.h"

// Leptonica headers
#include <allheaders.h>

// Tesseract C++ API headers
#include <tesseract/baseapi.h>
#include <tesseract/pageiterator.h>
#include <tesseract/resultiterator.h>
#include <tesseract/publictypes.h>
#include <tesseract/version.h>
#include <tesseract/renderer.h>

#include <windows.h>
#include <string>
#include <vector>
#include <memory>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>

namespace accsify {

struct EngineContext {
    tesseract::TessBaseAPI api;
    bool initialized = false;
    std::vector<unsigned char> raw_image_pixels;
    int image_w = 0;
    int image_h = 0;
    int image_bpp = 0;
    Pix* current_pix = nullptr;

    void cleanup_image() {
        if (current_pix) {
            pixDestroy(&current_pix);
            current_pix = nullptr;
        }
        raw_image_pixels.clear();
        image_w = 0;
        image_h = 0;
        image_bpp = 0;
    }

    ~EngineContext() {
        cleanup_image();
        if (initialized) {
            api.End();
            initialized = false;
        }
    }
};

struct IteratorContext {
    tesseract::PageIterator* page_iter = nullptr;
    tesseract::ResultIterator* res_iter = nullptr;
    bool is_result = false;

    ~IteratorContext() {
        if (res_iter) {
            delete res_iter;
            res_iter = nullptr;
            page_iter = nullptr;
        } else if (page_iter) {
            delete page_iter;
            page_iter = nullptr;
        }
    }
};

static char* duplicate_string(const char* src) {
    if (!src) return nullptr;
    size_t len = strlen(src);
    char* copy = (char*)malloc(len + 1);
    if (copy) {
        memcpy(copy, src, len + 1);
    }
    return copy;
}

static std::string escape_json_string(const std::string& input) {
    std::string out;
    out.reserve(input.size() + 16);
    for (char c : input) {
        switch (c) {
            case '"':  out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\b': out += "\\b"; break;
            case '\f': out += "\\f"; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default:
                if (static_cast<unsigned char>(c) < 0x20) {
                    char hex[8];
                    snprintf(hex, sizeof(hex), "\\u%04x", static_cast<unsigned char>(c));
                    out += hex;
                } else {
                    out += c;
                }
                break;
        }
    }
    return out;
}

} // namespace accsify

using namespace accsify;

extern "C" {

TESS_API const char* TESS_CALL tess_version(void) {
    return tesseract::TessBaseAPI::Version();
}

TESS_API TessEngineHandle TESS_CALL tess_create(void) {
    setMsgSeverity(L_SEVERITY_NONE);
    auto ctx = new (std::nothrow) EngineContext();
    return reinterpret_cast<TessEngineHandle>(ctx);
}

TESS_API void TESS_CALL tess_destroy(TessEngineHandle handle) {
    if (!handle) return;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    delete ctx;
}

TESS_API int TESS_CALL tess_init(TessEngineHandle handle, const char* datapath, const char* language, int oem_mode) {
    if (!handle) return -1;
    auto ctx = reinterpret_cast<EngineContext*>(handle);

    std::string path;
    if (datapath && datapath[0] != '\0') {
        path = datapath;
    } else {
        char base_buf[512] = {0};
        tess_model_get_path(base_buf, sizeof(base_buf));
        path = base_buf;

        // Extract primary language in case of combination e.g. "ara+eng" -> "ara"
        const char* l_str = (language && language[0] != '\0') ? language : "eng";
        std::string primary_lang = l_str;
        size_t plus_pos = primary_lang.find('+');
        if (plus_pos != std::string::npos) {
            primary_lang = primary_lang.substr(0, plus_pos);
        }

        // Check if model file exists in current flavor path
        int active_flavor = tess_model_get_flavor();
        char flavor_buf[512] = {0};
        tess_model_get_flavor_path(active_flavor, flavor_buf, sizeof(flavor_buf));
        std::string candidate = std::string(flavor_buf) + "\\" + primary_lang + ".traineddata";
        DWORD attr = GetFileAttributesA(candidate.c_str());
        if (attr != INVALID_FILE_ATTRIBUTES && !(attr & FILE_ATTRIBUTE_DIRECTORY)) {
            path = flavor_buf;
        } else {
            // Check other flavors
            for (int f = 0; f <= 3; ++f) {
                char f_buf[512] = {0};
                tess_model_get_flavor_path(f, f_buf, sizeof(f_buf));
                std::string f_cand = std::string(f_buf) + "\\" + primary_lang + ".traineddata";
                DWORD f_attr = GetFileAttributesA(f_cand.c_str());
                if (f_attr != INVALID_FILE_ATTRIBUTES && !(f_attr & FILE_ATTRIBUTE_DIRECTORY)) {
                    path = f_buf;
                    break;
                }
            }
        }
    }

    const char* lang = (language && language[0] != '\0') ? language : "eng";
    tesseract::OcrEngineMode oem = static_cast<tesseract::OcrEngineMode>(oem_mode);

    int res = ctx->api.Init(path.c_str(), lang, oem);
    if (res == 0) {
        ctx->initialized = true;
    }
    return res;
}

TESS_API int TESS_CALL tess_is_initialized(TessEngineHandle handle) {
    if (!handle) return 0;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    return ctx->initialized ? 1 : 0;
}

TESS_API int TESS_CALL tess_set_variable(TessEngineHandle handle, const char* name, const char* value) {
    if (!handle || !name || !value) return 0;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    return ctx->api.SetVariable(name, value) ? 1 : 0;
}

TESS_API int TESS_CALL tess_get_variable(TessEngineHandle handle, const char* name, char* buffer, int max_len) {
    if (!handle || !name || !buffer || max_len <= 0) return 0;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    const char* val = ctx->api.GetStringVariable(name);
    if (val) {
        strncpy_s(buffer, max_len, val, _TRUNCATE);
        return 1;
    }
    return 0;
}

TESS_API void TESS_CALL tess_set_page_seg_mode(TessEngineHandle handle, int psm_mode) {
    if (!handle) return;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    ctx->api.SetPageSegMode(static_cast<tesseract::PageSegMode>(psm_mode));
}

TESS_API int TESS_CALL tess_get_page_seg_mode(TessEngineHandle handle) {
    if (!handle) return 0;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    return static_cast<int>(ctx->api.GetPageSegMode());
}

TESS_API void TESS_CALL tess_set_source_resolution(TessEngineHandle handle, int ppi) {
    if (!handle) return;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    try {
        if (ctx->current_pix) {
            pixSetResolution(ctx->current_pix, ppi, ppi);
        }
        ctx->api.SetSourceResolution(ppi);
        ctx->api.SetVariable("user_defined_dpi", std::to_string(ppi).c_str());
    } catch (...) {}
}

TESS_API int TESS_CALL tess_get_source_resolution(TessEngineHandle handle) {
    if (!handle) return 0;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    try {
        return ctx->api.GetSourceYResolution();
    } catch (...) {
        return 0;
    }
}

TESS_API void TESS_CALL tess_set_rectangle(TessEngineHandle handle, int left, int top, int width, int height) {
    if (!handle) return;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    try {
        ctx->api.SetRectangle(left, top, width, height);
    } catch (...) {}
}

TESS_API void TESS_CALL tess_clear(TessEngineHandle handle) {
    if (!handle) return;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    try {
        ctx->cleanup_image();
        ctx->api.Clear();
    } catch (...) {}
}

TESS_API int TESS_CALL tess_set_char_whitelist(TessEngineHandle handle, const char* whitelist) {
    if (!handle) return 0;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    try {
        const char* val = whitelist ? whitelist : "";
        return ctx->api.SetVariable("tessedit_char_whitelist", val) ? 1 : 0;
    } catch (...) {
        return 0;
    }
}

TESS_API int TESS_CALL tess_set_char_blacklist(TessEngineHandle handle, const char* blacklist) {
    if (!handle) return 0;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    try {
        const char* val = blacklist ? blacklist : "";
        return ctx->api.SetVariable("tessedit_char_blacklist", val) ? 1 : 0;
    } catch (...) {
        return 0;
    }
}

static Pix* raw_to_pix(const unsigned char* imagedata, int width, int height, int bytes_per_pixel, int bytes_per_line, int dpi = 300) {
    if (!imagedata || width <= 0 || height <= 0 || bytes_per_pixel <= 0) return nullptr;
    int bpp = bytes_per_pixel * 8;
    if (bpp == 0) bpp = 1;
    Pix* pix = pixCreate(width, height, bpp == 24 ? 32 : bpp);
    if (!pix) return nullptr;
    l_uint32 *data = pixGetData(pix);
    int wpl = pixGetWpl(pix);
    switch (bpp) {
        case 1:
            for (int y = 0; y < height; ++y) {
                l_uint32* row_data = data + y * wpl;
                const unsigned char* src_line = imagedata + y * bytes_per_line;
                for (int x = 0; x < width; ++x) {
                    if (src_line[x / 8] & (0x80 >> (x % 8))) {
                        CLEAR_DATA_BIT(row_data, x);
                    } else {
                        SET_DATA_BIT(row_data, x);
                    }
                }
            }
            break;
        case 8:
            for (int y = 0; y < height; ++y) {
                l_uint32* row_data = data + y * wpl;
                const unsigned char* src_line = imagedata + y * bytes_per_line;
                for (int x = 0; x < width; ++x) {
                    SET_DATA_BYTE(row_data, x, src_line[x]);
                }
            }
            break;
        case 24:
            for (int y = 0; y < height; ++y) {
                l_uint32* row_data = data + y * wpl;
                const unsigned char* src_line = imagedata + y * bytes_per_line;
                for (int x = 0; x < width; ++x) {
                    SET_DATA_BYTE(row_data + x, COLOR_RED, src_line[3 * x]);
                    SET_DATA_BYTE(row_data + x, COLOR_GREEN, src_line[3 * x + 1]);
                    SET_DATA_BYTE(row_data + x, COLOR_BLUE, src_line[3 * x + 2]);
                }
            }
            break;
        case 32:
            for (int y = 0; y < height; ++y) {
                l_uint32* row_data = data + y * wpl;
                const unsigned char* src_line = imagedata + y * bytes_per_line;
                for (int x = 0; x < width; ++x) {
                    row_data[x] = (static_cast<l_uint32>(src_line[x * 4]) << 24) |
                                  (static_cast<l_uint32>(src_line[x * 4 + 1]) << 16) |
                                  (static_cast<l_uint32>(src_line[x * 4 + 2]) << 8) |
                                  static_cast<l_uint32>(src_line[x * 4 + 3]);
                }
            }
            break;
        default:
            pixDestroy(&pix);
            return nullptr;
    }
    pixSetResolution(pix, dpi, dpi);
    return pix;
}

TESS_API int TESS_CALL tess_set_image_file(TessEngineHandle handle, const char* filepath) {
    if (!handle || !filepath) return -1;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    try {
        ctx->cleanup_image();

        // Read file bytes into memory
        std::ifstream file(filepath, std::ios::binary | std::ios::ate);
        if (!file.is_open()) {
            return -1;
        }
        std::streamsize size = file.tellg();
        file.seekg(0, std::ios::beg);
        std::vector<unsigned char> file_buf(static_cast<size_t>(size));
        if (!file.read(reinterpret_cast<char*>(file_buf.data()), size)) {
            return -1;
        }

        return tess_set_image_bytes(handle, file_buf.data(), file_buf.size());
    } catch (...) {
        return -1;
    }
}

TESS_API int TESS_CALL tess_set_image_bytes(TessEngineHandle handle, const unsigned char* data, size_t length) {
    if (!handle || !data || length == 0) return -1;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    try {
        ctx->cleanup_image();

        // 1. Try Leptonica pixReadMem first so format & DPI metadata are preserved
        Pix* pix = pixReadMem(data, length);
        if (pix) {
            int xres = pixGetXRes(pix);
            int yres = pixGetYRes(pix);
            if (xres < 70 || yres < 70) {
                pixSetResolution(pix, 300, 300);
                xres = 300;
                yres = 300;
            }
            ctx->current_pix = pix;
            ctx->api.SetImage(pix);
            ctx->api.SetSourceResolution(yres);
            ctx->api.SetVariable("user_defined_dpi", std::to_string(yres).c_str());
            return 0;
        }

        // 2. Fallback to decode with stb_image
        int w = 0, h = 0, channels = 0;
        stbi_uc* decoded = stbi_load_from_memory(data, static_cast<int>(length), &w, &h, &channels, 0);
        if (decoded) {
            ctx->image_w = w;
            ctx->image_h = h;
            ctx->image_bpp = channels;
            Pix* spix = raw_to_pix(decoded, w, h, channels, w * channels, 300);
            stbi_image_free(decoded);
            if (spix) {
                ctx->current_pix = spix;
                ctx->api.SetImage(spix);
                ctx->api.SetSourceResolution(300);
                ctx->api.SetVariable("user_defined_dpi", "300");
                return 0;
            }
        }

        return -1;
    } catch (...) {
        return -1;
    }
}

TESS_API int TESS_CALL tess_set_image_raw(TessEngineHandle handle, const unsigned char* image_data,
                                          int width, int height, int bytes_per_pixel, int bytes_per_line) {
    if (!handle || !image_data || width <= 0 || height <= 0) return -1;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    try {
        ctx->cleanup_image();

        ctx->image_w = width;
        ctx->image_h = height;
        ctx->image_bpp = bytes_per_pixel;

        Pix* pix = raw_to_pix(image_data, width, height, bytes_per_pixel, bytes_per_line, 300);
        if (pix) {
            ctx->current_pix = pix;
            ctx->api.SetImage(pix);
            ctx->api.SetSourceResolution(300);
            ctx->api.SetVariable("user_defined_dpi", "300");
            return 0;
        }

        size_t total_bytes = static_cast<size_t>(bytes_per_line) * height;
        ctx->raw_image_pixels.assign(image_data, image_data + total_bytes);

        ctx->api.SetImage(ctx->raw_image_pixels.data(), width, height, bytes_per_pixel, bytes_per_line);
        if (ctx->api.GetSourceYResolution() < 70) {
            ctx->api.SetSourceResolution(300);
            ctx->api.SetVariable("user_defined_dpi", "300");
        }
        return 0;
    } catch (...) {
        return -1;
    }
}

TESS_API int TESS_CALL tess_recognize(TessEngineHandle handle) {
    if (!handle) return -1;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    return ctx->api.Recognize(nullptr);
}

TESS_API char* TESS_CALL tess_get_utf8_text(TessEngineHandle handle) {
    if (!handle) return nullptr;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    char* raw = ctx->api.GetUTF8Text();
    if (!raw) return nullptr;
    char* dup = duplicate_string(raw);
    delete[] raw;
    return dup;
}

TESS_API char* TESS_CALL tess_get_hocr_text(TessEngineHandle handle, int page_number) {
    if (!handle) return nullptr;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    char* raw = ctx->api.GetHOCRText(page_number);
    if (!raw) return nullptr;
    char* dup = duplicate_string(raw);
    delete[] raw;
    return dup;
}

TESS_API char* TESS_CALL tess_get_tsv_text(TessEngineHandle handle, int page_number) {
    if (!handle) return nullptr;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    char* raw = ctx->api.GetTSVText(page_number);
    if (!raw) return nullptr;
    char* dup = duplicate_string(raw);
    delete[] raw;
    return dup;
}

TESS_API char* TESS_CALL tess_get_box_text(TessEngineHandle handle, int page_number) {
    if (!handle) return nullptr;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    char* raw = ctx->api.GetBoxText(page_number);
    if (!raw) return nullptr;
    char* dup = duplicate_string(raw);
    delete[] raw;
    return dup;
}

TESS_API char* TESS_CALL tess_get_unlv_text(TessEngineHandle handle) {
    if (!handle) return nullptr;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    char* raw = ctx->api.GetUNLVText();
    if (!raw) return nullptr;
    char* dup = duplicate_string(raw);
    delete[] raw;
    return dup;
}

TESS_API char* TESS_CALL tess_get_json_text(TessEngineHandle handle) {
    if (!handle) return nullptr;
    auto ctx = reinterpret_cast<EngineContext*>(handle);

    ctx->api.Recognize(nullptr);

    char* full_text = ctx->api.GetUTF8Text();
    std::string text_str = full_text ? full_text : "";
    if (full_text) delete[] full_text;

    int mean_conf = ctx->api.MeanTextConf();
    int psm = static_cast<int>(ctx->api.GetPageSegMode());

    std::ostringstream json;
    json << "{\n";
    json << "  \"text\": \"" << escape_json_string(text_str) << "\",\n";
    json << "  \"mean_confidence\": " << mean_conf << ",\n";
    json << "  \"psm\": " << psm << ",\n";
    json << "  \"words\": [\n";

    tesseract::ResultIterator* ri = ctx->api.GetIterator();
    bool first_word = true;
    if (ri) {
        do {
            char* word_txt = ri->GetUTF8Text(tesseract::RIL_WORD);
            if (!word_txt) continue;
            std::string w_str = word_txt;
            delete[] word_txt;

            // Trim whitespace
            size_t start = w_str.find_first_not_of(" \t\r\n");
            if (start == std::string::npos) continue;
            size_t end = w_str.find_last_not_of(" \t\r\n");
            w_str = w_str.substr(start, end - start + 1);
            if (w_str.empty()) continue;

            float conf = ri->Confidence(tesseract::RIL_WORD);
            int left = 0, top = 0, right = 0, bottom = 0;
            ri->BoundingBox(tesseract::RIL_WORD, &left, &top, &right, &bottom);

            tesseract::Orientation orient;
            tesseract::WritingDirection wdir;
            tesseract::TextlineOrder torder;
            float deskew = 0.0f;
            ri->Orientation(&orient, &wdir, &torder, &deskew);

            std::string dir_str = (wdir == tesseract::WRITING_DIRECTION_RIGHT_TO_LEFT) ? "RightToLeft" :
                                  ((wdir == tesseract::WRITING_DIRECTION_TOP_TO_BOTTOM) ? "TopToBottom" : "LeftToRight");
            std::string order_str = (torder == tesseract::TEXTLINE_ORDER_RIGHT_TO_LEFT) ? "RTL" :
                                    ((torder == tesseract::TEXTLINE_ORDER_TOP_TO_BOTTOM) ? "TTB" : "LTR");

            if (!first_word) json << ",\n";
            first_word = false;

            json << "    {\n";
            json << "      \"text\": \"" << escape_json_string(w_str) << "\",\n";
            json << "      \"confidence\": " << conf << ",\n";
            json << "      \"bbox\": [" << left << ", " << top << ", " << right << ", " << bottom << "],\n";
            json << "      \"direction\": \"" << dir_str << "\",\n";
            json << "      \"order\": \"" << order_str << "\",\n";
            json << "      \"deskew_angle\": " << deskew << "\n";
            json << "    }";
        } while (ri->Next(tesseract::RIL_WORD));
        delete ri;
    }

    json << "\n  ]\n}";

    std::string final_json = json.str();
    return duplicate_string(final_json.c_str());
}

TESS_API int TESS_CALL tess_get_mean_confidence(TessEngineHandle handle) {
    if (!handle) return 0;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    return ctx->api.MeanTextConf();
}

TESS_API void TESS_CALL tess_free_text(char* text) {
    if (text) {
        free(text);
    }
}

TESS_API char* TESS_CALL tess_get_osd_text(TessEngineHandle handle, int page_number) {
    if (!handle) return nullptr;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    try {
        char* raw = ctx->api.GetOsdText(page_number);
        if (!raw) return nullptr;
        char* dup = duplicate_string(raw);
        delete[] raw;
        return dup;
    } catch (...) {
        return nullptr;
    }
}

TESS_API int* TESS_CALL tess_get_all_word_confidences(TessEngineHandle handle, int* out_count) {
    if (!handle || !out_count) return nullptr;
    *out_count = 0;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    try {
        int* raw = ctx->api.AllWordConfidences();
        if (!raw) return nullptr;
        int count = 0;
        while (raw[count] != -1) {
            count++;
        }
        *out_count = count;
        int* copy = (int*)malloc((count + 1) * sizeof(int));
        if (copy) {
            memcpy(copy, raw, (count + 1) * sizeof(int));
        }
        delete[] raw;
        return copy;
    } catch (...) {
        return nullptr;
    }
}

TESS_API void TESS_CALL tess_free_confidences(int* confidences) {
    if (confidences) {
        free(confidences);
    }
}

TESS_API int TESS_CALL tess_generate_searchable_pdf(TessEngineHandle handle, const char* image_path, const char* output_pdf_base) {
    if (!handle || !image_path || !output_pdf_base) return -1;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    try {
        char base_buf[512] = {0};
        tess_model_get_path(base_buf, sizeof(base_buf));
        tesseract::TessPDFRenderer renderer(output_pdf_base, base_buf, false);
        bool ok = ctx->api.ProcessPages(image_path, nullptr, 0, &renderer);
        return ok ? 0 : -1;
    } catch (...) {
        return -1;
    }
}

TESS_API int TESS_CALL tess_detect_orientation_script(
    TessEngineHandle handle,
    int* orient_deg,
    float* orient_conf,
    char* script_name,
    int script_name_max_len,
    float* script_conf
) {
    if (!handle) return -1;
    auto ctx = reinterpret_cast<EngineContext*>(handle);

    try {
        const char* s_name = nullptr;
        bool ok = ctx->api.DetectOrientationScript(orient_deg, orient_conf, &s_name, script_conf);
        if (ok) {
            if (script_name && script_name_max_len > 0) {
                strncpy_s(script_name, script_name_max_len, s_name ? s_name : "Unknown", _TRUNCATE);
            }
            return 0;
        }
        return -1;
    } catch (...) {
        return -1;
    }
}

TESS_API TessIteratorHandle TESS_CALL tess_analyse_layout(TessEngineHandle handle) {
    if (!handle) return nullptr;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    tesseract::PageIterator* pi = ctx->api.AnalyseLayout();
    if (!pi) return nullptr;

    auto iter_ctx = new (std::nothrow) IteratorContext();
    if (!iter_ctx) {
        delete pi;
        return nullptr;
    }
    iter_ctx->page_iter = pi;
    iter_ctx->is_result = false;
    return reinterpret_cast<TessIteratorHandle>(iter_ctx);
}

TESS_API TessIteratorHandle TESS_CALL tess_get_iterator(TessEngineHandle handle) {
    if (!handle) return nullptr;
    auto ctx = reinterpret_cast<EngineContext*>(handle);
    tesseract::ResultIterator* ri = ctx->api.GetIterator();
    if (!ri) return nullptr;

    auto iter_ctx = new (std::nothrow) IteratorContext();
    if (!iter_ctx) {
        delete ri;
        return nullptr;
    }
    iter_ctx->res_iter = ri;
    iter_ctx->page_iter = ri;
    iter_ctx->is_result = true;
    return reinterpret_cast<TessIteratorHandle>(iter_ctx);
}

TESS_API int TESS_CALL tess_iterator_next(TessIteratorHandle iter, int level) {
    if (!iter) return 0;
    auto ctx = reinterpret_cast<IteratorContext*>(iter);
    if (!ctx->page_iter) return 0;
    return ctx->page_iter->Next(static_cast<tesseract::PageIteratorLevel>(level)) ? 1 : 0;
}

TESS_API int TESS_CALL tess_iterator_is_at_beginning_of(TessIteratorHandle iter, int level) {
    if (!iter) return 0;
    auto ctx = reinterpret_cast<IteratorContext*>(iter);
    if (!ctx->page_iter) return 0;
    return ctx->page_iter->IsAtBeginningOf(static_cast<tesseract::PageIteratorLevel>(level)) ? 1 : 0;
}

TESS_API int TESS_CALL tess_iterator_get_bounding_box(
    TessIteratorHandle iter,
    int level,
    int* left,
    int* top,
    int* right,
    int* bottom
) {
    if (!iter) return 0;
    auto ctx = reinterpret_cast<IteratorContext*>(iter);
    if (!ctx->page_iter) return 0;
    return ctx->page_iter->BoundingBox(static_cast<tesseract::PageIteratorLevel>(level),
                                       left, top, right, bottom) ? 1 : 0;
}

TESS_API char* TESS_CALL tess_iterator_get_text(TessIteratorHandle iter, int level) {
    if (!iter) return nullptr;
    auto ctx = reinterpret_cast<IteratorContext*>(iter);
    if (!ctx->is_result || !ctx->res_iter) return nullptr;

    char* raw = ctx->res_iter->GetUTF8Text(static_cast<tesseract::PageIteratorLevel>(level));
    if (!raw) return nullptr;
    char* dup = duplicate_string(raw);
    delete[] raw;
    return dup;
}

TESS_API float TESS_CALL tess_iterator_get_confidence(TessIteratorHandle iter, int level) {
    if (!iter) return 0.0f;
    auto ctx = reinterpret_cast<IteratorContext*>(iter);
    if (!ctx->is_result || !ctx->res_iter) return 0.0f;
    return ctx->res_iter->Confidence(static_cast<tesseract::PageIteratorLevel>(level));
}

TESS_API int TESS_CALL tess_iterator_get_writing_direction(TessIteratorHandle iter, int* direction) {
    if (!iter || !direction) return -1;
    auto ctx = reinterpret_cast<IteratorContext*>(iter);
    if (!ctx->page_iter) return -1;

    tesseract::Orientation orient;
    tesseract::WritingDirection wdir;
    tesseract::TextlineOrder order;
    float deskew;
    ctx->page_iter->Orientation(&orient, &wdir, &order, &deskew);
    *direction = static_cast<int>(wdir);
    return 0;
}

TESS_API int TESS_CALL tess_iterator_get_textline_order(TessIteratorHandle iter, int* order) {
    if (!iter || !order) return -1;
    auto ctx = reinterpret_cast<IteratorContext*>(iter);
    if (!ctx->page_iter) return -1;

    tesseract::Orientation orient;
    tesseract::WritingDirection wdir;
    tesseract::TextlineOrder torder;
    float deskew;
    ctx->page_iter->Orientation(&orient, &wdir, &torder, &deskew);
    *order = static_cast<int>(torder);
    return 0;
}

TESS_API int TESS_CALL tess_iterator_get_deskew_angle(TessIteratorHandle iter, float* angle) {
    if (!iter || !angle) return -1;
    auto ctx = reinterpret_cast<IteratorContext*>(iter);
    if (!ctx->page_iter) return -1;

    tesseract::Orientation orient;
    tesseract::WritingDirection wdir;
    tesseract::TextlineOrder torder;
    ctx->page_iter->Orientation(&orient, &wdir, &torder, angle);
    return 0;
}

TESS_API void TESS_CALL tess_iterator_destroy(TessIteratorHandle iter) {
    if (!iter) return;
    auto ctx = reinterpret_cast<IteratorContext*>(iter);
    delete ctx;
}

} // extern "C"
