/**
 * @file tesseract_engine.h
 * @brief Complete C Application Binary Interface (C ABI) for the monolithic Tesseract Engine DLL.
 * @company accsify
 * @copyright Copyright (C) 2026 accsify. All rights reserved.
 */

#ifndef ACCSIFY_TESSERACT_ENGINE_H
#define ACCSIFY_TESSERACT_ENGINE_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32) || defined(__WIN32__)
    #ifdef TESSERACT_ENGINE_EXPORTS
        #define TESS_API __declspec(dllexport)
    #else
        #define TESS_API __declspec(dllimport)
    #endif
    #define TESS_CALL __cdecl
#else
    #define TESS_API __attribute__((visibility("default")))
    #define TESS_CALL
#endif

/* -------------------------------------------------------------------------
 * Handle Types
 * ------------------------------------------------------------------------- */
typedef void* TessEngineHandle;
typedef void* TessIteratorHandle;
typedef void* TessDownloadHandle;

/* -------------------------------------------------------------------------
 * Enumerations
 * ------------------------------------------------------------------------- */

/**
 * @brief Page Segmentation Modes (PSM)
 */
typedef enum TessPageSegMode {
    TESS_PSM_OSD_ONLY               = 0,  /**< Orientation and script detection only. */
    TESS_PSM_AUTO_OSD               = 1,  /**< Automatic page segmentation with orientation and script detection. (OSD) */
    TESS_PSM_AUTO_ONLY              = 2,  /**< Automatic page segmentation, but no OSD, or OCR. */
    TESS_PSM_AUTO                   = 3,  /**< Fully automatic page segmentation, but no OSD. (Default) */
    TESS_PSM_SINGLE_COLUMN          = 4,  /**< Assume a single column of text of variable sizes. */
    TESS_PSM_SINGLE_BLOCK_VERT_TEXT = 5,  /**< Assume a single uniform block of vertically aligned text. */
    TESS_PSM_SINGLE_BLOCK           = 6,  /**< Assume a single uniform block of text. */
    TESS_PSM_SINGLE_LINE            = 7,  /**< Treat the image as a single text line. */
    TESS_PSM_SINGLE_WORD            = 8,  /**< Treat the image as a single word. */
    TESS_PSM_CIRCLE_WORD            = 9,  /**< Treat the image as a single word in a circle. */
    TESS_PSM_SINGLE_CHAR            = 10, /**< Treat the image as a single character. */
    TESS_PSM_SPARSE_TEXT            = 11, /**< Find as much text as possible in no particular order. */
    TESS_PSM_SPARSE_TEXT_OSD        = 12, /**< Sparse text with orientation and script detection. */
    TESS_PSM_RAW_LINE               = 13  /**< Treat the image as a single text line, bypassing hacks. */
} TessPageSegMode;

/**
 * @brief OCR Engine Modes (OEM)
 */
typedef enum TessOcrEngineMode {
    TESS_OEM_TESSERACT_ONLY             = 0, /**< Legacy Tesseract engine only. */
    TESS_OEM_LSTM_ONLY                  = 1, /**< Neural nets LSTM engine only. */
    TESS_OEM_TESSERACT_LSTM_COMBINED    = 2, /**< Legacy + LSTM combined. */
    TESS_OEM_DEFAULT                    = 3  /**< Default, based on what is available. */
} TessOcrEngineMode;

/**
 * @brief Layout Navigation Hierarchy Levels
 */
typedef enum TessPageIteratorLevel {
    TESS_LEVEL_BLOCK    = 0, /**< Block of text/image/table */
    TESS_LEVEL_PARA     = 1, /**< Paragraph within a block */
    TESS_LEVEL_TEXTLINE = 2, /**< Text line within a paragraph */
    TESS_LEVEL_WORD     = 3, /**< Word within a text line */
    TESS_LEVEL_SYMBOL   = 4  /**< Individual character/symbol within a word */
} TessPageIteratorLevel;

