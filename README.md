# SchoolLinux: Interactive Linux Terminal Training System

## Overview

SchoolLinux is a gamified educational platform designed for teaching Linux terminal commands in a classroom environment. The system enables teachers to conduct interactive treasure-hunt games where students use Linux command-line skills to locate hidden "treasures" within dynamically generated directory structures on their local machines.

## Technical Architecture

### System Design

The application implements a client-server architecture with the following components:

- **Backend Server**: FastAPI-based REST API with WebSocket support for real-time communications
- **Frontend Client**: React-based single-page application with TypeScript
- **SSH Automation**: Paramiko library for remote environment provisioning
- **State Persistence**: Pickle-based serialization for system state management

### Communication Flow

1. **Registration Phase**: Students register via browser, system extracts IP addresses from connection metadata
2. **Deployment Phase**: Server generates unique game environments and deploys them to student machines via SSH
3. **Gameplay Phase**: Real-time bidirectional communication via WebSockets for submission and status updates
4. **Completion Phase**: Results aggregation and CSV export for grade assignment

## Technology Stack

### Backend
- **Python 3** - Core programming language
- **FastAPI** - Asynchronous web framework with automatic API documentation
- **Socket.IO** - WebSocket implementation for real-time client-server communication
- **Paramiko** - SSHv2 protocol library for remote command execution
- **Pydantic** - Data validation using Python type annotations
- **Pickle** - Native Python object serialization for persistent storage

### Frontend
- **React 19** - Component-based UI framework
- **TypeScript** - Type-safe JavaScript superset
- **Vite** - High-performance build tool and development server
- **Axios** - Promise-based HTTP client
- **Socket.IO Client** - Real-time bidirectional event-based communication
- **React Data Grid** - Efficient data table rendering for teacher dashboard
- **Font Awesome** - Icon library for UI elements

## System Requirements

### Server (Teacher's Computer)
- **Operating System**: Linux-based (tested on МОС 12)
- **Python**: 3.8 or higher
- **Node.JS**: Latest version is recommended
- **Network**: Local network connectivity to student machines
- **Ports**: 8000 (API), 4000 (optional, for frontend).

### Client (Student's Computer)
- **Operating System**: Linux with SSH server installed and running
- **SSH**: OpenSSH server configured and accessible
- **User Account**: Unified credentials (same username/password) for remote access
- **Browser**: Modern web browser with JavaScript and WebSocket support

## Installation

### 0. Install required dependencies
Ensure Python and Node.JS are correctly installed and work on teacher's computer.

### 1. Clone Repository
```bash
git clone https://github.com/A2020GK/SchoolLinux.git
cd SchoolLinux
```

### 2. Backend Setup
```bash
# Create Python Venv Enviroment
python -m venv .venv
source ./.venv/bin/activate # Or anything else on different OSs

# Install Python dependencies
pip install -r requirements.txt

# Create environment configuration file
cat > .env << EOF
SSH_USER=your_ssh_username
SSH_PASSWORD=your_ssh_password
EOF
```

### 3. Frontend Setup
```bash
cd frontend

# Install Node.js dependencies
npm install
```

### 4. Run Server
```bash
# From project root directory
fastapi run . --host 0.0.0.0

# Serve frontend (from frontend directory)
npx vite --host 0.0.0.0 --port 4000
```

Students access the application by navigating to `http://<teacher_ip>:<port (4000)>` in their browsers.

Game files are placed on students' computers in /home/\<user\>/Game

## Game Mechanics

### Environment Generation

The system generates a unique game environment for each student consisting of:

- **Directory Structure**: 125 directories organized in a 3-level hierarchy (5×5×5 tree)
- **File Distribution**: 30 randomly placed text files across the directory tree
- **Treasure Files**: 5 files containing treasure strings (format: `klad:<word1> <word2> <word3>`)
- **Compression**: Approximately 50% of files are GZIP-compressed (`.gz`), with 2 treasure files guaranteed to be compressed
- **Decoy Content**: Each file contains 20 lines of random English words to increase search complexity

### Student Objectives

Students must utilize Linux terminal commands to:
1. Navigate the directory tree (`cd`, `ls`, `pwd`)
2. View file contents (`cat`, `less`, `more`)
3. Decompress GZIP files (`gunzip`, `zcat`)
4. Search within files (`grep`, `find`)
5. Locate and submit treasure strings via the web interface

### Scoring System

- **Points per Treasure**: 1 point
- **Maximum Score**: 5 points
- **Duplicate Prevention**: Each treasure can only be submitted once
- **Real-time Updates**: Teacher dashboard displays live progress for all students

## API Documentation

### REST Endpoints

#### Information
- `GET /info` - Retrieve system status and client role
  - Response: `{ isTeacher: boolean, status: "reg" | "init" | "run" }`

#### Student Management
- `GET /students` - List all registered students (teacher only)
- `GET /students/me` - Retrieve current student's information
- `POST /students/reg` - Register a new student
  - Body: `{ pc: string, name: string }`
  - Validates SSH connectivity before registration
- `POST /students/logout` - Unregister current student
- `POST /students/kick/{ip}` - Remove specified student (teacher only)

