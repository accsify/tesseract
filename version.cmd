@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
python "%PROJECT_ROOT%scripts\set_version.py" %*
exit /b %ERRORLEVEL%
