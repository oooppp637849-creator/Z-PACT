@echo off
chcp 65001 > nul
cd /d "%~dp0"
python push_to_github.py
pause
