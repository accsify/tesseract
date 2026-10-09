@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo  Accsify Tesseract - PyPI Package Builder and Twine Verifier
echo  Company: accsify
echo  Target: Complete Wheel (.whl) and Source Distribution (.tar.gz)
echo =====================================================================

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: ---------------------------------------------------------------------
:: 1. Verify Python & Prerequisites
:: ---------------------------------------------------------------------
echo [*] Checking Python runtime...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not found in PATH!
    echo         Please install Python 3.8+ and ensure it is added to PATH.
    exit /b 1
)

echo [*] Verifying build, wheel, and twine modules...
python -m build --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python module 'build' is missing! Please install it with: pip install build
    exit /b 1
)
python -m twine --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python module 'twine' is missing! Please install it with: pip install twine
    exit /b 1
)
echo [OK] Python build environment verified.

:: ---------------------------------------------------------------------
:: 2. Auto-Include Native Standalone Binaries (x64 and x86)
:: ---------------------------------------------------------------------
echo.
echo [*] Synchronizing native libraries from dist/ into accsify_tesseract/lib...

set "DIST_ROOT=%SCRIPT_DIR%..\dist"
set "BIN_ROOT=%SCRIPT_DIR%..\bin"
set "PKG_LIB_DIR=%SCRIPT_DIR%accsify_tesseract\lib"

:: Clean any obsolete bin folder from previous runs
if exist "%SCRIPT_DIR%accsify_tesseract\bin" rd /s /q "%SCRIPT_DIR%accsify_tesseract\bin"

if not exist "%PKG_LIB_DIR%\x64" mkdir "%PKG_LIB_DIR%\x64"
if not exist "%PKG_LIB_DIR%\x86" mkdir "%PKG_LIB_DIR%\x86"

:: Check x64
if exist "%DIST_ROOT%\x64\tesseract_engine.dll" (
    copy /y "%DIST_ROOT%\x64\tesseract_engine.dll" "%PKG_LIB_DIR%\x64\" >nul
    copy /y "%DIST_ROOT%\x64\tesseract_cli.exe"    "%PKG_LIB_DIR%\x64\" >nul
    if exist "%DIST_ROOT%\x64\tesseract_engine.lib" copy /y "%DIST_ROOT%\x64\tesseract_engine.lib" "%PKG_LIB_DIR%\x64\" >nul
    echo [OK] x64 native binaries synchronized into accsify_tesseract\lib\x64
) else if exist "%BIN_ROOT%\x64\tesseract_engine.dll" (
    copy /y "%BIN_ROOT%\x64\tesseract_engine.dll" "%PKG_LIB_DIR%\x64\" >nul
    copy /y "%BIN_ROOT%\x64\tesseract_cli.exe"    "%PKG_LIB_DIR%\x64\" >nul
    if exist "%BIN_ROOT%\x64\tesseract_engine.lib" copy /y "%BIN_ROOT%\x64\tesseract_engine.lib" "%PKG_LIB_DIR%\x64\" >nul
    echo [OK] x64 native binaries synchronized from bin\x64
) else (
    echo [WARNING] x64 native binaries not found in %DIST_ROOT%\x64. Please run ..\build.cmd if missing.
)

:: Check x86
if exist "%DIST_ROOT%\x86\tesseract_engine.dll" (
    copy /y "%DIST_ROOT%\x86\tesseract_engine.dll" "%PKG_LIB_DIR%\x86\" >nul
    copy /y "%DIST_ROOT%\x86\tesseract_cli.exe"    "%PKG_LIB_DIR%\x86\" >nul
    if exist "%DIST_ROOT%\x86\tesseract_engine.lib" copy /y "%DIST_ROOT%\x86\tesseract_engine.lib" "%PKG_LIB_DIR%\x86\" >nul
    echo [OK] x86 native binaries synchronized into accsify_tesseract\lib\x86
) else if exist "%BIN_ROOT%\x86\tesseract_engine.dll" (
    copy /y "%BIN_ROOT%\x86\tesseract_engine.dll" "%PKG_LIB_DIR%\x86\" >nul
    copy /y "%BIN_ROOT%\x86\tesseract_cli.exe"    "%PKG_LIB_DIR%\x86\" >nul
    if exist "%BIN_ROOT%\x86\tesseract_engine.lib" copy /y "%BIN_ROOT%\x86\tesseract_engine.lib" "%PKG_LIB_DIR%\x86\" >nul
    echo [OK] x86 native binaries synchronized from bin\x86
) else (
    echo [WARNING] x86 native binaries not found in %DIST_ROOT%\x86. Please run ..\build.cmd if missing.
)

:: ---------------------------------------------------------------------
:: 3. Clean Prior Build Artifacts
:: ---------------------------------------------------------------------
echo.
echo [*] Cleaning previous build outputs...
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"
for /d %%d in (*.egg-info) do rd /s /q "%%d"
echo [OK] Build workspaces clean.

:: ---------------------------------------------------------------------
:: 4. Build Real PyPI Distributions (.tar.gz and Arch-Specific .whl)
:: ---------------------------------------------------------------------
echo.
echo [*] Building PEP 517 sdist distribution (with unified tests)...
python setup.py sdist
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Source distribution build failed!
    exit /b 1
)

echo.
echo [*] Building platform wheel for win_amd64 (containing ONLY x64 native binaries)...
python setup.py bdist_wheel --plat-name win_amd64
if %ERRORLEVEL% neq 0 (
    echo [ERROR] win_amd64 wheel build failed!
    exit /b 1
)

echo.
echo [*] Building platform wheel for win32 (containing ONLY x86 native binaries)...
python setup.py bdist_wheel --plat-name win32
if %ERRORLEVEL% neq 0 (
    echo [ERROR] win32 wheel build failed!
    exit /b 1
)

:: Clean ephemeral build workspace
if exist "build" rd /s /q "build"
for /d %%d in (*.egg-info) do rd /s /q "%%d"
if exist ".pytest_cache" rd /s /q ".pytest_cache"

:: ---------------------------------------------------------------------
:: 5. Verify Package Integrity with Twine
:: ---------------------------------------------------------------------
echo.
echo =====================================================================
echo  Verifying Built Packages with Twine
echo =====================================================================
python -m twine check --strict dist/*
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Twine package validation failed!
    echo         Please review the metadata and description errors above.
    exit /b 1
)
echo [OK] All distribution packages passed Twine strict validation!

:: ---------------------------------------------------------------------
:: 6. Verify Architecture Isolation in Distribution Wheels
:: ---------------------------------------------------------------------
echo.
echo [*] Verifying architecture isolation in distribution wheels:
python -c "import zipfile, glob; wheels = sorted(glob.glob('dist/*.whl')); [print('\n--- ' + w + ' ---') or [print('   ->', n) for n in zipfile.ZipFile(w).namelist() if 'lib/' in n] for w in wheels]"

:: ---------------------------------------------------------------------
:: 7. Summary and Upload Instructions
:: ---------------------------------------------------------------------
echo.
echo =====================================================================
echo  PACKAGE BUILD SUCCESSFUL! READY FOR PYPI UPLOAD
echo =====================================================================
echo  Artifacts created in %SCRIPT_DIR%dist:
dir /b "dist"
echo.
echo  To upload to Test PyPI:
echo    python -m twine upload --repository testpypi dist/*
echo.
echo  To upload to Official PyPI:
echo    python -m twine upload dist/*
echo =====================================================================
exit /b 0
