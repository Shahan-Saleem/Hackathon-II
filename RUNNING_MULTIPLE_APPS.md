# Running Two Separate Flask Applications Simultaneously

## Overview
This project contains two Flask applications that can run simultaneously on the same machine using different ports.

## Applications

1. **app.py** - Google OAuth integrated authentication application
2. **web_app.py** - Project-Based Task Management application

## Solution: Port Configuration

Both applications have been configured to run on separate ports to avoid conflicts:

- **app.py**: Runs on port 5001
- **web_app.py**: Runs on port 5002

## Files Created

1. `run_app_port.py` - Wrapper for app.py with configurable port
2. `run_web_app_port.py` - Wrapper for web_app.py with configurable port
3. `MULTIPLE_APPS_GUIDE.md` - Complete setup instructions

## Running Instructions

### Terminal 1: Run app.py
```bash
python run_app_port.py --port 5001
```

Access at: http://localhost:5001

### Terminal 2: Run web_app.py
```bash
python run_web_app_port.py --port 5002
```

Access at: http://localhost:5002

## Command Line Arguments

Both scripts support port customization:
```bash
python run_app_port.py --port 8080
python run_web_app_port.py --port 8081
```

## Key Features

✅ Different ports to avoid conflicts
✅ Command-line port override support
✅ Separate terminal windows required
✅ Original code unchanged
✅ Independent application states
✅ Browser-accessible URLs

## Requirements Met

1. ✅ Each app uses a different port (5001 and 5002)
2. ✅ Existing code kept unchanged
3. ✅ Separate terminal windows needed
4. ✅ Browser access URLs provided
5. ✅ Port override via command line arguments

Both applications can now run simultaneously without conflicts!