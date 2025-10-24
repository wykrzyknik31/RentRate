@echo off
REM Clean start script for RentRate backend (Windows)
REM This script clears Python cache, runs migrations, and starts the server fresh

echo ============================================
echo  RentRate Backend - Clean Start
echo ============================================
echo.

echo [1/4] Cleaning Python cache...
if exist __pycache__ rmdir /s /q __pycache__
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
echo Cache cleared!
echo.

echo [2/4] Checking virtual environment...
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found!
    echo Please create it with: python -m venv venv
    echo.
)

echo [3/4] Running database migrations...
set FLASK_APP=app.py
flask db upgrade
if %errorlevel% equ 0 (
    echo Database migrations completed successfully!
) else (
    echo WARNING: Database migrations encountered issues, continuing anyway...
)
echo.

echo [4/4] Starting Flask server...
echo ============================================
echo.
python app.py
