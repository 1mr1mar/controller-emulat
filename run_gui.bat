@echo off
title Virtual Xbox Controller - GUI Launcher
echo 🎮 Virtual Xbox Controller - GUI Launcher
echo ========================================
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
python -c "import vgamepad, pynput, tkinter" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some required packages are missing
    echo Installing required packages...
    pip install vgamepad pynput
    if errorlevel 1 (
        echo ❌ Failed to install packages
        echo Please run: pip install vgamepad pynput
        pause
        exit /b 1
    )
)

echo ✅ All dependencies are ready!
echo 🚀 Launching GUI...
echo.

REM Launch the GUI version
python gamepad_gui.py

if errorlevel 1 (
    echo.
    echo ❌ Error launching GUI. Trying launcher...
    python launcher.py
)

echo.
echo 👋 Controller session ended
pause
