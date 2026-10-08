/**
 * @file tesseract_engine_cpp.hpp
 * @brief High-level C++ RAII wrapper for the Accsify Tesseract OCR Engine.
 * @company accsify
 * @copyright Copyright (C) 2026 accsify. All rights reserved.
 */

#ifndef ACCSIFY_TESSERACT_ENGINE_CPP_HPP
#define ACCSIFY_TESSERACT_ENGINE_CPP_HPP

#include "tesseract_engine.h"
#include <string>
#include <vector>
#include <memory>
#include <stdexcept>
#include <functional>

namespace accsify {

class TesseractIterator {
public:
    explicit TesseractIterator(TessIteratorHandle handle) : m_handle(handle) {}
    ~TesseractIterator() {
        if (m_handle) {
            tess_iterator_destroy(m_handle);
            m_handle = nullptr;
        }
    }

    TesseractIterator(const TesseractIterator&) = delete;
    TesseractIterator& operator=(const TesseractIterator&) = delete;

    TesseractIterator(TesseractIterator&& other) noexcept : m_handle(other.m_handle) {
        other.m_handle = nullptr;
    }

    TesseractIterator& operator=(TesseractIterator&& other) noexcept {
        if (this != &other) {
            if (m_handle) tess_iterator_destroy(m_handle);
            m_handle = other.m_handle;
            other.m_handle = nullptr;
        }
        return *this;
    }

    bool next(TessPageIteratorLevel level) {
        return m_handle && tess_iterator_next(m_handle, static_cast<int>(level)) != 0;
    }

    bool is_at_beginning_of(TessPageIteratorLevel level) const {
        return m_handle && tess_iterator_is_at_beginning_of(m_handle, static_cast<int>(level)) != 0;
    }

    bool get_bounding_box(TessPageIteratorLevel level, TessBoundingBox& box) const {
        if (!m_handle) return false;
        return tess_iterator_get_bounding_box(m_handle, static_cast<int>(level),
                                             &box.left, &box.top, &box.right, &box.bottom) != 0;
    }

    std::string get_text(TessPageIteratorLevel level) const {
        if (!m_handle) return "";
        char* raw = tess_iterator_get_text(m_handle, static_cast<int>(level));
        if (!raw) return "";
        std::string result(raw);
        tess_free_text(raw);
        return result;
    }

    float get_confidence(TessPageIteratorLevel level) const {
        if (!m_handle) return 0.0f;
        return tess_iterator_get_confidence(m_handle, static_cast<int>(level));
    }

    TessWritingDirection get_writing_direction() const {
        int dir = 0;
        if (m_handle) tess_iterator_get_writing_direction(m_handle, &dir);
        return static_cast<TessWritingDirection>(dir);
    }

    TessTextlineOrder get_textline_order() const {
        int order = 0;
        if (m_handle) tess_iterator_get_textline_order(m_handle, &order);
        return static_cast<TessTextlineOrder>(order);
    }

    float get_deskew_angle() const {
        float angle = 0.0f;
        if (m_handle) tess_iterator_get_deskew_angle(m_handle, &angle);
        return angle;
    }

    TessIteratorHandle raw_handle() const { return m_handle; }

private:
    TessIteratorHandle m_handle;
};

class TesseractEngine {
public:
    TesseractEngine() {
        m_handle = tess_create();
        if (!m_handle) {
            throw std::runtime_error("Failed to allocate Tesseract engine handle");
        }
    }

    ~TesseractEngine() {
        if (m_handle) {
            tess_destroy(m_handle);
            m_handle = nullptr;
        }
    }

    TesseractEngine(const TesseractEngine&) = delete;
    TesseractEngine& operator=(const TesseractEngine&) = delete;

    TesseractEngine(TesseractEngine&& other) noexcept : m_handle(other.m_handle) {
        other.m_handle = nullptr;
    }

    TesseractEngine& operator=(TesseractEngine&& other) noexcept {
        if (this != &other) {
            if (m_handle) tess_destroy(m_handle);
            m_handle = other.m_handle;
            other.m_handle = nullptr;
        }
        return *this;
    }

    bool init(const std::string& datapath, const std::string& language = "eng", TessOcrEngineMode oem = TESS_OEM_DEFAULT) {
        return tess_init(m_handle, datapath.empty() ? nullptr : datapath.c_str(),
                         language.c_str(), static_cast<int>(oem)) == 0;
    }

    bool is_initialized() const {
        return tess_is_initialized(m_handle) != 0;
    }

    bool set_variable(const std::string& name, const std::string& value) {
        return tess_set_variable(m_handle, name.c_str(), value.c_str()) != 0;
    }

    std::string get_variable(const std::string& name) const {
        char buf[256] = {0};
        if (tess_get_variable(m_handle, name.c_str(), buf, sizeof(buf)) != 0) {
            return std::string(buf);
        }
        return "";
    }

    void set_page_seg_mode(TessPageSegMode psm) {
        tess_set_page_seg_mode(m_handle, static_cast<int>(psm));
    }

    TessPageSegMode get_page_seg_mode() const {
        return static_cast<TessPageSegMode>(tess_get_page_seg_mode(m_handle));
    }

