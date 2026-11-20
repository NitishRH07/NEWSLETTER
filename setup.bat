@echo off
REM =========================================================
REM  setup.bat — One-time setup for HAL Newsletter Generator
REM =========================================================
echo.
echo ========================================
echo  HAL AI Tools Weekly — Setup
echo ========================================
echo.

REM 1. Create virtual environment
echo [1/5] Creating Python virtual environment...
python -m venv venv
if errorlevel 1 (echo ERROR: Python not found. Install Python 3.11+ && pause && exit /b 1)

REM 2. Upgrade pip
echo [2/5] Upgrading pip...
venv\Scripts\python -m pip install --upgrade pip --quiet

REM 3. Install Python dependencies
echo [3/5] Installing Python dependencies...
venv\Scripts\pip install -r backend\requirements.txt
if errorlevel 1 (echo ERROR: pip install failed && pause && exit /b 1)

REM 4. Install Playwright Chromium browser
echo [4/5] Installing Playwright Chromium...
venv\Scripts\playwright install chromium
if errorlevel 1 (echo WARNING: Playwright install may have failed — check manually)

REM 5. Initialise database
echo [5/5] Initialising database...
venv\Scripts\python backend\database\db_manager.py --init
if errorlevel 1 (echo WARNING: DB init failed — check Python path)

REM Copy .env.example if config/.env doesn't exist
if not exist config\.env (
    echo.
    echo [INFO] Copying config\.env.example to config\.env
    echo [INFO] EDIT config\.env and add your API keys before running!
    copy config\.env.example config\.env
)

echo.
echo ========================================
echo  Setup complete!
echo  Next steps:
echo  1. Edit config\.env and add your GEMINI_API_KEY
echo  2. Run: run_backend.bat
echo  3. Run: run_frontend.bat
echo ========================================
pause
