@echo off
setlocal
chcp 65001 > nul
title Z-PACT Ultra-Fast Server

REM Navigate to script directory
cd /d "%~dp0"

REM Environment configuration
set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set SERVER_RELOAD=false

echo ==============================================================
echo                 Z-PACT Platform - Fast Server
echo ==============================================================
echo [1/2] Opening browser at: http://127.0.0.1:8000/login
echo [2/2] Starting server with multi-core performance...
echo.
echo Press Ctrl + C to stop the server.
echo ==============================================================
echo.

REM Open browser immediately
start "" "http://127.0.0.1:8000/login"

REM Start server
python main.py

if errorlevel 1 (
    echo.
    echo An error occurred while running the server.
    pause
)
