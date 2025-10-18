@echo off
REM SchoolLinux Installation Script for Windows
REM This script installs dependencies and sets up the environment

echo 🚀 Starting SchoolLinux installation for Windows...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16 or higher from https://nodejs.org
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed. Please install npm.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Create virtual environment for backend
echo 📦 Setting up Python virtual environment...
cd backend
python -m venv .venv
call .venv\Scripts\activate.bat

REM Install Python dependencies
echo 📦 Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Backend dependencies installed

REM Go back to project root
cd ..

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
cd frontend
npm install

echo ✅ Frontend dependencies installed

REM Go back to project root
cd ..

echo 🎉 Installation completed successfully!
echo.
echo To run the application:
echo   run_windows.bat
echo.
echo Or manually:
echo   cd backend ^&^& .venv\Scripts\activate.bat ^&^& fastapi run . ^&
echo   cd frontend ^&^& npm run dev -- --port 4000 ^&
echo   start http://localhost:4000

pause
