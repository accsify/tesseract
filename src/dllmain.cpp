/**
 * @file dllmain.cpp
 * @brief Dynamic Link Library entry point for Accsi Tesseract OCR Engine.
 * @company accsi
 * @copyright Copyright (C) 2026 accsi. All rights reserved.
 */

#include <windows.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    (void)lpReserved;
    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
        DisableThreadLibraryCalls(hModule);
        break;
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
