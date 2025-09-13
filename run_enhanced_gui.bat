@echo off
title Virtual Xbox Controller - Enhanced GUI Launcher
echo 🎮 Virtual Xbox Controller - Enhanced GUI Launcher
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo 🔍 Checking dependencies...
python -c "import vgamepad, pynput, tkinter, PIL" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some required packages are missing
    echo Installing required packages...
    pip install vgamepad pynput pillow
    if errorlevel 1 (
        echo ❌ Failed to install packages
        echo Please run: pip install vgamepad pynput pillow
        pause
        exit /b 1
    )
)

echo ✅ All dependencies are ready!
echo 🚀 Launching Enhanced GUI...
echo.

REM Launch the Enhanced GUI version
python gamepad_gui_enhanced.py

if errorlevel 1 (
    echo.
    echo ❌ Error launching Enhanced GUI. Trying launcher...
    python launcher.py
)

echo.
echo 👋 Controller session ended
pause
