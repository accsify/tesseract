@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo  Accsi Tesseract Source Updater / Downloader
echo =====================================================================

set "TESSERACT_VERSION=%~1"
if "%TESSERACT_VERSION%"=="" (
    set "TESSERACT_VERSION=5.5.0"
)

set "LEPTONICA_VERSION=%~2"
if "%LEPTONICA_VERSION%"=="" (
    set "LEPTONICA_VERSION=1.84.1"
)

set "ROOT_DIR=%~dp0"
if exist "%ROOT_DIR%..\deps" (
    set "DEPS_DIR=%ROOT_DIR%..\deps"
) else (
    set "DEPS_DIR=%ROOT_DIR%deps"
)

if not exist "%DEPS_DIR%" (
    mkdir "%DEPS_DIR%"
)

echo [*] Target Tesseract Version : %TESSERACT_VERSION%
echo [*] Target Leptonica Version : %LEPTONICA_VERSION%
echo [*] Dependencies Directory   : %DEPS_DIR%
echo.

where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git is not installed or not in PATH! Please install Git.
    exit /b 1
)

:: ---------------------------------------------------------------------
:: 1. Leptonica
:: ---------------------------------------------------------------------
echo [*] Updating Leptonica source repository...
if exist "%DEPS_DIR%\leptonica\.git" (
    pushd "%DEPS_DIR%\leptonica"
    git fetch --tags --depth 1 origin %LEPTONICA_VERSION%
    git checkout %LEPTONICA_VERSION%
    popd
) else (
    if exist "%DEPS_DIR%\leptonica" rd /s /q "%DEPS_DIR%\leptonica"
    git clone --depth 1 --branch %LEPTONICA_VERSION% https://github.com/DanBloomberg/leptonica.git "%DEPS_DIR%\leptonica"
)

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to fetch Leptonica %LEPTONICA_VERSION%!
    exit /b 1
)
echo [OK] Leptonica is up to date.
echo.

:: ---------------------------------------------------------------------
:: 2. Tesseract
:: ---------------------------------------------------------------------
echo [*] Updating Tesseract OCR source repository...
if exist "%DEPS_DIR%\tesseract\.git" (
    pushd "%DEPS_DIR%\tesseract"
    git fetch --tags --depth 1 origin %TESSERACT_VERSION%
    git checkout %TESSERACT_VERSION%
    popd
) else (
    if exist "%DEPS_DIR%\tesseract" rd /s /q "%DEPS_DIR%\tesseract"
    git clone --depth 1 --branch %TESSERACT_VERSION% https://github.com/tesseract-ocr/tesseract.git "%DEPS_DIR%\tesseract"
)

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to fetch Tesseract %TESSERACT_VERSION%!
    exit /b 1
)
echo [OK] Tesseract is up to date.
echo.

echo =====================================================================
echo  Source update completed successfully!
echo =====================================================================
exit /b 0
