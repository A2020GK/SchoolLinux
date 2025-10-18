#!/bin/bash

# SchoolLinux Installation Script for Linux
# This script installs dependencies and sets up the environment

set -e  # Exit on any error

echo "🚀 Starting SchoolLinux installation for Linux..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create virtual environment for backend
echo "📦 Setting up Python virtual environment..."
cd backend
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend dependencies installed"

# Go back to project root
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install

echo "✅ Frontend dependencies installed"

# Go back to project root
cd ..

echo "🎉 Installation completed successfully!"
echo ""
echo "To run the application:"
echo "  ./run_linux.sh"
echo ""
echo "Or manually:"
echo "  cd backend && source .venv/bin/activate && fastapi run . &"
echo "  cd frontend && npm run dev -- --port 4000 &"
echo "  xdg-open http://localhost:4000"