/**
 * @brief Text Writing Direction
 */
typedef enum TessWritingDirection {
    TESS_DIRECTION_LEFT_TO_RIGHT = 0, /**< Left-to-right (e.g. Latin, Cyrillic) */
    TESS_DIRECTION_RIGHT_TO_LEFT = 1, /**< Right-to-left (e.g. Arabic, Hebrew) */
    TESS_DIRECTION_TOP_TO_BOTTOM = 2  /**< Top-to-bottom (e.g. traditional Chinese/Japanese) */
} TessWritingDirection;

/**
 * @brief Textline Reading Order
 */
typedef enum TessTextlineOrder {
    TESS_ORDER_LEFT_TO_RIGHT = 0,
    TESS_ORDER_RIGHT_TO_LEFT = 1,
    TESS_ORDER_TOP_TO_BOTTOM = 2
} TessTextlineOrder;

/**
 * @brief Model repository categories
 */
typedef enum TessModelType {
    TESS_MODEL_TYPE_FAST     = 0, /**< tessdata_fast (compact, fast inference, 1-5MB) */
    TESS_MODEL_TYPE_BEST     = 1, /**< tessdata_best (high-precision LSTM, 15-40MB) */
    TESS_MODEL_TYPE_STANDARD = 2, /**< tessdata (standard release models) */
    TESS_MODEL_TYPE_SCRIPT   = 3  /**< script models (Arabic, Cyrillic, Devanagari, Latin, etc.) */
} TessModelType;

/* -------------------------------------------------------------------------
 * Structures
 * ------------------------------------------------------------------------- */

#pragma pack(push, 8)
/**
 * @brief Model information structure
 */
typedef struct TessModelInfo {
    char name[64];              /**< Model identifier e.g. "eng", "fra", "script/Arabic" */
    char display_name[128];     /**< Human readable name e.g. "English", "Arabic Script" */
    int32_t model_type;         /**< TessModelType */
    int64_t file_size;          /**< Estimated size in bytes */
    char download_url[256];     /**< Direct HTTPS URL */
    int32_t is_installed;       /**< 1 if present in current tessdata path, 0 otherwise */
} TessModelInfo;

/**
 * @brief Bounding Box structure
 */
typedef struct TessBoundingBox {
    int32_t left;
    int32_t top;
    int32_t right;
    int32_t bottom;
} TessBoundingBox;
#pragma pack(pop)

/**
 * @brief Callback for download progress monitoring
 * @param model_name Identifier of the model being downloaded
 * @param model_type TessModelType
 * @param bytes_downloaded Number of bytes received so far
 * @param total_bytes Total size in bytes (-1 if unknown)
 * @param percentage Progress 0.0 to 100.0
 * @param status_message Current status description
 * @param user_data Custom user-supplied pointer
 * @return Return 0 to continue download, non-zero to cancel/abort
 */
typedef int (TESS_CALL *TessDownloadProgressCallback)(
    const char* model_name,
    int32_t model_type,
    int64_t bytes_downloaded,
    int64_t total_bytes,
    double percentage,
    const char* status_message,
    void* user_data
);

/* -------------------------------------------------------------------------
 * Engine Lifecycle & Information
 * ------------------------------------------------------------------------- */

/**
 * @brief Returns the version string of the engine and Tesseract.
 */
TESS_API const char* TESS_CALL tess_version(void);

/**
 * @brief Create a new Tesseract engine instance.
 * @return Engine handle, or NULL on failure.
 */
TESS_API TessEngineHandle TESS_CALL tess_create(void);

/**
 * @brief Destroy a Tesseract engine instance and free all resources.
 * @param handle Engine handle.
 */
TESS_API void TESS_CALL tess_destroy(TessEngineHandle handle);

