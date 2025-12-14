@echo off
REM Quick start script for Windows

echo CAN Real-Time Plotter - Quick Start
echo ====================================
echo.

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

echo [OK] Python found

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo To start the application:
echo   venv\Scripts\activate.bat
echo   python main.py
echo.
echo Make sure you have PCAN-Basic or IXXAT VCI drivers installed
echo for your CAN hardware adapter.
echo.
pause
