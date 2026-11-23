@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist config.json (
  echo [ERROR] config.json not found.
  echo Copy config.json.example to config.json and set server + token.
  pause
  exit /b 1
)

python taobao_collector.py %*
pause
