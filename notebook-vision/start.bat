@echo off
:: Notebook Vision - Windows Start Script
:: This script helps you start both backend and frontend services

echo 🚀 Starting Notebook Vision Application
echo ======================================

:: Check if we're in the right directory
if not exist "backend" (
    echo ❌ Error: backend directory not found
    echo Please run this script from the notebook-vision root directory
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ Error: frontend directory not found  
    echo Please run this script from the notebook-vision root directory
    pause
    exit /b 1
)

:: Check dependencies
echo 🔍 Checking dependencies...

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.9 or later from https://python.org
    pause
    exit /b 1
)

:: Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js 16 or later from https://nodejs.org
    pause
    exit /b 1
)

:: Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed or not in PATH
    echo Please install npm (usually comes with Node.js)
    pause
    exit /b 1
)

echo ✅ All dependencies found!

:: Setup backend virtual environment if it doesn't exist
if not exist "backend\venv" (
    echo 📦 Creating Python virtual environment...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    cd ..
    echo ✅ Virtual environment created and dependencies installed!
) else (
    echo ✅ Virtual environment found!
)

:: Install frontend dependencies if needed
if not exist "frontend\node_modules" (
    echo 📦 Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
    echo ✅ Frontend dependencies installed!
) else (
    echo ✅ Frontend dependencies found!
)

:: Start backend
echo 🔧 Starting backend server...
cd backend
call venv\Scripts\activate.bat
start "Notebook Vision Backend" cmd /k "python main.py"
cd ..

:: Wait for backend to start
timeout /t 5 /nobreak >nul

:: Start frontend  
echo 🎨 Starting frontend server...
cd frontend
start "Notebook Vision Frontend" cmd /k "npm run dev"
cd ..

:: Wait for frontend to start
timeout /t 3 /nobreak >nul

echo.
echo 🎉 Notebook Vision is now starting!
echo ======================================
echo 📱 Frontend will be available at: http://localhost:3000
echo 🔧 Backend API will be available at: http://localhost:8000
echo.
echo Two command windows should have opened:
echo - One for the backend (Python/FastAPI)
echo - One for the frontend (React/Vite)
echo.
echo Close those windows to stop the application.
echo.
echo Press any key to exit this script...
pause >nul
