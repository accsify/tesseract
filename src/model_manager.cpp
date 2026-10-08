/**
 * @file model_manager.cpp
 * @brief Model path management, catalog queries, and download dispatching.
 * @company accsi
 * @copyright Copyright (C) 2026 accsi. All rights reserved.
 */

#include "tesseract_engine.h"
#include "model_catalog_data.h"
#include <windows.h>
#include <shlwapi.h>
#include <string>
#include <vector>
#include <mutex>
#include <memory>
#include <cstring>
#include <algorithm>

#pragma comment(lib, "shlwapi.lib")

namespace accsi {

int perform_download(
    const std::string& url_str,
    const std::string& dest_path,
    const std::string& model_name,
    int model_type,
    TessDownloadProgressCallback cb,
    void* user_data,
    std::atomic<bool>* cancel_flag
);

struct AsyncDownloadContext {
    std::atomic<bool> cancelled{false};
    std::thread worker;
};

class ModelManagerImpl {
public:
    static ModelManagerImpl& instance() {
        static ModelManagerImpl s_inst;
        return s_inst;
    }

    std::string get_default_path() {
        char dll_path[MAX_PATH] = {0};
        HMODULE hModule = NULL;
        GetModuleHandleExA(
            GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
            (LPCSTR)&tess_version,
            &hModule
        );

        if (GetModuleFileNameA(hModule, dll_path, MAX_PATH) > 0) {
            PathRemoveFileSpecA(dll_path);
            PathAppendA(dll_path, "tessdata");
            return std::string(dll_path);
        }
        return ".\\tessdata";
    }

    std::string get_active_path() {
        std::lock_guard<std::mutex> lock(m_mutex);
        if (m_custom_path.empty()) {
            return get_default_path();
        }
        return m_custom_path;
    }

    void set_active_path(const std::string& path) {
        std::lock_guard<std::mutex> lock(m_mutex);
        m_custom_path = path;
    }

    void ensure_directory(const std::string& path) {
        CreateDirectoryA(path.c_str(), NULL);
    }

    std::string get_model_filename(const std::string& model_name) {
        std::string fname = model_name;
        // If script/Arabic -> script\\Arabic
        std::replace(fname.begin(), fname.end(), '/', '\\');
        if (fname.size() < 12 || fname.substr(fname.size() - 12) != ".traineddata") {
            fname += ".traineddata";
        }
        return fname;
    }

    std::string get_full_model_path(const std::string& model_name) {
        std::string dir = get_active_path();
        std::string rel = get_model_filename(model_name);

        char combined[MAX_PATH] = {0};
        PathCombineA(combined, dir.c_str(), rel.c_str());
        return std::string(combined);
    }

    bool is_installed(const std::string& model_name) {
        std::string full_path = get_full_model_path(model_name);
        DWORD attr = GetFileAttributesA(full_path.c_str());
        return (attr != INVALID_FILE_ATTRIBUTES && !(attr & FILE_ATTRIBUTE_DIRECTORY));
    }

    std::vector<const CatalogEntry*> filter_catalog(int model_type) {
        std::vector<const CatalogEntry*> filtered;
        for (size_t i = 0; i < g_model_catalog_size; ++i) {
            if (model_type == -1 || g_model_catalog[i].model_type == model_type) {
                filtered.push_back(&g_model_catalog[i]);
            }
        }
        return filtered;
    }

    const CatalogEntry* find_catalog_entry(const std::string& model_name, int model_type) {
        for (size_t i = 0; i < g_model_catalog_size; ++i) {
            if (g_model_catalog[i].name == model_name) {
                if (model_type == -1 || g_model_catalog[i].model_type == model_type) {
                    return &g_model_catalog[i];
                }
            }
        }
        return nullptr;
    }

