@echo off
setlocal
cd /d "%~dp0"
if not exist .env copy .env.example .env >nul
docker compose up -d || (echo Docker failed. Start Docker Desktop first. & pause & exit /b 1)
if not exist .venv\Scripts\python.exe py -3 -m venv .venv || (echo Python 3 required. & pause & exit /b 1)
.venv\Scripts\python.exe -m pip install -r requirements.txt || (echo Package install failed. & pause & exit /b 1)
.venv\Scripts\python.exe -m scripts.wait_for_db || (echo Database failed to start. & pause & exit /b 1)
.venv\Scripts\python.exe -m scripts.seed || (echo Database unavailable. Check Docker Desktop is healthy. & pause & exit /b 1)
start "" http://127.0.0.1:8000
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
pause
