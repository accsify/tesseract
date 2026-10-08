@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo  Accsify Tesseract Engine Standalone Monolithic DLL Builder
echo  Target: Windows x64 ^& x86 (/MT Zero-Dependency Static Runtime)
echo =====================================================================

set "PROJECT_ROOT=%~dp0"
set "BUILD_DIR=%PROJECT_ROOT%build"
set "DIST_DIR=%PROJECT_ROOT%dist"
set "BIN_DIR=%PROJECT_ROOT%bin"
set "INCLUDE_DIR=%PROJECT_ROOT%include"

set "TARGET_ARCH=%~1"
if "%TARGET_ARCH%"=="" set "TARGET_ARCH=all"

:: Handle clean command
if /i "%TARGET_ARCH%"=="clean" (
    echo [*] Cleaning build and distribution directories...
    if exist "%BUILD_DIR%" rd /s /q "%BUILD_DIR%"
    if exist "%DIST_DIR%" rd /s /q "%DIST_DIR%"
    if exist "%PROJECT_ROOT%build_x64" rd /s /q "%PROJECT_ROOT%build_x64"
    echo [OK] Clean completed.
    exit /b 0
)

:: ---------------------------------------------------------------------
:: 1. Auto-detect Visual Studio Installation
:: ---------------------------------------------------------------------
echo [*] Detecting Visual Studio C++ build environment...

set "VCVARS_BAT="

:: Check vswhere.exe in standard locations
set "VSWHERE_PATH=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE_PATH%" (
    set "VSWHERE_PATH=%ProgramFiles%\Microsoft Visual Studio\Installer\vswhere.exe"
)

