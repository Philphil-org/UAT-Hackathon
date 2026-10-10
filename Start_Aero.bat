@echo off
title Aero - Zero-Touch OS Installer & Launcher
color 0b

echo ==============================================
echo        Aero: Zero-Touch OS Engine
echo ==============================================
echo.

:: Check if the virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] First time setup detected!
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
    
    echo [INFO] Installing required AI models and dependencies (this may take a minute)...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    echo.
    echo [SUCCESS] Setup complete!
) else (
    echo [INFO] Environment found. Loading Aero...
    call venv\Scripts\activate.bat
)

:: Run the launcher
echo [INFO] Starting the Aero UI Launcher...
python launcher.py

echo.
echo [INFO] Aero has been closed.
pause
