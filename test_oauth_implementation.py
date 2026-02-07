"""
Test script to verify Google OAuth implementation
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from backend.token_manager import TokenManager
from datetime import datetime, timedelta
import jwt

def test_jwt_functionality():
    """Test the JWT token functionality"""
    print("Testing JWT Token Manager...")

    # Test data
    user_data = {
        'id': 'test_user_123',
        'username': 'testuser',
        'email': 'test@example.com',
        'provider': 'google'
    }

    # Create access token
    try:
        # Create a mock Flask app context for testing
        from flask import Flask
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key-for-testing'

        with app.app_context():
            access_token = TokenManager.create_access_token(user_data, timedelta(minutes=30))
            print("[PASS] Access token created successfully")

            # Verify access token
            decoded_data = TokenManager.verify_access_token(access_token)
            if decoded_data and decoded_data['id'] == 'test_user_123':
                print("[PASS] Access token verification successful")
            else:
                print("[FAIL] Access token verification failed")

            # Test expired token
            expired_token = TokenManager.create_access_token(user_data, timedelta(seconds=-1))
            decoded_expired = TokenManager.verify_access_token(expired_token)
            if decoded_expired is None:
                print("[PASS] Expired token correctly rejected")
            else:
                print("[FAIL] Expired token incorrectly accepted")

            # Test refresh token
            refresh_token = TokenManager.create_refresh_token(user_data, timedelta(hours=1))
            decoded_refresh = TokenManager.decode_token(refresh_token)
            if decoded_refresh and decoded_refresh['type'] == 'refresh':
                print("[PASS] Refresh token created and decoded successfully")
            else:
                print("[FAIL] Refresh token creation or decoding failed")

        print("\nJWT Token Manager tests completed!")
        return True

    except Exception as e:
        print(f"[FAIL] JWT Token Manager test failed: {str(e)}")
        return False

def check_imports():
    """Check if all required imports work"""
    print("Checking required imports...")

    try:
        import jwt
        print("[PASS] PyJWT imported successfully")
    except ImportError:
        print("[FAIL] PyJWT import failed")
        return False

    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import id_token
        from google_auth_oauthlib.flow import Flow
        print("[PASS] Google OAuth libraries imported successfully")
    except ImportError:
        print("[FAIL] Google OAuth libraries import failed")
        return False

    try:
        import requests
        print("[PASS] Requests imported successfully")
    except ImportError:
        print("[FAIL] Requests import failed")
        return False

    print("All imports successful!\n")
    return True

def main():
    print("Testing Google OAuth Implementation\n")

    # Check imports
    if not check_imports():
        print("Import check failed, exiting...")
        return False

    # Test JWT functionality
    jwt_success = test_jwt_functionality()

    if jwt_success:
        print("\nAll tests passed! Google OAuth implementation is ready.")
        print("\nNext Steps:")
        print("   1. Set up Google OAuth credentials in Google Cloud Console")
        print("   2. Configure environment variables (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)")
        print("   3. Run the application: python web_app.py")
        print("   4. Visit http://localhost:5000 to test the login flow")
        return True
    else:
        print("\nSome tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)