@echo off
setlocal enabledelayedexpansion

title GraphTrace AI - Stop Services
cd /d "%~dp0"

echo ============================================================
echo           GraphTrace AI — Stopping Services
echo ============================================================
echo.

set KILLED_ANY=0

:: 1. Terminate windows by window title
echo [*] Closing server terminal windows...
taskkill /FI "WINDOWTITLE eq GraphTrace AI - Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq GraphTrace AI - Frontend*" /T /F >nul 2>&1

:: 2. Terminate any processes listening on port 8000 (Backend / uvicorn / Python)
echo [*] Checking and freeing port 8000 (Backend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo     Killing PID %%a on port 8000...
    taskkill /F /PID %%a >nul 2>&1
    set KILLED_ANY=1
)

:: 3. Terminate any processes listening on port 5173 (Frontend / Vite / Node)
echo [*] Checking and freeing port 5173 (Frontend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo     Killing PID %%a on port 5173...
    taskkill /F /PID %%a >nul 2>&1
    set KILLED_ANY=1
)

echo.
echo ============================================================
echo   [OK] All GraphTrace AI services have been stopped.
echo ============================================================
echo.
ping -n 2 127.0.0.1 >nul
exit /b 0
