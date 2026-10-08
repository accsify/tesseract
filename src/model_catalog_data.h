/**
 * @file model_catalog_data.h
 * @brief Catalog of official Tesseract models (fast, best, standard, scripts).
 * @company accsi
 * @copyright Copyright (C) 2026 accsi. All rights reserved.
 */

#ifndef ACCSI_MODEL_CATALOG_DATA_H
#define ACCSI_MODEL_CATALOG_DATA_H

#include "tesseract_engine.h"

namespace accsi {

struct CatalogEntry {
    const char* name;
    const char* display_name;
    int model_type;
    int64_t file_size;
    const char* url;
};

static const CatalogEntry g_model_catalog[] = {
    // -------------------------------------------------------------
    // Helper & OSD models
    // -------------------------------------------------------------
    { "osd", "Orientation & Script Detection", TESS_MODEL_TYPE_FAST, 10562727, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/osd.traineddata" },
    { "osd", "Orientation & Script Detection (Best)", TESS_MODEL_TYPE_BEST, 10562727, "https://github.com/tesseract-ocr/tessdata_best/raw/main/osd.traineddata" },

    // -------------------------------------------------------------
    // Fast models (tessdata_fast) - Lightweight & High Performance
    // -------------------------------------------------------------
    { "eng", "English (Fast)", TESS_MODEL_TYPE_FAST, 4113088, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/eng.traineddata" },
    { "ara", "Arabic (Fast)", TESS_MODEL_TYPE_FAST, 2371900, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/ara.traineddata" },
    { "fra", "French (Fast)", TESS_MODEL_TYPE_FAST, 4043180, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/fra.traineddata" },
    { "deu", "German (Fast)", TESS_MODEL_TYPE_FAST, 4015000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/deu.traineddata" },
    { "spa", "Spanish (Fast)", TESS_MODEL_TYPE_FAST, 4050000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/spa.traineddata" },
    { "ita", "Italian (Fast)", TESS_MODEL_TYPE_FAST, 4020000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/ita.traineddata" },
    { "por", "Portuguese (Fast)", TESS_MODEL_TYPE_FAST, 4030000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/por.traineddata" },
    { "rus", "Russian (Fast)", TESS_MODEL_TYPE_FAST, 4370000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/rus.traineddata" },
    { "chi_sim", "Chinese Simplified (Fast)", TESS_MODEL_TYPE_FAST, 11000000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/chi_sim.traineddata" },
    { "chi_tra", "Chinese Traditional (Fast)", TESS_MODEL_TYPE_FAST, 13000000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/chi_tra.traineddata" },
    { "jpn", "Japanese (Fast)", TESS_MODEL_TYPE_FAST, 11500000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/jpn.traineddata" },
    { "kor", "Korean (Fast)", TESS_MODEL_TYPE_FAST, 12000000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/kor.traineddata" },
    { "hin", "Hindi (Fast)", TESS_MODEL_TYPE_FAST, 2500000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/hin.traineddata" },
    { "tur", "Turkish (Fast)", TESS_MODEL_TYPE_FAST, 3900000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/tur.traineddata" },
    { "pol", "Polish (Fast)", TESS_MODEL_TYPE_FAST, 4100000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/pol.traineddata" },
    { "nld", "Dutch (Fast)", TESS_MODEL_TYPE_FAST, 3950000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/nld.traineddata" },
    { "swe", "Swedish (Fast)", TESS_MODEL_TYPE_FAST, 3800000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/swe.traineddata" },
    { "vie", "Vietnamese (Fast)", TESS_MODEL_TYPE_FAST, 4200000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/vie.traineddata" },
    { "heb", "Hebrew (Fast)", TESS_MODEL_TYPE_FAST, 2100000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/heb.traineddata" },
    { "ell", "Greek (Fast)", TESS_MODEL_TYPE_FAST, 3100000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/ell.traineddata" },

    // -------------------------------------------------------------
    // Best models (tessdata_best) - High Accuracy / Full LSTM
    // -------------------------------------------------------------
    { "eng", "English (Best)", TESS_MODEL_TYPE_BEST, 15400000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata" },
    { "ara", "Arabic (Best)", TESS_MODEL_TYPE_BEST, 12500000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/ara.traineddata" },
    { "fra", "French (Best)", TESS_MODEL_TYPE_BEST, 15300000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/fra.traineddata" },
    { "deu", "German (Best)", TESS_MODEL_TYPE_BEST, 15350000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/deu.traineddata" },
    { "spa", "Spanish (Best)", TESS_MODEL_TYPE_BEST, 15400000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/spa.traineddata" },
    { "ita", "Italian (Best)", TESS_MODEL_TYPE_BEST, 15300000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/ita.traineddata" },
    { "por", "Portuguese (Best)", TESS_MODEL_TYPE_BEST, 15350000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/por.traineddata" },
    { "rus", "Russian (Best)", TESS_MODEL_TYPE_BEST, 16100000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/rus.traineddata" },
    { "chi_sim", "Chinese Simplified (Best)", TESS_MODEL_TYPE_BEST, 41000000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/chi_sim.traineddata" },
    { "chi_tra", "Chinese Traditional (Best)", TESS_MODEL_TYPE_BEST, 48000000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/chi_tra.traineddata" },
    { "jpn", "Japanese (Best)", TESS_MODEL_TYPE_BEST, 34000000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/jpn.traineddata" },
    { "kor", "Korean (Best)", TESS_MODEL_TYPE_BEST, 35000000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/kor.traineddata" },
    { "hin", "Hindi (Best)", TESS_MODEL_TYPE_BEST, 13000000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/hin.traineddata" },
    { "tur", "Turkish (Best)", TESS_MODEL_TYPE_BEST, 15000000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/tur.traineddata" },
    { "pol", "Polish (Best)", TESS_MODEL_TYPE_BEST, 15500000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/pol.traineddata" },
    { "nld", "Dutch (Best)", TESS_MODEL_TYPE_BEST, 15200000, "https://github.com/tesseract-ocr/tessdata_best/raw/main/nld.traineddata" },

    // -------------------------------------------------------------
    // Standard models (tessdata) - Compatible standard models
    // -------------------------------------------------------------
    { "eng", "English (Standard)", TESS_MODEL_TYPE_STANDARD, 23000000, "https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata" },
    { "ara", "Arabic (Standard)", TESS_MODEL_TYPE_STANDARD, 19000000, "https://github.com/tesseract-ocr/tessdata/raw/main/ara.traineddata" },
    { "fra", "French (Standard)", TESS_MODEL_TYPE_STANDARD, 22000000, "https://github.com/tesseract-ocr/tessdata/raw/main/fra.traineddata" },
    { "deu", "German (Standard)", TESS_MODEL_TYPE_STANDARD, 22000000, "https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata" },
    { "spa", "Spanish (Standard)", TESS_MODEL_TYPE_STANDARD, 22000000, "https://github.com/tesseract-ocr/tessdata/raw/main/spa.traineddata" },

    // -------------------------------------------------------------
    // Writing Scripts (tessdata_fast/script)
    // -------------------------------------------------------------
    { "script/Arabic", "Arabic Script", TESS_MODEL_TYPE_SCRIPT, 5400000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Arabic.traineddata" },
    { "script/Armenian", "Armenian Script", TESS_MODEL_TYPE_SCRIPT, 4100000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Armenian.traineddata" },
    { "script/Bengali", "Bengali Script", TESS_MODEL_TYPE_SCRIPT, 4300000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Bengali.traineddata" },
    { "script/Canadian_Aboriginal", "Canadian Aboriginal Script", TESS_MODEL_TYPE_SCRIPT, 3600000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Canadian_Aboriginal.traineddata" },
    { "script/Cherokee", "Cherokee Script", TESS_MODEL_TYPE_SCRIPT, 3500000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Cherokee.traineddata" },
    { "script/Cyrillic", "Cyrillic Script", TESS_MODEL_TYPE_SCRIPT, 4900000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Cyrillic.traineddata" },
    { "script/Devanagari", "Devanagari Script", TESS_MODEL_TYPE_SCRIPT, 4800000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Devanagari.traineddata" },
    { "script/Ethiopic", "Ethiopic Script", TESS_MODEL_TYPE_SCRIPT, 4300000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Ethiopic.traineddata" },
    { "script/Georgian", "Georgian Script", TESS_MODEL_TYPE_SCRIPT, 4100000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Georgian.traineddata" },
    { "script/Greek", "Greek Script", TESS_MODEL_TYPE_SCRIPT, 3900000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Greek.traineddata" },
    { "script/Gujarati", "Gujarati Script", TESS_MODEL_TYPE_SCRIPT, 4300000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Gujarati.traineddata" },
    { "script/Gurmukhi", "Gurmukhi Script", TESS_MODEL_TYPE_SCRIPT, 4200000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Gurmukhi.traineddata" },
    { "script/HanS", "Han Simplified Script", TESS_MODEL_TYPE_SCRIPT, 11500000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/HanS.traineddata" },
    { "script/HanT", "Han Traditional Script", TESS_MODEL_TYPE_SCRIPT, 13200000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/HanT.traineddata" },
    { "script/Hangul", "Hangul Script", TESS_MODEL_TYPE_SCRIPT, 12200000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Hangul.traineddata" },
    { "script/Hebrew", "Hebrew Script", TESS_MODEL_TYPE_SCRIPT, 3800000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Hebrew.traineddata" },
    { "script/Japanese", "Japanese Script", TESS_MODEL_TYPE_SCRIPT, 11800000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Japanese.traineddata" },
    { "script/Kannada", "Kannada Script", TESS_MODEL_TYPE_SCRIPT, 4400000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Kannada.traineddata" },
    { "script/Khmer", "Khmer Script", TESS_MODEL_TYPE_SCRIPT, 4200000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Khmer.traineddata" },
    { "script/Lao", "Lao Script", TESS_MODEL_TYPE_SCRIPT, 4100000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Lao.traineddata" },
    { "script/Latin", "Latin Script", TESS_MODEL_TYPE_SCRIPT, 5800000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Latin.traineddata" },
    { "script/Malayalam", "Malayalam Script", TESS_MODEL_TYPE_SCRIPT, 4500000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Malayalam.traineddata" },
    { "script/Myanmar", "Myanmar Script", TESS_MODEL_TYPE_SCRIPT, 4300000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Myanmar.traineddata" },
    { "script/Oriya", "Oriya Script", TESS_MODEL_TYPE_SCRIPT, 4300000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Oriya.traineddata" },
    { "script/Sinhala", "Sinhala Script", TESS_MODEL_TYPE_SCRIPT, 4300000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Sinhala.traineddata" },
    { "script/Syriac", "Syriac Script", TESS_MODEL_TYPE_SCRIPT, 3600000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Syriac.traineddata" },
    { "script/Tamil", "Tamil Script", TESS_MODEL_TYPE_SCRIPT, 4500000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Tamil.traineddata" },
    { "script/Telugu", "Telugu Script", TESS_MODEL_TYPE_SCRIPT, 4500000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Telugu.traineddata" },
    { "script/Thaana", "Thaana Script", TESS_MODEL_TYPE_SCRIPT, 3500000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Thaana.traineddata" },
    { "script/Thai", "Thai Script", TESS_MODEL_TYPE_SCRIPT, 4300000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Thai.traineddata" },
    { "script/Tibetan", "Tibetan Script", TESS_MODEL_TYPE_SCRIPT, 4100000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Tibetan.traineddata" },
    { "script/Vietnamese", "Vietnamese Script", TESS_MODEL_TYPE_SCRIPT, 4200000, "https://github.com/tesseract-ocr/tessdata_fast/raw/main/script/Vietnamese.traineddata" }
};

static const size_t g_model_catalog_size = sizeof(g_model_catalog) / sizeof(g_model_catalog[0]);

} // namespace accsi

#endif /* ACCSI_MODEL_CATALOG_DATA_H */