#### Game Control
- `POST /game/start` - Initialize and deploy game environments (teacher only)
  - Transitions status: `reg` → `init` → `run`
  - Generates unique environments for all registered students
- `POST /game/stop` - Terminate game and export results (teacher only)
  - Returns: CSV-formatted results
  - Format: `IP;Computer;Name;Treasures`
- `POST /game/klad` - Submit found treasure
  - Body: `{ value: string }`
  - Validates treasure belongs to submitter's environment

### WebSocket Events

#### Server → Client
- `info` - Broadcast status changes to all connected clients
  - Payload: `{ status: string }`
- `students` - Update student list (teacher only)
  - Payload: `Record<string, Student>`
- `update` - Update individual student data
  - Payload: `{ pc: string, name: string, klads: number }`

#### Client → Server
- `connect` - Establish WebSocket connection
  - IP address extraction from connection metadata
- `disconnect` - Handle client disconnection

## Data Persistence

### State Management

The application uses Python's `pickle` module for serialization:

```python
@dataclass
class Student:
    pc: str          # Computer identifier
    name: str        # Student full name
    klads: set       # Set of unredeemed treasures

@dataclass
class Data:
    students: dict   # IP address → Student mapping
    status: str      # System state: "reg" | "init" | "run"
```

State is persisted to `data.pkl` and survives server restarts, enabling:
- Multiple game sessions without re-registration
- Recovery from unexpected server failures
- Audit trail for completed games

## Deployment Considerations

### Security

⚠️ **Important Security Notes**:
- SSH credentials stored in environment variables (`.env` file)
- System assumes trusted local network environment (classroom LAN)
- Teacher access based on IP address (`127.0.0.1` check)
- No authentication mechanism for web interface

### Network Configuration

- Ensure firewall rules permit:
  - SSH (port 22) from teacher machine to all student machines
  - HTTP (port 8000 or configured port) from student browsers to teacher machine
- All machines must be on the same network for IP-based identification

### SSH Setup on Student Machines

## Testing and Validation

The system has been tested in real classroom environments using:
- **Distribution**: МОС Linux 12 (Moscow Education Operating System)
- **Class Size**: Multiple sessions with 20-30 students
- **Hardware**: Standard school computer laboratory equipment

### Known Limitations

1. **Timer Functionality**: Time limit enforcement not implemented; requires manual game termination by teacher
2. **Scalability**: Designed for single classroom (20-30 concurrent users)
3. **SSH Dependency**: Requires pre-configured SSH access on all student machines
4. **Error Handling**: Limited feedback for network or SSH connectivity issues

## Future Development Roadmap

Potential enhancements identified from user feedback:

1. **Integrated Tutorial Module**: Built-in Linux command reference for teachers and students
2. **Multiple Game Modes**: 
   - Reverse challenge: students hide treasures for others to find
   - Competitive mode: first to find treasure claims points
3. **Advanced Configuration**:
   - Adjustable difficulty settings (directory depth, file count)
   - Custom treasure patterns and content
4. **Timer Implementation**: Automatic game termination with configurable duration
5. **Enhanced Analytics**: Detailed statistics on command usage and student performance patterns

## Project Structure

```
SchoolLinux/
├── __init__.py           # FastAPI application initialization and WebSocket setup
├── data.py               # Data models and persistence layer
├── game.py               # Game logic and treasure validation
├── generator.py          # Environment generation and SSH deployment
├── info.py               # System information endpoints
├── ssh.py                # SSH client wrapper
├── students.py           # Student registration and management
├── utils.py              # Utility functions and base schemas
├── words.txt             # Word list for content generation
├── requirements.txt      # Python dependencies
└── frontend/             # React frontend application
    ├── src/
    │   ├── App.tsx       # Main application component
    │   ├── Teacher.tsx   # Teacher dashboard interface
    │   ├── Student.tsx   # Student game interface
    │   ├── api.ts        # API client configuration
    │   └── ...
    ├── package.json      # Node.js dependencies
    └── vite.config.ts    # Build configuration
```

## Educational Context

### Pedagogical Approach

The system is designed for a two-phase lesson structure:

1. **Theory Phase** (15-20 minutes)
   - Teacher introduces Linux terminal concepts
   - Demonstrates essential commands with examples
   - Explains game objectives and rules

2. **Practice Phase** (20-30 minutes)
   - Students apply learned commands in competitive environment
   - Gamification motivates exploration and experimentation
   - Immediate feedback through scoring system

### Target Learning Outcomes

Students will be able to:
- Navigate Linux filesystem hierarchy
- Use basic file viewing commands (`cat`, `less`, `head`, `tail`)
- Search file contents with `grep`, `find` and regular expressions
- Work with compressed files (`gzip`, `gunzip`, `zcat`)
- Understand command composition and piping

## Acknowledgments

This project was developed as a school educational tool for teaching Linux terminal skills in Russian educational institutions. Special thanks to the teachers who participated in testing and provided valuable feedback for system improvements.

---

For issues, feature requests, or contributions, please visit the GitHub repository.
Developed by [Antony Karasev (A2020GK)](https://github.com/A2020GK)
