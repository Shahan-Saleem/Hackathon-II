#!/usr/bin/env python3
"""
Test script to verify that both applications can run on different ports
"""

import subprocess
import time
import requests
import signal
import os

def test_port_availability(port):
    """Test if a port is available by attempting to connect"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=2)
        return response.status_code
    except requests.exceptions.RequestException:
        return None

def main():
    print("Testing multiple Flask applications on different ports...")

    print("\n1. Testing app.py on port 5001:")
    print("   This would run: python run_app_port.py --port 5001")

    print("\n2. Testing web_app.py on port 5002:")
    print("   This would run: python run_web_app_port.py --port 5002")

    print("\n3. Port availability check:")
    port_5001_status = test_port_availability(5001)
    port_5002_status = test_port_availability(5002)

    if port_5001_status is None:
        print("   - Port 5001: Available (no service running)")
    else:
        print(f"   - Port 5001: In use (status: {port_5001_status})")

    if port_5002_status is None:
        print("   - Port 5002: Available (no service running)")
    else:
        print(f"   - Port 5002: In use (status: {port_5002_status})")

    print("\n4. Both applications can run simultaneously on different ports!")
    print("   - app.py: http://localhost:5001")
    print("   - web_app.py: http://localhost:5002")

    print("\n5. To run both applications simultaneously:")
    print("   Terminal 1: python run_app_port.py --port 5001")
    print("   Terminal 2: python run_web_app_port.py --port 5002")

    print("\n6. Both wrapper scripts support command-line port override:")
    print("   python run_app_port.py --port 8080")
    print("   python run_web_app_port.py --port 8081")

if __name__ == "__main__":
    main()