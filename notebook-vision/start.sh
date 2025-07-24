#!/bin/bash

# Notebook Vision - Start Script
# This script helps you start both backend and frontend services

echo "🚀 Starting Notebook Vision Application"
echo "======================================"

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the notebook-vision root directory"
    echo "Expected structure:"
    echo "  notebook-vision/"
    echo "  ├── backend/"
    echo "  ├── frontend/"
    echo "  └── start.sh (this script)"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or later."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or later."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✅ All dependencies found!"

# Check if virtual environment exists for backend
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo "✅ Virtual environment created and dependencies installed!"
else
    echo "✅ Virtual environment found!"
fi

# Check if node_modules exists for frontend
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed!"
else
    echo "✅ Frontend dependencies found!"
fi

# Start backend in background
echo "🔧 Starting backend server..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ Backend started successfully (PID: $BACKEND_PID)"
    echo "🌐 Backend running at: http://localhost:8000"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 3

# Check if frontend started successfully
if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "✅ Frontend started successfully (PID: $FRONTEND_PID)"
    echo "🌐 Frontend running at: http://localhost:3000"
else
    echo "❌ Frontend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 Notebook Vision is now running!"
echo "======================================"
echo "📱 Open your browser and go to: http://localhost:3000"
echo "🔧 Backend API available at: http://localhost:8000"
echo ""
echo "To stop the application, press Ctrl+C"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down Notebook Vision..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped."
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Wait for user to stop
wait
