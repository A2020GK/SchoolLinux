#!/bin/bash

# SchoolLinux Run Script for Linux
# This script starts both backend and frontend servers

set -e  # Exit on any error

echo "🚀 Starting SchoolLinux..."

# Check if virtual environment exists
if [ ! -d "backend/.venv" ]; then
    echo "❌ Virtual environment not found. Please run ./install_linux.sh first."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend dependencies not installed. Please run ./install_linux.sh first."
    exit 1
fi

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend server
echo "🔧 Starting backend server..."
cd backend
source .venv/bin/activate
fastapi run . &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Start frontend server
echo "🌐 Starting frontend server..."
cd frontend
npm run dev -- --port 4000 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 3

# Open browser
echo "🌍 Opening browser..."
xdg-open "http://localhost:4000" 2>/dev/null || echo "Please open http://localhost:4000 in your browser"

echo ""
echo "✅ SchoolLinux is running!"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:4000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user to stop
wait