    void set_resolution(int ppi) {
        tess_set_source_resolution(m_handle, ppi);
    }

    bool set_image_file(const std::string& filepath) {
        return tess_set_image_file(m_handle, filepath.c_str()) == 0;
    }

    bool set_image_bytes(const unsigned char* data, size_t length) {
        return tess_set_image_bytes(m_handle, data, length) == 0;
    }

    bool set_image_raw(const unsigned char* data, int width, int height, int bytes_per_pixel, int bytes_per_line) {
        return tess_set_image_raw(m_handle, data, width, height, bytes_per_pixel, bytes_per_line) == 0;
    }

    bool recognize() {
        return tess_recognize(m_handle) == 0;
    }

    std::string get_utf8_text() const {
        char* text = tess_get_utf8_text(m_handle);
        if (!text) return "";
        std::string s(text);
        tess_free_text(text);
        return s;
    }

    std::string get_hocr_text(int page_num = 0) const {
        char* text = tess_get_hocr_text(m_handle, page_num);
        if (!text) return "";
        std::string s(text);
        tess_free_text(text);
        return s;
    }

    std::string get_tsv_text(int page_num = 0) const {
        char* text = tess_get_tsv_text(m_handle, page_num);
        if (!text) return "";
        std::string s(text);
        tess_free_text(text);
        return s;
    }

    std::string get_box_text(int page_num = 0) const {
        char* text = tess_get_box_text(m_handle, page_num);
        if (!text) return "";
        std::string s(text);
        tess_free_text(text);
        return s;
    }

    std::string get_unlv_text() const {
        char* text = tess_get_unlv_text(m_handle);
        if (!text) return "";
        std::string s(text);
        tess_free_text(text);
        return s;
    }

    std::string get_json_text() const {
        char* text = tess_get_json_text(m_handle);
        if (!text) return "{}";
        std::string s(text);
        tess_free_text(text);
        return s;
    }

    int get_mean_confidence() const {
        return tess_get_mean_confidence(m_handle);
    }

    bool detect_orientation_script(int& orient_deg, float& orient_conf, std::string& script_name, float& script_conf) {
        char s_buf[64] = {0};
        int res = tess_detect_orientation_script(m_handle, &orient_deg, &orient_conf, s_buf, sizeof(s_buf), &script_conf);
        if (res == 0) {
            script_name = s_buf;
            return true;
        }
        return false;
    }

    std::unique_ptr<TesseractIterator> analyse_layout() {
        TessIteratorHandle iter = tess_analyse_layout(m_handle);
        if (!iter) return nullptr;
        return std::make_unique<TesseractIterator>(iter);
    }

    std::unique_ptr<TesseractIterator> get_iterator() {
        TessIteratorHandle iter = tess_get_iterator(m_handle);
        if (!iter) return nullptr;
        return std::make_unique<TesseractIterator>(iter);
    }

    static std::string version() {
        return tess_version();
    }

    TessEngineHandle raw_handle() const { return m_handle; }

private:
    TessEngineHandle m_handle = nullptr;
};

class ModelManager {
public:
    static bool set_path(const std::string& path) {
        return tess_model_set_path(path.c_str()) == 0;
    }

    static std::string get_path() {
        char buf[512] = {0};
        tess_model_get_path(buf, sizeof(buf));
        return std::string(buf);
    }

    static std::string get_default_path() {
        char buf[512] = {0};
        tess_model_get_default_path(buf, sizeof(buf));
        return std::string(buf);
    }

    static void set_flavor(TessModelType type) {
        tess_model_set_flavor(static_cast<int>(type));
    }

    static TessModelType get_flavor() {
        return static_cast<TessModelType>(tess_model_get_flavor());
    }

    static std::string get_flavor_path(TessModelType type) {
        char buf[512] = {0};
        tess_model_get_flavor_path(static_cast<int>(type), buf, sizeof(buf));
        return std::string(buf);
    }

    static bool is_installed(const std::string& model_name, TessModelType type = TESS_MODEL_TYPE_FAST) {
        return tess_model_is_installed(model_name.c_str(), static_cast<int>(type)) != 0;
    }

    static int get_catalog_count(int model_type = -1) {
        return tess_model_get_catalog_count(model_type);
    }

    static bool get_catalog_item(int model_type, int index, TessModelInfo& out_info) {
        return tess_model_get_catalog_item(model_type, index, &out_info) == 0;
    }

    static bool download(const std::string& model_name, TessModelType type,
                         TessDownloadProgressCallback cb = nullptr, void* user_data = nullptr) {
        return tess_model_download(model_name.c_str(), static_cast<int>(type), cb, user_data) == 0;
    }

    static std::vector<std::string> get_installed_models() {
        std::vector<std::string> list;
        int count = tess_model_get_installed_count();
        char buf[128] = {0};
        for (int i = 0; i < count; ++i) {
            if (tess_model_get_installed_item(i, buf, sizeof(buf)) == 0) {
                list.emplace_back(buf);
            }
        }
        return list;
    }
};

} // namespace accsify

namespace accsi = accsify;

#endif /* ACCSIFY_TESSERACT_ENGINE_CPP_HPP */
