@echo off
title Hiramoti Collection - Store & Admin Server
color 06

echo ======================================================================
echo           HIRAMOTI COLLECTION SATARA — STORE & ADMIN SERVER
echo ======================================================================
echo.
echo  Starting local server...
echo.

cd /d "%~dp0"

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in system PATH.
    echo Please install Python 3.10+ from python.org and try again.
    pause
    exit /b 1
)

:: Check and install dependencies if flask is missing
python -c "import flask, werkzeug" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO] Installing required dependencies...
    pip install flask werkzeug
)

echo.
echo [OK] Python and dependencies verified.
echo.
echo [1] Store Website:  http://localhost:5000/
echo [2] Admin Console:  http://localhost:5000/admin
echo.
echo Opening Admin Dashboard in browser...
start http://localhost:5000/admin
echo.
echo Server is running. Keep this window open while using Hiramoti.
echo Press Ctrl+C in this window to stop the server.
echo ======================================================================
echo.

python app.py
pause
