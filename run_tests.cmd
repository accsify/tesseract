@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo   Accsify Tesseract - Full Test Suite Runner (A to Z)
echo   Company: accsify
echo =====================================================================
echo.

cd /d "%~dp0"

echo [*] Running full test suite with Python unittest discovery...
python tests\test_all.py

if errorlevel 1 (
    echo.
    echo [ERROR] Test suite failed!
    exit /b 1
)

echo.
echo [SUCCESS] All tests passed cleanly!
exit /b 0
