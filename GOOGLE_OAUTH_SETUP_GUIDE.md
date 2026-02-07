# Google OAuth 2.0 Setup Guide

This guide explains how to set up Google OAuth 2.0 for secure user authentication in your web application.

## Prerequisites

- Google Cloud Platform account
- Flask application with the following dependencies:
  - `google-auth`
  - `google-auth-oauthlib`
  - `PyJWT` (for token management)
  - `requests`

## Step 1: Create Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top, then "New Project"
3. Enter a project name (e.g., "My Flask App")
4. Click "Create"

## Step 2: Enable Google+ API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google+ API" (or "People API" as Google+ has been deprecated)
3. Click on "Google People API"
4. Click "Enable"

## Step 3: Create OAuth 2.0 Client ID

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. If prompted to configure the OAuth consent screen, do so:
   - Select "External" for user type
   - Enter an app name (e.g., "My Flask App")
   - Add your email to user information
   - Click "Save and Continue"
   - Click "Publish App" (for testing purposes)

4. After configuring consent screen, create OAuth 2.0 Client ID:
   - Application type: Web application
   - Name: Your app name
   - Authorized JavaScript origins:
     - `http://localhost:5000`
     - `http://127.0.0.1:5000`
   - Authorized redirect URIs:
     - `http://localhost:5000/auth/google/callback`
     - `http://127.0.0.1:5000/auth/google/callback`
   - Click "Create"

5. Download the credentials JSON file or copy the Client ID and Client Secret

## Step 4: Configure Environment Variables

Create a `.env` file in your project root:

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
SECRET_KEY=your_secret_key_here
```

Or set environment variables directly:

```bash
export GOOGLE_CLIENT_ID="your_client_id_here"
export GOOGLE_CLIENT_SECRET="your_client_secret_here"
export SECRET_KEY="your_secret_key_here"
```

## Step 5: Flask Application Integration

### OAuth Routes

Your Flask app should have these routes:

1. `/login/google` - Initiates Google OAuth flow
2. `/auth/google/callback` - Handles OAuth callback

### Security Best Practices Implemented

1. **State Parameter Validation**: Prevents CSRF attacks
2. **Token Validation**: Verifies tokens with Google's tokeninfo endpoint
3. **Audience Validation**: Ensures tokens are issued for your client
4. **Email Verification**: Confirms user's email is verified
5. **JWT Token Management**: Secure session handling

### Database Integration

The system creates user records in the database upon first login and updates existing records on subsequent logins.

## Step 6: Error Handling

The implementation includes comprehensive error handling for:

- Invalid credentials
- Cancelled consent
- Network errors
- Token validation failures
- State mismatch errors

## Step 7: Testing

1. Start your Flask application
2. Navigate to your login page
3. Click "Sign in with Google"
4. Complete the Google authentication process
5. Verify that user information is correctly stored and retrieved

## Security Considerations

- Never store Google passwords (OAuth tokens only)
- Validate callback URLs to prevent phishing attacks
- Use HTTPS in production
- Implement proper session management
- Regularly rotate secrets
- Monitor for suspicious activity

## Troubleshooting

### Common Issues:

1. **Invalid Grant Error**: Usually caused by incorrect redirect URI
2. **Origin not allowed**: Check authorized origins in Google Cloud Console
3. **Callback mismatch**: Verify redirect URIs match exactly

### Debugging Tips:

- Enable logging to see OAuth flow details
- Check browser console for JavaScript errors
- Verify environment variables are set correctly
- Ensure your application can reach Google's OAuth servers

## Production Considerations

- Use HTTPS for all authentication requests
- Implement proper logging and monitoring
- Set up proper error reporting
- Regular security audits
- Proper session timeout mechanisms
- Secure secret management (not hardcoded)

## Sample Code Structure

```python
from flask import Flask, session, redirect, url_for, request
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from backend.token_manager import TokenManager
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

@app.route('/login/google')
def google_login():
    # Implementation as shown in web_app.py

@app.route('/auth/google/callback')
def google_callback():
    # Implementation as shown in web_app.py
```

This implementation provides a secure, production-ready Google OAuth 2.0 integration with proper security measures and error handling.