if exist "%VSWHERE_PATH%" (
    for /f "usebackq tokens=*" %%i in (`"%VSWHERE_PATH%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do (
        if exist "%%i\VC\Auxiliary\Build\vcvarsall.bat" (
            set "VCVARS_BAT=%%i\VC\Auxiliary\Build\vcvarsall.bat"
            echo [OK] Found Visual Studio via vswhere: %%i
        )
    )
)

:: Fallback standard directories if vswhere did not resolve
if "%VCVARS_BAT%"=="" (
    for %%p in (
        "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat"
        "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
        "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvarsall.bat"
        "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat"
        "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat"
        "C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\VC\Auxiliary\Build\vcvarsall.bat"
        "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build\vcvarsall.bat"
        "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat"
    ) do (
        if "%VCVARS_BAT%"=="" if exist %%p (
            set "VCVARS_BAT=%%~p"
            echo [OK] Found Visual Studio at: %%~p
        )
    )
)

if "%VCVARS_BAT%"=="" (
    echo [ERROR] Could not automatically detect Visual Studio with C++ tools!
    echo         Please ensure Visual Studio 2017/2019/2022 or newer is installed.
    exit /b 1
)

:: Ensure distribution folders exist
if not exist "%DIST_DIR%\x64" mkdir "%DIST_DIR%\x64"
if not exist "%DIST_DIR%\x86" mkdir "%DIST_DIR%\x86"
if not exist "%DIST_DIR%\include" mkdir "%DIST_DIR%\include"

:: Copy header files to dist\include
copy /y "%INCLUDE_DIR%\*.h*" "%DIST_DIR%\include\" >nul

:: ---------------------------------------------------------------------
:: 2. Build x64 Target
:: ---------------------------------------------------------------------
if /i "%TARGET_ARCH%"=="all" goto BUILD_X64
if /i "%TARGET_ARCH%"=="x64" goto BUILD_X64
goto CHECK_X86

:BUILD_X64
echo.
echo =====================================================================
echo  Building x64 Release (tesseract_engine.dll)
echo =====================================================================

call "%VCVARS_BAT%" x64
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to initialize x64 environment!
    exit /b 1
)

if not exist "%BUILD_DIR%\x64" mkdir "%BUILD_DIR%\x64"

cmake -B "%BUILD_DIR%\x64" -G "Ninja" -DCMAKE_BUILD_TYPE=Release "%PROJECT_ROOT%"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] CMake configuration failed for x64!
    exit /b 1
)

cmake --build "%BUILD_DIR%\x64" --config Release
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Build compilation failed for x64!
    exit /b 1
)

:: Copy x64 outputs to dist\x64 and bin\x64
if not exist "%BIN_DIR%\x64" mkdir "%BIN_DIR%\x64"
copy /y "%BIN_DIR%\x64\tesseract_engine.dll" "%DIST_DIR%\x64\" >nul
copy /y "%BIN_DIR%\x64\tesseract_engine.lib" "%DIST_DIR%\x64\" >nul
if exist "%BIN_DIR%\x64\tesseract_cli.exe" copy /y "%BIN_DIR%\x64\tesseract_cli.exe" "%DIST_DIR%\x64\" >nul
echo [OK] x64 binary created: %DIST_DIR%\x64\tesseract_engine.dll
if exist "%DIST_DIR%\x64\tesseract_cli.exe" echo [OK] x64 CLI created:    %DIST_DIR%\x64\tesseract_cli.exe

if /i "%TARGET_ARCH%"=="x64" goto FINISH

:CHECK_X86
if /i "%TARGET_ARCH%"=="all" goto BUILD_X86
if /i "%TARGET_ARCH%"=="x86" goto BUILD_X86
goto FINISH

:BUILD_X86
echo.
echo =====================================================================
echo  Building x86 Release (tesseract_engine.dll)
echo =====================================================================

call "%VCVARS_BAT%" x86
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to initialize x86 environment!
    exit /b 1
)

if not exist "%BUILD_DIR%\x86" mkdir "%BUILD_DIR%\x86"

cmake -B "%BUILD_DIR%\x86" -G "Ninja" -DCMAKE_BUILD_TYPE=Release "%PROJECT_ROOT%"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] CMake configuration failed for x86!
    exit /b 1
)

cmake --build "%BUILD_DIR%\x86" --config Release
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Build compilation failed for x86!
    exit /b 1
)

:: Copy x86 outputs to dist\x86 and bin\x86
if not exist "%BIN_DIR%\x86" mkdir "%BIN_DIR%\x86"
copy /y "%BIN_DIR%\x86\tesseract_engine.dll" "%DIST_DIR%\x86\" >nul
copy /y "%BIN_DIR%\x86\tesseract_engine.lib" "%DIST_DIR%\x86\" >nul
if exist "%BIN_DIR%\x86\tesseract_cli.exe" copy /y "%BIN_DIR%\x86\tesseract_cli.exe" "%DIST_DIR%\x86\" >nul
echo [OK] x86 binary created: %DIST_DIR%\x86\tesseract_engine.dll
if exist "%DIST_DIR%\x86\tesseract_cli.exe" echo [OK] x86 CLI created:    %DIST_DIR%\x86\tesseract_cli.exe

:: Sync to python package lib directory
set "PY_LIB_DIR=%PROJECT_ROOT%python\accsify_tesseract\lib"
if not exist "%PY_LIB_DIR%\x64" mkdir "%PY_LIB_DIR%\x64"
if not exist "%PY_LIB_DIR%\x86" mkdir "%PY_LIB_DIR%\x86"
if exist "%DIST_DIR%\x64\tesseract_engine.dll" copy /y "%DIST_DIR%\x64\*.*" "%PY_LIB_DIR%\x64\" >nul
if exist "%DIST_DIR%\x86\tesseract_engine.dll" copy /y "%DIST_DIR%\x86\*.*" "%PY_LIB_DIR%\x86\" >nul

:FINISH
echo.
echo =====================================================================
echo  BUILD SUCCESSFUL!
echo =====================================================================
echo  Final Deliverables located in:
echo   [x64 DLL] %DIST_DIR%\x64\tesseract_engine.dll
echo   [x86 DLL] %DIST_DIR%\x86\tesseract_engine.dll
echo   [Headers] %DIST_DIR%\include\include.h
echo =====================================================================
exit /b 0
