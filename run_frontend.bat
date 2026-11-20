@echo off
REM =========================================================
REM  run_frontend.bat — Start the React/Vite dev server
REM =========================================================
echo Starting HAL Newsletter frontend (Vite dev server)...
cd /d %~dp0\frontend
npm run dev
pause
