/**
 * @file model_manager.cpp
 * @brief Model path management, flavor organization, catalog queries, and download dispatching.
 * @company accsify
 * @copyright Copyright (C) 2026 accsify. All rights reserved.
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
#include <thread>
#include <atomic>

#pragma comment(lib, "shlwapi.lib")

namespace accsify {

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

    void set_flavor(int flavor) {
        std::lock_guard<std::mutex> lock(m_mutex);
        m_flavor = flavor;
    }

    int get_flavor() {
        std::lock_guard<std::mutex> lock(m_mutex);
        return m_flavor;
    }

    std::string get_flavor_subdir(int flavor) {
        switch (flavor) {
            case TESS_MODEL_TYPE_FAST:     return "fast";
            case TESS_MODEL_TYPE_BEST:     return "best";
            case TESS_MODEL_TYPE_STANDARD: return "standard";
            case TESS_MODEL_TYPE_SCRIPT:   return "script";
            default:                       return "fast";
        }
    }

    std::string get_flavor_dir(int flavor) {
        std::string base = get_active_path();
        char combined[MAX_PATH] = {0};
        std::string sub = get_flavor_subdir(flavor);
        PathCombineA(combined, base.c_str(), sub.c_str());
        return std::string(combined);
    }

    void ensure_directory(const std::string& path) {
        if (path.empty()) return;
        char temp[MAX_PATH] = {0};
        strncpy_s(temp, sizeof(temp), path.c_str(), _TRUNCATE);
        for (char* p = temp + 1; *p; ++p) {
            if (*p == '\\' || *p == '/') {
                char orig = *p;
                *p = '\0';
                CreateDirectoryA(temp, NULL);
                *p = orig;
            }
        }
        CreateDirectoryA(temp, NULL);
    }

    std::string normalize_model_basename(const std::string& model_name) {
        std::string fname = model_name;
        if (fname.rfind("script/", 0) == 0) {
            fname = fname.substr(7);
        } else if (fname.rfind("script\\", 0) == 0) {
            fname = fname.substr(7);
        }
        if (fname.size() < 12 || fname.substr(fname.size() - 12) != ".traineddata") {
            fname += ".traineddata";
        }
        return fname;
    }

    std::string get_full_model_path_for_storage(const std::string& model_name, int model_type) {
        std::string base = get_active_path();
        std::string fname = normalize_model_basename(model_name);

        char combined[MAX_PATH] = {0};
        if (model_name.rfind("script/", 0) == 0 || model_name.rfind("script\\", 0) == 0 || model_type == TESS_MODEL_TYPE_SCRIPT) {
            std::string s_dir = base + "\\script";
            PathCombineA(combined, s_dir.c_str(), fname.c_str());
        } else {
            std::string sub = get_flavor_subdir(model_type);
            std::string sub_dir = base + "\\" + sub;
            PathCombineA(combined, sub_dir.c_str(), fname.c_str());
        }
        return std::string(combined);
    }

    bool file_exists(const std::string& full_path) {
        DWORD attr = GetFileAttributesA(full_path.c_str());
        return (attr != INVALID_FILE_ATTRIBUTES && !(attr & FILE_ATTRIBUTE_DIRECTORY));
    }

    bool is_installed(const std::string& model_name, int model_type = -1) {
        std::string base = get_active_path();
        std::string fname = normalize_model_basename(model_name);

        // 1. Check in specific flavor subdirectory if specified
        if (model_type >= 0) {
            std::string flavor_path = get_full_model_path_for_storage(model_name, model_type);
            if (file_exists(flavor_path)) return true;
        }

        // 2. Check current active flavor
        {
            std::string cur_flavor_path = get_full_model_path_for_storage(model_name, get_flavor());
            if (file_exists(cur_flavor_path)) return true;
        }

        // 3. Check flat base directory
        char flat_combined[MAX_PATH] = {0};
        PathCombineA(flat_combined, base.c_str(), fname.c_str());
        if (file_exists(flat_combined)) return true;

        // 4. Check script subdirectory if applicable
        char script_combined[MAX_PATH] = {0};
        std::string script_dir = base + "\\script";
        PathCombineA(script_combined, script_dir.c_str(), fname.c_str());
        if (file_exists(script_combined)) return true;

        // 5. Check other flavors
        for (int t = 0; t <= 3; ++t) {
            std::string other_path = get_full_model_path_for_storage(model_name, t);
            if (file_exists(other_path)) return true;
        }

        return false;
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

    static void scan_directory_models(const std::string& dir_path, const std::string& prefix, std::vector<std::string>& results) {
        std::string search_pattern = dir_path + "\\*.traineddata";
        WIN32_FIND_DATAA fd;
        HANDLE hFind = FindFirstFileA(search_pattern.c_str(), &fd);
        if (hFind != INVALID_HANDLE_VALUE) {
            do {
                if (!(fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) {
                    std::string fname = fd.cFileName;
                    if (fname.size() > 12 && fname.substr(fname.size() - 12) == ".traineddata") {
                        std::string base_id = fname.substr(0, fname.size() - 12);
                        if (!prefix.empty()) {
                            results.push_back(prefix + "/" + base_id);
                        } else {
                            results.push_back(base_id);
                        }
                    }
                }
            } while (FindNextFileA(hFind, &fd));
            FindClose(hFind);
        }
    }

    std::vector<std::string> scan_installed() {
        std::vector<std::string> results;
        std::string base_dir = get_active_path();

        // 1. Root tessdata
        scan_directory_models(base_dir, "", results);

        // 2. Flavor subdirectories
        scan_directory_models(base_dir + "\\fast", "fast", results);
        scan_directory_models(base_dir + "\\best", "best", results);
        scan_directory_models(base_dir + "\\standard", "standard", results);
        scan_directory_models(base_dir + "\\script", "script", results);

        return results;
    }

private:
    ModelManagerImpl() : m_flavor(TESS_MODEL_TYPE_FAST) {}
    std::mutex m_mutex;
    std::string m_custom_path;
    int m_flavor;
};

} // namespace accsify

using namespace accsify;

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

TESS_API void TESS_CALL tess_model_set_flavor(int model_type) {
    ModelManagerImpl::instance().set_flavor(model_type);
}

TESS_API int TESS_CALL tess_model_get_flavor(void) {
    return ModelManagerImpl::instance().get_flavor();
}

TESS_API int TESS_CALL tess_model_get_flavor_path(int model_type, char* buffer, int max_len) {
    if (!buffer || max_len <= 0) return -1;
    std::string p = ModelManagerImpl::instance().get_flavor_dir(model_type);
    strncpy_s(buffer, max_len, p.c_str(), _TRUNCATE);
    return 0;
}

TESS_API int TESS_CALL tess_model_is_installed(const char* model_name, int model_type) {
    if (!model_name) return 0;
    return ModelManagerImpl::instance().is_installed(model_name, model_type) ? 1 : 0;
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
    out_info->is_installed = ModelManagerImpl::instance().is_installed(entry->name, entry->model_type) ? 1 : 0;

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
        // Construct fallback URL based on type
        std::string basename = ModelManagerImpl::instance().normalize_model_basename(model_name);
        if (model_type == TESS_MODEL_TYPE_BEST) {
            url = std::string("https://github.com/tesseract-ocr/tessdata_best/raw/main/") + basename;
        } else if (model_type == TESS_MODEL_TYPE_STANDARD) {
            url = std::string("https://github.com/tesseract-ocr/tessdata/raw/main/") + basename;
        } else {
            url = std::string("https://github.com/tesseract-ocr/tessdata_fast/raw/main/") + basename;
        }
    }

    std::string full_dest = ModelManagerImpl::instance().get_full_model_path_for_storage(model_name, model_type);
    char dir_only[MAX_PATH] = {0};
    strncpy_s(dir_only, sizeof(dir_only), full_dest.c_str(), _TRUNCATE);
    PathRemoveFileSpecA(dir_only);
    ModelManagerImpl::instance().ensure_directory(dir_only);

    int dl_res = perform_download(url, full_dest, model_name, model_type, callback, user_data, nullptr);
    if (dl_res == 0) {
        // Also copy to root tessdata if it doesn't exist yet, guaranteeing single-path fallback
        std::string base = ModelManagerImpl::instance().get_active_path();
        std::string fname = ModelManagerImpl::instance().normalize_model_basename(model_name);
        char flat_dest[MAX_PATH] = {0};
        PathCombineA(flat_dest, base.c_str(), fname.c_str());
        if (!ModelManagerImpl::instance().file_exists(flat_dest)) {
            CopyFileA(full_dest.c_str(), flat_dest, FALSE);
        }
    }
    return dl_res;
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
        std::string url;
        if (entry) {
            url = entry->url;
        } else {
            std::string basename = ModelManagerImpl::instance().normalize_model_basename(m_name);
            if (model_type == TESS_MODEL_TYPE_BEST) {
                url = std::string("https://github.com/tesseract-ocr/tessdata_best/raw/main/") + basename;
            } else if (model_type == TESS_MODEL_TYPE_STANDARD) {
                url = std::string("https://github.com/tesseract-ocr/tessdata/raw/main/") + basename;
            } else {
                url = std::string("https://github.com/tesseract-ocr/tessdata_fast/raw/main/") + basename;
            }
        }

        std::string full_dest = ModelManagerImpl::instance().get_full_model_path_for_storage(m_name, model_type);
        char dir_only[MAX_PATH] = {0};
        strncpy_s(dir_only, sizeof(dir_only), full_dest.c_str(), _TRUNCATE);
        PathRemoveFileSpecA(dir_only);
        ModelManagerImpl::instance().ensure_directory(dir_only);

        int dl_res = perform_download(url, full_dest, m_name, model_type, callback, user_data, &ctx->cancelled);
        if (dl_res == 0) {
            std::string base = ModelManagerImpl::instance().get_active_path();
            std::string fname = ModelManagerImpl::instance().normalize_model_basename(m_name);
            char flat_dest[MAX_PATH] = {0};
            PathCombineA(flat_dest, base.c_str(), fname.c_str());
            if (!ModelManagerImpl::instance().file_exists(flat_dest)) {
                CopyFileA(full_dest.c_str(), flat_dest, FALSE);
            }
        }
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
