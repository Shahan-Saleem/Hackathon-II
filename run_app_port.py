#!/usr/bin/env python3
"""
Application Startup Script for app.py with Port Configuration
"""

import os
import sys
import threading
import time
import webbrowser
import argparse

# Add current directory to Python path to import app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_app(port=5001):
    """Run the app.py application on the specified port"""
    # Import app inside the function to avoid issues with Flask app context
    from app import app

    print(f"Starting app.py on port {port}...")
    print(f"Server will be available at: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)

    try:
        # Run the Flask app in the main thread (blocking)
        app.run(debug=True, host='127.0.0.1', port=port, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down server...")
        print("👋 Application stopped.")

def open_browser(port):
    """Open the web browser after a delay"""
    time.sleep(3)  # Wait for server to start
    webbrowser.open(f'http://localhost:{port}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run app.py with configurable port')
    parser.add_argument('--port', '-p', type=int, default=5001,
                        help='Port number for the application (default: 5001)')

    args = parser.parse_args()

    # Validate port number
    if not (1024 <= args.port <= 65535):
        print(f"Error: Port {args.port} is outside the valid range (1024-65535)")
        sys.exit(1)

    run_app(args.port)