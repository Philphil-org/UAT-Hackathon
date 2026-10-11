@echo off
title Aero - Zero-Touch OS Installer & Launcher
color 0b

:: Ensure the script runs in its own directory regardless of how it was launched
cd /d "%~dp0"

echo ==============================================
echo        Aero: Zero-Touch OS Engine
echo ==============================================
echo.

:: Check if the virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] First time setup detected!
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Python not found or unable to create venv. Please ensure Python 3.10+ is installed.
        pause
        exit /b 1
    )
    
    echo [INFO] Installing required dependencies (this may take a minute)...
    call venv\Scripts\activate.bat
    python -m pip install -r requirements.txt
    echo.
    echo [SUCCESS] Setup complete!
) else (
    echo [INFO] Environment found. Loading ZeroTouch...
    call venv\Scripts\activate.bat
)

:: Run the launcher
echo [INFO] Starting ZeroTouch OS...
python launcher.py

echo.
echo [INFO] ZeroTouch has been closed.
pause
