@echo off
REM SchoolLinux Run Script for Windows
REM This script starts both backend and frontend servers

echo 🚀 Starting SchoolLinux...

REM Check if virtual environment exists
if not exist "backend\.venv" (
    echo ❌ Virtual environment not found. Please run install_windows.bat first.
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo ❌ Frontend dependencies not installed. Please run install_windows.bat first.
    pause
    exit /b 1
)

REM Start backend server
echo 🔧 Starting backend server...
cd backend
start "Backend Server" cmd /k ".venv\Scripts\activate.bat && fastapi run ."
cd ..

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server
echo 🌐 Starting frontend server...
cd frontend
start "Frontend Server" cmd /k "npm run dev -- --port 4000"
cd ..

REM Wait a moment for frontend to start
timeout /t 3 /nobreak >nul

REM Open browser
echo 🌍 Opening browser...
start http://localhost:4000

echo.
echo ✅ SchoolLinux is running!
echo    Backend: http://localhost:8000
echo    Frontend: http://localhost:4000
echo.
echo Close the terminal windows to stop the servers.
echo Press any key to exit this script...
pause >nul
