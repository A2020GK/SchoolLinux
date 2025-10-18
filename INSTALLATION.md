# SchoolLinux Installation Guide

This guide will help you install and run the SchoolLinux application on both Windows and Linux systems.

## Prerequisites

Before installing SchoolLinux, make sure you have the following installed:

### Required Software
- **Python 3.8 or higher** - [Download Python](https://python.org)
- **Node.js 16 or higher** - [Download Node.js](https://nodejs.org)
- **npm** (comes with Node.js)

### Verify Installation
You can verify your installations by running these commands in your terminal:

```bash
python3 --version  # or python --version on Windows
node --version
npm --version
```

## Installation

### Linux Installation

1. **Run the installation script:**
   ```bash
   ./install_linux.sh
   ```

2. **Start the application:**
   ```bash
   ./run_linux.sh
   ```

### Windows Installation

1. **Run the installation script:**
   - Double-click `install_windows.bat` or run it from Command Prompt

2. **Start the application:**
   - Double-click `run_windows.bat` or run it from Command Prompt

## Manual Installation (Alternative)

If the automated scripts don't work, you can install manually:

### Backend Setup
```bash
cd backend
python3 -m venv .venv  # or python -m venv .venv on Windows
source .venv/bin/activate  # or .venv\Scripts\activate.bat on Windows
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Running the Application
```bash
# Terminal 1 - Backend
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate.bat on Windows
fastapi run .

# Terminal 2 - Frontend
cd frontend
npm run dev -- --port 4000
```

## Accessing the Application

Once both servers are running:
- **Frontend (Web Interface):** http://localhost:4000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Troubleshooting

### Common Issues

1. **Port already in use:**
   - Make sure no other application is using ports 4000 or 8000
   - You can change the frontend port by modifying the run scripts

2. **Permission denied (Linux):**
   - Make sure the scripts are executable: `chmod +x *.sh`

3. **Python not found:**
   - Make sure Python is installed and added to your PATH
   - Try using `python3` instead of `python`

4. **Node.js not found:**
   - Make sure Node.js is installed and added to your PATH

### Getting Help

If you encounter issues:
1. Check that all prerequisites are installed correctly
2. Verify that ports 4000 and 8000 are available
3. Check the terminal output for error messages
4. Make sure you're running the scripts from the project root directory

## Project Structure

```
SchoolLinux/
├── backend/
│   ├── requirements.txt    # Python dependencies
│   ├── data.py            # Data models and storage
│   └── __init__.py        # FastAPI application
├── frontend/
│   ├── package.json       # Node.js dependencies
│   └── src/               # React/TypeScript source code
├── install_linux.sh       # Linux installation script
├── run_linux.sh          # Linux run script
├── install_windows.bat    # Windows installation script
└── run_windows.bat       # Windows run script
```

## Stopping the Application

- **Linux:** Press `Ctrl+C` in the terminal running `run_linux.sh`
- **Windows:** Close the terminal windows opened by `run_windows.bat`
