@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem Creates "AccTrack" shortcut next to start.bat with the triangle icon.
rem Double-click the shortcut afterwards (it shows the logo in the title bar
rem and keeps the window open if the app fails).

if not exist "acctrack.ico" (
  echo [ERROR] acctrack.ico not found next to this file.
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$d = '%~dp0'.TrimEnd('\');" ^
  "$w = New-Object -ComObject WScript.Shell;" ^
  "$s = $w.CreateShortcut((Join-Path $d 'AccTrack.lnk'));" ^
  "$s.TargetPath = Join-Path $env:WINDIR 'System32\cmd.exe';" ^
  "$s.Arguments = '/c \"\"' + (Join-Path $d 'start.bat') + '\"\"';" ^
  "$s.WorkingDirectory = $d;" ^
  "$s.IconLocation = (Join-Path $d 'acctrack.ico') + ',0';" ^
  "$s.Description = 'AccTrack - deals, channels, stock';" ^
  "$s.Save(); Write-Host 'Shortcut created: AccTrack.lnk'"

echo.
echo Done. Double-click AccTrack.lnk to start with the logo icon.
pause
