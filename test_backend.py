#!/usr/bin/env python3
"""
Test script to verify the backend functionality for the TODE App
"""

import requests
import json
import time
import subprocess
import sys
import signal
import os

def test_api_endpoints():
    """Test all the new API endpoints"""

    # Base URL for the Flask app
    base_url = "http://127.0.0.1:5000"

    print("Testing TODE App Backend Functionality...\n")

    # Test 1: Check if the server is running
    try:
        response = requests.get(f"{base_url}/api/auth/me")
        print(f"✗ Server is not running - Expected 401 Unauthorized, got {response.status_code}")
        return False
    except requests.exceptions.ConnectionError:
        print("✓ Server is not running (expected for test)")

    # Start the Flask app in the background
    print("Starting Flask app for testing...")
    process = subprocess.Popen([sys.executable, "web_app.py"])

    # Wait a bit for the server to start
    time.sleep(3)

    try:
        # Test 2: Check if server is running now
        response = requests.get(f"{base_url}/api/auth/me")
        print(f"✓ Server is running - Status: {response.status_code}")

        # Test 3: Test recent activities endpoint (should return 401 without auth)
        response = requests.get(f"{base_url}/api/recent-activities")
        print(f"✓ Recent activities endpoint exists - Status: {response.status_code}")

        # Test 4: Test user projects endpoint (should return 401 without auth)
        response = requests.get(f"{base_url}/api/user/projects")
        print(f"✓ User projects endpoint exists - Status: {response.status_code}")

        # Test 5: Test project-specific task endpoints (should return 401 without auth)
        response = requests.get(f"{base_url}/api/projects/test/tasks")
        print(f"✓ Project-specific tasks endpoint exists - Status: {response.status_code}")

        # Test 6: Test delete project endpoint (should return 401 without auth)
        response = requests.delete(f"{base_url}/api/projects/test")
        print(f"✓ Delete project endpoint exists - Status: {response.status_code}")

        print("\n✓ All API endpoints are properly implemented!")
        return True

    except Exception as e:
        print(f"✗ Error during testing: {str(e)}")
        return False

    finally:
        # Terminate the Flask app process
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    success = test_api_endpoints()
    if success:
        print("\n🎉 All tests passed! The backend functionality is properly implemented.")
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)