/**
 * @brief Initialize the Tesseract engine with a data path and language.
 * @param handle Engine handle.
 * @param datapath Path to tessdata directory containing .traineddata files. NULL uses default path.
 * @param language Language code e.g. "eng", "fra", "ara+eng", or script "script/Arabic".
 * @param oem_mode OCR engine mode (TessOcrEngineMode).
 * @return 0 on success, non-zero on error.
 */
TESS_API int TESS_CALL tess_init(TessEngineHandle handle, const char* datapath, const char* language, int oem_mode);

/**
 * @brief Check if the engine is initialized.
 */
TESS_API int TESS_CALL tess_is_initialized(TessEngineHandle handle);

/**
 * @brief Set an internal Tesseract variable/parameter.
 * @param handle Engine handle.
 * @param name Variable name (e.g. "tessedit_char_whitelist").
 * @param value Variable value string.
 * @return 1 on success, 0 on failure.
 */
TESS_API int TESS_CALL tess_set_variable(TessEngineHandle handle, const char* name, const char* value);

/**
 * @brief Get an internal Tesseract variable/parameter value.
 */
TESS_API int TESS_CALL tess_get_variable(TessEngineHandle handle, const char* name, char* buffer, int max_len);

/**
 * @brief Set the Page Segmentation Mode (PSM).
 */
TESS_API void TESS_CALL tess_set_page_seg_mode(TessEngineHandle handle, int psm_mode);

/**
 * @brief Get current Page Segmentation Mode (PSM).
 */
TESS_API int TESS_CALL tess_get_page_seg_mode(TessEngineHandle handle);

/**
 * @brief Set source image resolution in Pixels Per Inch (PPI/DPI).
 */
TESS_API void TESS_CALL tess_set_source_resolution(TessEngineHandle handle, int ppi);

/**
 * @brief Get current source image resolution in Pixels Per Inch (PPI/DPI).
 * @return PPI/DPI value, or 0 if unset.
 */
TESS_API int TESS_CALL tess_get_source_resolution(TessEngineHandle handle);

/**
 * @brief Restrict recognition to a sub-rectangle (Region of Interest / ROI) of the currently loaded image.
 * @param handle Engine handle.
 * @param left Left X pixel coordinate.
 * @param top Top Y pixel coordinate.
 * @param width Rectangle width in pixels.
 * @param height Rectangle height in pixels.
 */
TESS_API void TESS_CALL tess_set_rectangle(TessEngineHandle handle, int left, int top, int width, int height);

/**
 * @brief Clear recognition results and reset current image while keeping the engine initialized.
 * Allows rapidly recognizing another image without reloading language models.
 */
TESS_API void TESS_CALL tess_clear(TessEngineHandle handle);

/**
 * @brief Set character whitelist (restrict recognition to only these characters, e.g. "0123456789").
 * Pass NULL or empty string to remove restriction.
 * @return 1 on success, 0 on failure.
 */
TESS_API int TESS_CALL tess_set_char_whitelist(TessEngineHandle handle, const char* whitelist);

/**
 * @brief Set character blacklist (prevent OCR from outputting these characters).
 * Pass NULL or empty string to remove restriction.
 * @return 1 on success, 0 on failure.
 */
TESS_API int TESS_CALL tess_set_char_blacklist(TessEngineHandle handle, const char* blacklist);

/* -------------------------------------------------------------------------
 * Image Input
 * ------------------------------------------------------------------------- */

/**
 * @brief Set image from a file on disk (supports PNG, JPEG, TIFF, BMP, WebP, GIF, PNM).
 * @return 0 on success, non-zero on failure.
 */
TESS_API int TESS_CALL tess_set_image_file(TessEngineHandle handle, const char* filepath);

/**
 * @brief Set image from an encoded memory buffer (PNG, JPEG, TIFF, BMP).
 * @param handle Engine handle.
 * @param data Buffer pointer.
 * @param length Buffer length in bytes.
 * @return 0 on success, non-zero on failure.
 */
