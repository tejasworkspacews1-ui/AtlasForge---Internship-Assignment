@echo off
REM AtlasForge backend launcher (Windows)
cd /d "%~dp0"
if not exist .venv (
    python -m venv .venv
    call .venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)
set PYTHONPATH=%CD%
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
