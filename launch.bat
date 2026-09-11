@echo off
setlocal enabledelayedexpansion

title GraphTrace AI Launcher
cd /d "%~dp0"

echo ============================================================
echo           GraphTrace AI — System Launch Sequence
echo ============================================================
echo.

:: 1. Verify Backend Virtual Environment
if not exist "backend\venv\Scripts\python.exe" (
    echo [ERROR] Python virtual environment not found at backend\venv!
    echo Please set up the virtual environment first:
    echo   python -m venv backend\venv
    echo   backend\venv\Scripts\pip install -r backend\requirements.txt
    echo.
    pause
    exit /b 1
)

:: 2. Verify Frontend Dependencies
if not exist "frontend\node_modules" (
    echo [WARNING] frontend\node_modules not found. Running npm install...
    cd frontend
    call npm install
    cd /d "%~dp0"
)

:: 3. Pre-seed Demo & Enterprise Graph Fixtures
echo [*] Initializing knowledge graph data and sample projects...
backend\venv\Scripts\python.exe -m scripts.make_demo >nul 2>&1
if errorlevel 1 (
    echo [!] Note: scripts.make_demo exited with a warning, continuing...
) else (
    echo [OK] Knowledge graphs and sample project verified.
)

:: 4. Stop any previous instances on ports 8000 and 5173 to avoid conflicts
echo [*] Checking for existing instances on ports 8000 and 5173...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: 5. Start Backend Server
echo [*] Starting FastAPI Backend (http://127.0.0.1:8000)...
start "GraphTrace AI - Backend" cmd /k "title GraphTrace AI - Backend && set PYTHONPATH=. && backend\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

:: 6. Start Frontend Server
echo [*] Starting Vite Frontend (http://localhost:5173)...
start "GraphTrace AI - Frontend" cmd /k "title GraphTrace AI - Frontend && cd /d "%~dp0frontend" && npm run dev"

:: 7. Wait briefly for services to initialize
echo [*] Waiting for services to initialize...
ping -n 4 127.0.0.1 >nul

:: 8. Open Browser
echo [*] Launching application in default browser...
start http://localhost:5173

echo.
echo ============================================================
echo           GraphTrace AI is LIVE and Running!
echo ============================================================
echo   - Frontend:      http://localhost:5173
echo   - Backend API:   http://127.0.0.1:8000
echo   - OpenAPI Docs:  http://127.0.0.1:8000/docs
echo.
echo   To stop all running services:
echo     Run "stop.bat" or close the server windows.
echo ============================================================
echo.