TESS_API int TESS_CALL tess_set_image_bytes(TessEngineHandle handle, const unsigned char* data, size_t length);

/**
 * @brief Set image from raw uncompressed pixel data.
 * @param handle Engine handle.
 * @param image_data Pointer to raw pixel bytes.
 * @param width Image width in pixels.
 * @param height Image height in pixels.
 * @param bytes_per_pixel Bytes per pixel (1=grayscale, 3=RGB, 4=RGBA).
 * @param bytes_per_line Bytes per row (stride/pitch).
 * @return 0 on success, non-zero on failure.
 */
TESS_API int TESS_CALL tess_set_image_raw(TessEngineHandle handle, const unsigned char* image_data,
                                          int width, int height, int bytes_per_pixel, int bytes_per_line);

/* -------------------------------------------------------------------------
 * Recognition & Text Outputs
 * ------------------------------------------------------------------------- */

/**
 * @brief Perform recognition on the currently set image.
 * @return 0 on success, non-zero on failure.
 */
TESS_API int TESS_CALL tess_recognize(TessEngineHandle handle);

/**
 * @brief Get recognized UTF-8 plain text. Must be freed with tess_free_text().
 */
TESS_API char* TESS_CALL tess_get_utf8_text(TessEngineHandle handle);

/**
 * @brief Get recognized HOCR formatted HTML. Must be freed with tess_free_text().
 * @param handle Engine handle.
 * @param page_number 0-based page number.
 */
TESS_API char* TESS_CALL tess_get_hocr_text(TessEngineHandle handle, int page_number);

/**
 * @brief Get recognized TSV (tab-separated values) text. Must be freed with tess_free_text().
 */
TESS_API char* TESS_CALL tess_get_tsv_text(TessEngineHandle handle, int page_number);

/**
 * @brief Get recognized Box text (character bounding boxes). Must be freed with tess_free_text().
 */
TESS_API char* TESS_CALL tess_get_box_text(TessEngineHandle handle, int page_number);

/**
 * @brief Get recognized UNLV text. Must be freed with tess_free_text().
 */
TESS_API char* TESS_CALL tess_get_unlv_text(TessEngineHandle handle);

/**
 * @brief Get recognized document structure as a JSON formatted string. Must be freed with tess_free_text().
 * Contains full layout hierarchy: text, mean confidence, blocks, lines, words with coordinates, writing directions.
 */
TESS_API char* TESS_CALL tess_get_json_text(TessEngineHandle handle);

/**
 * @brief Get mean confidence of the recognized text (0 to 100).
 */
TESS_API int TESS_CALL tess_get_mean_confidence(TessEngineHandle handle);

/**
 * @brief Free text allocated and returned by any tess_get_*_text function.
 */
TESS_API void TESS_CALL tess_free_text(char* text);

/**
 * @brief Get recognized text formatted as classical OSD output. Must be freed with tess_free_text().
 * Formatted with 'Page number', 'Orientation in degrees', 'Rotate', 'Orientation confidence', 'Script', 'Script confidence'.
 * @param handle Engine handle.
 * @param page_number 0-based page number.
 */
TESS_API char* TESS_CALL tess_get_osd_text(TessEngineHandle handle, int page_number);

/**
 * @brief Get an array of confidences (0 to 100) for all recognized words.
 * @param handle Engine handle.
 * @param out_count Output pointer receiving the word count.
 * @return Dynamically allocated int array. Must be freed with tess_free_confidences().
 */
TESS_API int* TESS_CALL tess_get_all_word_confidences(TessEngineHandle handle, int* out_count);

/**
 * @brief Free confidence array returned by tess_get_all_word_confidences().
 */
TESS_API void TESS_CALL tess_free_confidences(int* confidences);

/**
 * @brief Generate a searchable PDF from an image file on disk.
 * @param handle Engine handle.
 * @param image_path Source image file path.
 * @param output_pdf_base Output PDF base path without extension (.pdf will be appended).
 * @return 0 on success, non-zero on failure.
 */
