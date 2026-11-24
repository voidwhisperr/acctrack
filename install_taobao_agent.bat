@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   Ledger - встановлення Taobao-агента
echo ============================================
echo.
where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python не знайдено.
  echo Встанови Python 3.11+ з python.org і запусти цей файл знову.
  pause
  exit /b 1
)
echo Встав SERVER з Ledger: Аналітика/Таобао - Налаштування агента
set /p GT_SERVER=Server (напр. https://ledger.example.com): 
echo Встав TOKEN звідти ж.
set /p GT_TOKEN=Token: 
if "%GT_SERVER%"=="" ( echo [ERROR] Server порожній. & pause & exit /b 1 )
if "%GT_TOKEN%"=="" ( echo [ERROR] Token порожній. & pause & exit /b 1 )
python -c "import json,os;json.dump({'server':os.environ['GT_SERVER'].strip().rstrip('/'),'token':os.environ['GT_TOKEN'].strip()},open('config.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)"
if errorlevel 1 ( echo [ERROR] Не вдалося записати config.json. & pause & exit /b 1 )
echo.
echo [1/2] Встановлюю Playwright...
python -m pip install --upgrade pip
python -m pip install playwright
if errorlevel 1 ( echo [ERROR] pip install не вдався. & pause & exit /b 1 )
echo [2/2] Завантажую Chromium...
python -m playwright install chromium
if errorlevel 1 ( echo [ERROR] Chromium не встановився. & pause & exit /b 1 )
echo.
echo Готово. Запускаю агент...
python taobao_collector.py
pause