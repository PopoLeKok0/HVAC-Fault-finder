@echo off
REM HVAC Fault Finder - Quick Start Script for Windows

echo.
echo ========================================
echo   HVAC Fault Finder - Web Application
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt -q

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo ✓ Dependencies installed
echo.

REM Start the application
echo Starting HVAC Fault Finder...
echo.
echo ============================================
echo Open your browser and go to:
echo http://localhost:5000
echo ============================================
echo.
echo Press Ctrl+C to stop the application
echo.

python app.py