TESS_API int TESS_CALL tess_generate_searchable_pdf(TessEngineHandle handle, const char* image_path, const char* output_pdf_base);

/* -------------------------------------------------------------------------
 * Layout Analysis, Orientation, Writing Direction & Script Detection
 * ------------------------------------------------------------------------- */

/**
 * @brief Detect orientation and script (OSD).
 * @param handle Engine handle.
 * @param orient_deg Output degrees of orientation (0, 90, 180, 270).
 * @param orient_conf Output orientation confidence.
 * @param script_name Buffer to receive detected script name (e.g. "Latin", "Arabic").
 * @param script_name_max_len Size of script_name buffer.
 * @param script_conf Output script confidence.
 * @return 0 on success, non-zero on failure.
 */
TESS_API int TESS_CALL tess_detect_orientation_script(
    TessEngineHandle handle,
    int* orient_deg,
    float* orient_conf,
    char* script_name,
    int script_name_max_len,
    float* script_conf
);

/**
 * @brief Perform layout analysis on the image and return an iterator over layout blocks.
 * @return Iterator handle, or NULL on failure. Must be freed with tess_iterator_destroy().
 */
TESS_API TessIteratorHandle TESS_CALL tess_analyse_layout(TessEngineHandle handle);

/**
 * @brief Get a result iterator after recognition to inspect words, lines, boxes, and confidences.
 * @return Iterator handle, or NULL on failure. Must be freed with tess_iterator_destroy().
 */
TESS_API TessIteratorHandle TESS_CALL tess_get_iterator(TessEngineHandle handle);

/**
 * @brief Advance the iterator to the next element at the given hierarchy level.
 * @return 1 if successfully advanced, 0 if at the end of the page.
 */
TESS_API int TESS_CALL tess_iterator_next(TessIteratorHandle iter, int level);

/**
 * @brief Check if iterator is at the beginning of a given level.
 */
TESS_API int TESS_CALL tess_iterator_is_at_beginning_of(TessIteratorHandle iter, int level);

/**
 * @brief Get bounding box of the element at the current iterator position.
 * @return 1 on success, 0 on failure.
 */
TESS_API int TESS_CALL tess_iterator_get_bounding_box(
    TessIteratorHandle iter,
    int level,
    int* left,
    int* top,
    int* right,
    int* bottom
);

/**
 * @brief Get text of element at current iterator position. Must be freed with tess_free_text().
 */
TESS_API char* TESS_CALL tess_iterator_get_text(TessIteratorHandle iter, int level);

/**
 * @brief Get confidence (0.0 to 100.0) of element at current iterator position.
 */
TESS_API float TESS_CALL tess_iterator_get_confidence(TessIteratorHandle iter, int level);

/**
 * @brief Get writing direction of current element (0=LTR, 1=RTL, 2=TTB).
 */
TESS_API int TESS_CALL tess_iterator_get_writing_direction(TessIteratorHandle iter, int* direction);

/**
 * @brief Get textline reading order of current element (0=LTR, 1=RTL, 2=TTB).
 */
TESS_API int TESS_CALL tess_iterator_get_textline_order(TessIteratorHandle iter, int* order);

/**
 * @brief Get deskew angle in radians.
 */
TESS_API int TESS_CALL tess_iterator_get_deskew_angle(TessIteratorHandle iter, float* angle);

/**
 * @brief Destroy and free an iterator handle.
 */
TESS_API void TESS_CALL tess_iterator_destroy(TessIteratorHandle iter);

/* -------------------------------------------------------------------------
 * Model Management & WinHTTP Downloader
 * ------------------------------------------------------------------------- */

/**
 * @brief Set the active tessdata models directory path.
 * @param path Directory path. If NULL or empty, resets to default.
 * @return 0 on success, non-zero on failure.
 */
TESS_API int TESS_CALL tess_model_set_path(const char* path);

