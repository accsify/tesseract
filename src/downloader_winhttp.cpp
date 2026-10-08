/**
 * @file downloader_winhttp.cpp
 * @brief Native Windows WinHTTP streaming downloader with live progress and cancellation.
 * @company accsi
 * @copyright Copyright (C) 2026 accsi. All rights reserved.
 */

#include "tesseract_engine.h"
#include <windows.h>
#include <winhttp.h>
#include <string>
#include <vector>
#include <atomic>
#include <thread>
#include <memory>
#include <fstream>
#include <iostream>

#pragma comment(lib, "winhttp.lib")

namespace accsi {

struct DownloadTask {
    std::atomic<bool> cancelled{false};
    std::thread worker;
    std::string model_name;
    int model_type = 0;
    std::string target_file;
    std::string url;
    TessDownloadProgressCallback callback = nullptr;
    void* user_data = nullptr;
    int result_code = 0;
};

static std::wstring to_wide(const std::string& str) {
    if (str.empty()) return std::wstring();
    int size = MultiByteToWideChar(CP_UTF8, 0, str.c_str(), -1, NULL, 0);
    std::wstring wstr(size - 1, 0);
    MultiByteToWideChar(CP_UTF8, 0, str.c_str(), -1, &wstr[0], size);
    return wstr;
}

static bool parse_url(const std::string& url_str, std::wstring& host, std::wstring& path, INTERNET_PORT& port, bool& is_https) {
    std::wstring w_url = to_wide(url_str);
    URL_COMPONENTS urlComp = {0};
    urlComp.dwStructSize = sizeof(urlComp);
    urlComp.dwHostNameLength = (DWORD)-1;
    urlComp.dwUrlPathLength = (DWORD)-1;
    urlComp.dwExtraInfoLength = (DWORD)-1;

    if (!WinHttpCrackUrl(w_url.c_str(), (DWORD)w_url.length(), 0, &urlComp)) {
        return false;
    }

    host = std::wstring(urlComp.lpszHostName, urlComp.dwHostNameLength);
    path = std::wstring(urlComp.lpszUrlPath, urlComp.dwUrlPathLength);
    if (urlComp.dwExtraInfoLength > 0) {
        path += std::wstring(urlComp.lpszExtraInfo, urlComp.dwExtraInfoLength);
    }
    port = urlComp.nPort;
    is_https = (urlComp.nScheme == INTERNET_SCHEME_HTTPS);
    return true;
}

int perform_download(
    const std::string& url_str,
    const std::string& dest_path,
    const std::string& model_name,
    int model_type,
    TessDownloadProgressCallback cb,
    void* user_data,
    std::atomic<bool>* cancel_flag
) {
    std::string current_url = url_str;
    int redirect_count = 0;
    const int max_redirects = 8;

    while (redirect_count < max_redirects) {
        if (cancel_flag && cancel_flag->load()) {
            if (cb) cb(model_name.c_str(), model_type, 0, 0, 0.0, "Cancelled", user_data);
            return -2;
        }

        std::wstring host, path;
        INTERNET_PORT port = INTERNET_DEFAULT_HTTPS_PORT;
        bool is_https = true;

        if (!parse_url(current_url, host, path, port, is_https)) {
            if (cb) cb(model_name.c_str(), model_type, 0, 0, 0.0, "Invalid URL", user_data);
            return -1;
        }

        HINTERNET hSession = WinHttpOpen(
            L"Accsi-Tesseract-Downloader/5.5 (Windows NT)",
            WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
            WINHTTP_NO_PROXY_NAME,
            WINHTTP_NO_PROXY_BYPASS,
            0
        );

        if (!hSession) return -1;

        // Enable TLS 1.2 and 1.3
        DWORD secureProtocols = WINHTTP_FLAG_SECURE_PROTOCOL_TLS1_2 | WINHTTP_FLAG_SECURE_PROTOCOL_TLS1_3;
        WinHttpSetOption(hSession, WINHTTP_OPTION_SECURE_PROTOCOLS, &secureProtocols, sizeof(secureProtocols));

        // Set timeouts (connect, send, receive)
        WinHttpSetTimeouts(hSession, 15000, 15000, 30000, 60000);

        HINTERNET hConnect = WinHttpConnect(hSession, host.c_str(), port, 0);
        if (!hConnect) {
            WinHttpCloseHandle(hSession);
            return -1;
        }

        DWORD req_flags = is_https ? WINHTTP_FLAG_SECURE : 0;
        HINTERNET hRequest = WinHttpOpenRequest(
            hConnect,
            L"GET",
            path.c_str(),
            NULL,
            WINHTTP_NO_REFERER,
            WINHTTP_DEFAULT_ACCEPT_TYPES,
            req_flags
        );

        if (!hRequest) {
            WinHttpCloseHandle(hConnect);
            WinHttpCloseHandle(hSession);
            return -1;
        }

        // Configure redirects
        DWORD redirectPolicy = WINHTTP_OPTION_REDIRECT_POLICY_ALWAYS;
        WinHttpSetOption(hRequest, WINHTTP_OPTION_REDIRECT_POLICY, &redirectPolicy, sizeof(redirectPolicy));

        if (!WinHttpSendRequest(hRequest, WINHTTP_NO_ADDITIONAL_HEADERS, 0, WINHTTP_NO_REQUEST_DATA, 0, 0, 0)) {
            WinHttpCloseHandle(hRequest);
            WinHttpCloseHandle(hConnect);
            WinHttpCloseHandle(hSession);
            return -1;
        }

        if (!WinHttpReceiveResponse(hRequest, NULL)) {
            WinHttpCloseHandle(hRequest);
            WinHttpCloseHandle(hConnect);
            WinHttpCloseHandle(hSession);
            return -1;
        }

        DWORD statusCode = 0;
        DWORD statusSize = sizeof(statusCode);
        WinHttpQueryHeaders(hRequest, WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER,
                            WINHTTP_HEADER_NAME_BY_INDEX, &statusCode, &statusSize, WINHTTP_NO_HEADER_INDEX);

        // Handle redirects if WinHTTP did not follow automatically
        if (statusCode == 301 || statusCode == 302 || statusCode == 307 || statusCode == 308) {
            DWORD locSize = 0;
            WinHttpQueryHeaders(hRequest, WINHTTP_QUERY_LOCATION, WINHTTP_HEADER_NAME_BY_INDEX, NULL, &locSize, WINHTTP_NO_HEADER_INDEX);
            if (GetLastError() == ERROR_INSUFFICIENT_BUFFER && locSize > 0) {
                std::vector<wchar_t> locBuf(locSize / sizeof(wchar_t) + 1, 0);
                if (WinHttpQueryHeaders(hRequest, WINHTTP_QUERY_LOCATION, WINHTTP_HEADER_NAME_BY_INDEX, locBuf.data(), &locSize, WINHTTP_NO_HEADER_INDEX)) {
                    int utf8_size = WideCharToMultiByte(CP_UTF8, 0, locBuf.data(), -1, NULL, 0, NULL, NULL);
                    std::string new_url(utf8_size - 1, 0);
                    WideCharToMultiByte(CP_UTF8, 0, locBuf.data(), -1, &new_url[0], utf8_size, NULL, NULL);
                    current_url = new_url;
                    redirect_count++;
                    WinHttpCloseHandle(hRequest);
                    WinHttpCloseHandle(hConnect);
                    WinHttpCloseHandle(hSession);
                    continue;
                }
            }
        }

        if (statusCode != 200) {
            if (cb) {
                std::string msg = "HTTP Error " + std::to_string(statusCode);
                cb(model_name.c_str(), model_type, 0, 0, 0.0, msg.c_str(), user_data);
            }
            WinHttpCloseHandle(hRequest);
            WinHttpCloseHandle(hConnect);
            WinHttpCloseHandle(hSession);
            return -1;
        }

        // Query Content-Length
        int64_t total_bytes = -1;
        wchar_t clBuf[64] = {0};
        DWORD clSize = sizeof(clBuf);
        if (WinHttpQueryHeaders(hRequest, WINHTTP_QUERY_CONTENT_LENGTH, WINHTTP_HEADER_NAME_BY_INDEX, clBuf, &clSize, WINHTTP_NO_HEADER_INDEX)) {
            total_bytes = _wtoi64(clBuf);
        }

        std::string temp_path = dest_path + ".tmp";
        HANDLE hFile = CreateFileA(temp_path.c_str(), GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (hFile == INVALID_HANDLE_VALUE) {
            if (cb) cb(model_name.c_str(), model_type, 0, 0, 0.0, "Cannot create destination file", user_data);
            WinHttpCloseHandle(hRequest);
            WinHttpCloseHandle(hConnect);
            WinHttpCloseHandle(hSession);
            return -1;
        }

        const DWORD buffer_size = 65536; // 64 KB chunk
        std::vector<char> buffer(buffer_size);
        int64_t downloaded_bytes = 0;
        bool aborted = false;

        while (true) {
            if (cancel_flag && cancel_flag->load()) {
                aborted = true;
                break;
            }

            DWORD bytes_available = 0;
            if (!WinHttpQueryDataAvailable(hRequest, &bytes_available)) {
                break;
            }
            if (bytes_available == 0) {
                break; // Complete
            }

            DWORD bytes_to_read = (std::min)(bytes_available, buffer_size);
            DWORD bytes_read = 0;
            if (!WinHttpReadData(hRequest, buffer.data(), bytes_to_read, &bytes_read) || bytes_read == 0) {
                break;
            }

            DWORD bytes_written = 0;
            if (!WriteFile(hFile, buffer.data(), bytes_read, &bytes_written, NULL) || bytes_written != bytes_read) {
                aborted = true;
                break;
            }

            downloaded_bytes += bytes_read;
            double percentage = 0.0;
            if (total_bytes > 0) {
                percentage = (double)downloaded_bytes * 100.0 / (double)total_bytes;
                if (percentage > 100.0) percentage = 100.0;
            }

            if (cb) {
                int user_cancel = cb(model_name.c_str(), model_type, downloaded_bytes, total_bytes, percentage, "Downloading", user_data);
                if (user_cancel != 0) {
                    aborted = true;
                    break;
                }
            }
        }

        CloseHandle(hFile);
        WinHttpCloseHandle(hRequest);
        WinHttpCloseHandle(hConnect);
        WinHttpCloseHandle(hSession);

        if (aborted) {
            DeleteFileA(temp_path.c_str());
            if (cb) cb(model_name.c_str(), model_type, downloaded_bytes, total_bytes, 0.0, "Aborted", user_data);
            return -2;
        }

        // Rename temp file to final destination
        MoveFileExA(temp_path.c_str(), dest_path.c_str(), MOVEFILE_REPLACE_EXISTING);

        if (cb) {
            cb(model_name.c_str(), model_type, downloaded_bytes, downloaded_bytes, 100.0, "Completed", user_data);
        }

        return 0;
    }

    return -1;
}

} // namespace accsi
