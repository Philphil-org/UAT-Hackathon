@echo off
title ZeroTouch OS - Installer & Launcher
color 0b

:: Change working directory to this script's directory
cd /d "%~dp0"

echo ==============================================
echo        ZeroTouch OS - Spatial Companion
echo ==============================================
echo.

:: Detect Python command (check 'python' then 'py')
set "PY_CMD="
python --version >nul 2>&1
if not errorlevel 1 (
    set "PY_CMD=python"
) else (
    py --version >nul 2>&1
    if not errorlevel 1 (
        set "PY_CMD=py"
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python was not found in your system PATH!
    echo.
    echo Please install Python 3.10+ from python.org
    echo IMPORTANT: Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [INFO] Detected Python engine: %PY_CMD%
%PY_CMD% --version

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo.
    echo [INFO] First time setup detected!
    echo [INFO] Creating Python virtual environment...
    %PY_CMD% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    
    echo [INFO] Installing required dependencies...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    echo.
    echo [SUCCESS] Environment setup complete!
) else (
    echo [INFO] Existing environment found. Activating...
    call venv\Scripts\activate.bat
)

:: Launch ZeroTouch cleanly and dismiss the terminal window
echo [INFO] Launching ZeroTouch OS...
if exist "venv\Scripts\pythonw.exe" (
    start "" "venv\Scripts\pythonw.exe" launcher.py
    exit /b 0
) else if exist "venv\Scripts\python.exe" (
    start "" "venv\Scripts\python.exe" launcher.py
    exit /b 0
) else (
    start "" python launcher.py
    exit /b 0
)
