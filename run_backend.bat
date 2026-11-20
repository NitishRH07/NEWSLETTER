@echo off
REM =========================================================
REM  run_backend.bat — Start the FastAPI backend server
REM =========================================================
echo Starting HAL Newsletter API backend...
cd /d %~dp0
call venv\Scripts\activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
pause