/**
 * @brief Get the active tessdata models directory path.
 * @param buffer Output buffer.
 * @param max_len Buffer size in bytes.
 * @return 0 on success, non-zero on failure.
 */
TESS_API int TESS_CALL tess_model_get_path(char* buffer, int max_len);

/**
 * @brief Get the default tessdata models directory path (adjacent to the DLL in ./tessdata).
 */
TESS_API int TESS_CALL tess_model_get_default_path(char* buffer, int max_len);

/**
 * @brief Set the active model flavor (TESS_MODEL_TYPE_FAST, TESS_MODEL_TYPE_BEST, etc.).
 * When set, models are saved into and searched inside corresponding subdirectories (e.g. ./tessdata/best/).
 */
TESS_API void TESS_CALL tess_model_set_flavor(int model_type);

/**
 * @brief Get the active model flavor (TessModelType).
 */
TESS_API int TESS_CALL tess_model_get_flavor(void);

/**
 * @brief Get the directory path for a specific flavor (e.g. ./tessdata/best or ./tessdata/fast).
 */
TESS_API int TESS_CALL tess_model_get_flavor_path(int model_type, char* buffer, int max_len);

/**
 * @brief Check if a model is installed in the active tessdata path.
 * @param model_name Name of the model (e.g. "eng", "ara", "script/Arabic").
 * @param model_type TessModelType.
 * @return 1 if installed, 0 if not installed.
 */
TESS_API int TESS_CALL tess_model_is_installed(const char* model_name, int model_type);

/**
 * @brief Get the count of catalog models available for a model type.
 * @param model_type TessModelType (-1 for all types).
 * @return Number of models in catalog.
 */
TESS_API int TESS_CALL tess_model_get_catalog_count(int model_type);

/**
 * @brief Retrieve model information from the catalog by index.
 * @param model_type TessModelType (-1 for all types).
 * @param index 0-based index.
 * @param out_info Pointer to TessModelInfo struct to populate.
 * @return 0 on success, non-zero on failure.
 */
TESS_API int TESS_CALL tess_model_get_catalog_item(int model_type, int index, TessModelInfo* out_info);

/**
 * @brief Download a model synchronously with live progress callbacks.
 * @param model_name Identifier of model to download (e.g. "eng", "script/Arabic").
 * @param model_type TessModelType.
 * @param callback Progress callback function (can be NULL).
 * @param user_data User pointer passed to callback.
 * @return 0 on success, non-zero on failure or cancellation.
 */
TESS_API int TESS_CALL tess_model_download(
    const char* model_name,
    int model_type,
    TessDownloadProgressCallback callback,
    void* user_data
);

/**
 * @brief Start downloading a model asynchronously on a background worker thread.
 * @param model_name Identifier of model to download.
 * @param model_type TessModelType.
 * @param callback Progress callback function.
 * @param user_data User pointer passed to callback.
 * @param out_handle Receives download handle for cancellation/tracking.
 * @return 0 on success, non-zero on failure.
 */
TESS_API int TESS_CALL tess_model_download_async(
    const char* model_name,
    int model_type,
    TessDownloadProgressCallback callback,
    void* user_data,
    TessDownloadHandle* out_handle
);

/**
 * @brief Cancel an in-progress asynchronous model download.
 * @param handle Download handle returned by tess_model_download_async().
 * @return 0 on success, non-zero on failure.
 */
TESS_API int TESS_CALL tess_model_cancel_download(TessDownloadHandle handle);

/**
 * @brief Get the number of traineddata model files installed on disk in active tessdata folder.
 */
TESS_API int TESS_CALL tess_model_get_installed_count(void);

/**
 * @brief Get the name of an installed model file by index.
 */
TESS_API int TESS_CALL tess_model_get_installed_item(int index, char* out_name, int max_len);

#ifdef __cplusplus
}
#endif

#endif /* ACCSIFY_TESSERACT_ENGINE_H */
