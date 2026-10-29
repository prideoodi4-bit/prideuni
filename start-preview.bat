@echo off
cd /d "%~dp0"
set PREVIEW_MODE=true
set BOT_TOKEN=
set DATA_DIR=runtime
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
python -m uvicorn app:app --host 127.0.0.1 --port 8080 --no-access-log