    std::vector<std::string> scan_installed() {
        std::vector<std::string> results;
        std::string base_dir = get_active_path();
        std::string search_pattern = base_dir + "\\*.traineddata";

        WIN32_FIND_DATAA fd;
        HANDLE hFind = FindFirstFileA(search_pattern.c_str(), &fd);
        if (hFind != INVALID_HANDLE_VALUE) {
            do {
                if (!(fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) {
                    std::string fname = fd.cFileName;
                    if (fname.size() > 12 && fname.substr(fname.size() - 12) == ".traineddata") {
                        results.push_back(fname.substr(0, fname.size() - 12));
                    }
                }
            } while (FindNextFileA(hFind, &fd));
            FindClose(hFind);
        }

        // Also check script/ subfolder
        std::string script_pattern = base_dir + "\\script\\*.traineddata";
        hFind = FindFirstFileA(script_pattern.c_str(), &fd);
        if (hFind != INVALID_HANDLE_VALUE) {
            do {
                if (!(fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) {
                    std::string fname = fd.cFileName;
                    if (fname.size() > 12 && fname.substr(fname.size() - 12) == ".traineddata") {
                        results.push_back("script/" + fname.substr(0, fname.size() - 12));
                    }
                }
            } while (FindNextFileA(hFind, &fd));
            FindClose(hFind);
        }

        return results;
    }

private:
    ModelManagerImpl() = default;
    std::mutex m_mutex;
    std::string m_custom_path;
};

} // namespace accsi

using namespace accsi;

extern "C" {

TESS_API int TESS_CALL tess_model_set_path(const char* path) {
    if (!path || path[0] == '\0') {
        ModelManagerImpl::instance().set_active_path("");
    } else {
        ModelManagerImpl::instance().set_active_path(path);
    }
    return 0;
}

TESS_API int TESS_CALL tess_model_get_path(char* buffer, int max_len) {
    if (!buffer || max_len <= 0) return -1;
    std::string p = ModelManagerImpl::instance().get_active_path();
    strncpy_s(buffer, max_len, p.c_str(), _TRUNCATE);
    return 0;
}

TESS_API int TESS_CALL tess_model_get_default_path(char* buffer, int max_len) {
    if (!buffer || max_len <= 0) return -1;
    std::string p = ModelManagerImpl::instance().get_default_path();
    strncpy_s(buffer, max_len, p.c_str(), _TRUNCATE);
    return 0;
}

TESS_API int TESS_CALL tess_model_is_installed(const char* model_name, int model_type) {
    (void)model_type;
    if (!model_name) return 0;
    return ModelManagerImpl::instance().is_installed(model_name) ? 1 : 0;
}

TESS_API int TESS_CALL tess_model_get_catalog_count(int model_type) {
    auto filtered = ModelManagerImpl::instance().filter_catalog(model_type);
    return static_cast<int>(filtered.size());
}

TESS_API int TESS_CALL tess_model_get_catalog_item(int model_type, int index, TessModelInfo* out_info) {
    if (!out_info || index < 0) return -1;
    auto filtered = ModelManagerImpl::instance().filter_catalog(model_type);
    if (index >= static_cast<int>(filtered.size())) return -1;

    const CatalogEntry* entry = filtered[index];
    strncpy_s(out_info->name, sizeof(out_info->name), entry->name, _TRUNCATE);
    strncpy_s(out_info->display_name, sizeof(out_info->display_name), entry->display_name, _TRUNCATE);
    out_info->model_type = entry->model_type;
    out_info->file_size = entry->file_size;
    strncpy_s(out_info->download_url, sizeof(out_info->download_url), entry->url, _TRUNCATE);
    out_info->is_installed = ModelManagerImpl::instance().is_installed(entry->name) ? 1 : 0;

    return 0;
}

TESS_API int TESS_CALL tess_model_download(
    const char* model_name,
    int model_type,
    TessDownloadProgressCallback callback,
    void* user_data
) {
    if (!model_name) return -1;
    const CatalogEntry* entry = ModelManagerImpl::instance().find_catalog_entry(model_name, model_type);
    std::string url;
    if (entry) {
        url = entry->url;
    } else {
        // Construct default fallback URL
        if (model_type == TESS_MODEL_TYPE_BEST) {
            url = std::string("https://github.com/tesseract-ocr/tessdata_best/raw/main/") + model_name + ".traineddata";
        } else if (model_type == TESS_MODEL_TYPE_STANDARD) {
            url = std::string("https://github.com/tesseract-ocr/tessdata/raw/main/") + model_name + ".traineddata";
        } else {
            url = std::string("https://github.com/tesseract-ocr/tessdata_fast/raw/main/") + model_name + ".traineddata";
        }
    }

    std::string dest_dir = ModelManagerImpl::instance().get_active_path();
    ModelManagerImpl::instance().ensure_directory(dest_dir);

    // If script/... ensure script/ directory exists
    std::string mname(model_name);
    if (mname.rfind("script/", 0) == 0) {
        std::string script_dir = dest_dir + "\\script";
        ModelManagerImpl::instance().ensure_directory(script_dir);
    }

    std::string full_dest = ModelManagerImpl::instance().get_full_model_path(model_name);
    return perform_download(url, full_dest, model_name, model_type, callback, user_data, nullptr);
}

TESS_API int TESS_CALL tess_model_download_async(
    const char* model_name,
    int model_type,
    TessDownloadProgressCallback callback,
    void* user_data,
    TessDownloadHandle* out_handle
) {
    if (!model_name || !out_handle) return -1;
    auto ctx = new AsyncDownloadContext();
    std::string m_name(model_name);

    ctx->worker = std::thread([ctx, m_name, model_type, callback, user_data]() {
        const CatalogEntry* entry = ModelManagerImpl::instance().find_catalog_entry(m_name, model_type);
        std::string url = entry ? entry->url : ("https://github.com/tesseract-ocr/tessdata_fast/raw/main/" + m_name + ".traineddata");

        std::string dest_dir = ModelManagerImpl::instance().get_active_path();
        ModelManagerImpl::instance().ensure_directory(dest_dir);
        if (m_name.rfind("script/", 0) == 0) {
            ModelManagerImpl::instance().ensure_directory(dest_dir + "\\script");
        }

        std::string full_dest = ModelManagerImpl::instance().get_full_model_path(m_name);
        perform_download(url, full_dest, m_name, model_type, callback, user_data, &ctx->cancelled);
    });

    *out_handle = reinterpret_cast<TessDownloadHandle>(ctx);
    return 0;
}

TESS_API int TESS_CALL tess_model_cancel_download(TessDownloadHandle handle) {
    if (!handle) return -1;
    auto ctx = reinterpret_cast<AsyncDownloadContext*>(handle);
    ctx->cancelled.store(true);
    if (ctx->worker.joinable()) {
        ctx->worker.join();
    }
    delete ctx;
    return 0;
}

TESS_API int TESS_CALL tess_model_get_installed_count(void) {
    auto list = ModelManagerImpl::instance().scan_installed();
    return static_cast<int>(list.size());
}

TESS_API int TESS_CALL tess_model_get_installed_item(int index, char* out_name, int max_len) {
    if (!out_name || max_len <= 0 || index < 0) return -1;
    auto list = ModelManagerImpl::instance().scan_installed();
    if (index >= static_cast<int>(list.size())) return -1;

    strncpy_s(out_name, max_len, list[index].c_str(), _TRUNCATE);
    return 0;
}

} // extern "C"
