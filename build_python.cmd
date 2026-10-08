@echo off
setlocal

echo =====================================================================
echo  Accsify Tesseract - Python Package Build Runner
echo =====================================================================

set "PROJECT_ROOT=%~dp0"
call "%PROJECT_ROOT%python\build_package.cmd"
exit /b %ERRORLEVEL%
