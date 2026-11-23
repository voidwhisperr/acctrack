@echo off
chcp 65001 >nul
cd /d "%~dp0"
python game_tracker.py
pause
