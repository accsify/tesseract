@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo  Accsify Tesseract - GitHub Release Packaging Utility
echo  Company: accsify
echo =====================================================================

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

:: Verify Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not found in PATH!
    echo         Please ensure Python 3.8+ is installed to run release packager.
    exit /b 1
)

:: Run release packaging script
python "%PROJECT_ROOT%scripts\make_release.py"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Release packaging failed!
    exit /b 1
)

exit /b 0
