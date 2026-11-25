@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title Ledger

echo.
echo        /\
echo       /  \        L E D G E R
echo      /____\       deals . channels . stock
echo.
echo ============================================================
echo   Starting Ledger
echo ============================================================
echo   URL:  http://localhost:8766
echo   Stop: close this window or press Ctrl+C
echo.

rem create shortcut with icon on first run

if not exist "Ledger.lnk" if exist "assets\ledger.ico" (
  powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$d = '%~dp0'.TrimEnd('\');" ^
    "$w = New-Object -ComObject WScript.Shell;" ^
    "$s = $w.CreateShortcut((Join-Path $d 'Ledger.lnk'));" ^
    "$s.TargetPath = Join-Path $env:WINDIR 'System32\cmd.exe';" ^
    "$s.Arguments = '/c \"\"' + (Join-Path $d 'start.bat') + '\"\"';" ^
    "$s.WorkingDirectory = $d;" ^
    "$s.IconLocation = (Join-Path $d 'assets\ledger.ico') + ',0';" ^
    "$s.Description = 'Ledger - deals, channels, stock';" ^
    "$s.Save()" >nul 2>&1
)

set PY=
where python >nul 2>&1 && set PY=python
if "%PY%"=="" ( where py >nul 2>&1 && set PY=py -3 )
if "%PY%"=="" (
  if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set PY="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)
if "%PY%"=="" (
  if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set PY="%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
)
if "%PY%"=="" (
  echo [ERROR] Python not found. Install Python 3.11+ from https://python.org
  echo         and tick "Add python.exe to PATH" during setup.
  pause
  exit /b 1
)

%PY% game_tracker.py
set CODE=%ERRORLEVEL%

echo.
if not "%CODE%"=="0" (
  echo ============================================================
  echo   App exited with code %CODE% - see the message above
  echo ============================================================
) else (
  echo App stopped.
)
pause
endlocal
