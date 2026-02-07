# Running Multiple Flask Applications Simultaneously

This guide explains how to run two separate Python Flask web applications on the same machine simultaneously.

## Applications Available

1. **app.py** - Google OAuth integrated authentication application
2. **web_app.py** - Project-Based Task Management application

## Method 1: Using Port Configuration Scripts

### Prerequisites
- Python 3.x installed
- Required packages installed: `pip install -r requirements.txt`

### Running Both Applications Simultaneously

#### Terminal 1 - Run app.py on port 5001:
```bash
python run_app_port.py --port 5001
```

#### Terminal 2 - Run web_app.py on port 5002:
```bash
python run_web_app_port.py --port 5002
```

### Accessing the Applications

After starting both applications, you can access them at:

- **app.py (Google OAuth app)**: http://localhost:5001
- **web_app.py (Task Management app)**: http://localhost:5002

## Method 2: Direct Command Line Override

You can also run the applications directly with different ports using Python's `-c` option:

### Terminal 1 - Run app.py on port 5001:
```bash
python -c "
import sys
sys.path.insert(0, '.')
from app import app
app.run(debug=True, host='127.0.0.1', port=5001, use_reloader=False)
"
```

### Terminal 2 - Run web_app.py on port 5002:
```bash
python -c "
import sys
sys.path.insert(0, '.')
from web_app import app
app.run(debug=True, host='0.0.0.0', port=5002, use_reloader=False)
"
```

## Port Configuration Options

Both wrapper scripts support the following options:

### run_app_port.py options:
- `--port 5001` or `-p 5001`: Specify port number (default: 5001)

### run_web_app_port.py options:
- `--port 5002` or `-p 5002`: Specify port number (default: 5002)

## Available Ports

The applications can run on any available port in the range 1024-65535. Common alternatives:
- 5001, 5002, 5003, etc. for development
- 8000, 8080, 8081 for alternative development servers
- 3000, 4000 for Node.js-like port numbers

## Verification

To verify that both applications are running:

1. Check the terminal output for each application - they should show "Running on http://..." with different ports
2. Visit both URLs in your browser
3. Each application should load independently

## Stopping Applications

Press `Ctrl+C` in each terminal window to stop the respective application.

## Troubleshooting

### Port Already in Use
If you get a "port already in use" error, try a different port number.

### Permission Issues
On Unix systems, ports below 1024 require administrator privileges.

### Browser Auto-Opening
The scripts attempt to open browsers automatically. If this causes issues, you can manually visit the URLs.

## Environment Variables

Both applications require the same environment variables. Make sure your .env file is properly configured:

```bash
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
FACEBOOK_CLIENT_ID=your_facebook_client_id_here
FACEBOOK_CLIENT_SECRET=your_facebook_client_secret_here
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
SECRET_KEY=your_strong_secret_key_here
```

## Notes

- Each application runs in its own process and has its own database/session state
- The applications are completely independent of each other
- You can run additional instances on other ports if needed
- The original code remains unchanged as requested