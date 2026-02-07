
#!/usr/bin/env python3
"""
Web API for the Project-Based Task Management Application
Simple Flask app with essential routes
"""

from flask import Flask, request, jsonify, session, send_from_directory, redirect, url_for, make_response
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from backend.models import *
from backend.storage import Storage
from backend.token_manager import TokenManager
from werkzeug.security import check_password_hash, generate_password_hash
import json
import re
import uuid
from datetime import datetime, timedelta
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file FIRST, before any other operations
load_dotenv()

app = Flask(__name__)
# Set static folder to the static directory in the root
app.static_folder = 'static'
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# OAuth configuration
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Only for development

# OAuth configuration object - single source of truth
class OAuthConfig:
    def __init__(self):
        self.GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
        self.GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
        self.FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID')
        self.FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_CLIENT_SECRET')
        self.GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
        self.GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')

oauth_config = OAuthConfig()

# Initialize the storage
storage = Storage()

def validate_oauth_configuration():
    """Validate OAuth provider configurations at startup"""
    print("[INFO] Validating OAuth provider configurations...")

    providers_status = {}

    # Define exact placeholder strings to check against
    exact_placeholders = {
        'your_google_client_id_here',
        'your_google_client_secret_here',
        'your_facebook_client_id_here',
        'your_facebook_client_secret_here',
        'your_github_client_id_here',
        'your_github_client_secret_here',
        'your_client_id_here',
        'your_client_secret_here',
        'change_me',
        'update_this',
        'placeholder',
        'example',
        ''
    }

    def is_exact_placeholder_value(value):
        """Check if a value is an exact placeholder string"""
        if value is None:
            return True  # None is considered a placeholder
        return value.strip().lower() in exact_placeholders

    def is_empty_or_whitespace(value):
        """Check if a value is empty or contains only whitespace"""
        return value is None or value.strip() == ""

    # Check Google OAuth
    google_client_id_missing = is_empty_or_whitespace(oauth_config.GOOGLE_CLIENT_ID)
    google_client_secret_missing = is_empty_or_whitespace(oauth_config.GOOGLE_CLIENT_SECRET)
    google_has_placeholder = is_exact_placeholder_value(oauth_config.GOOGLE_CLIENT_ID) or is_exact_placeholder_value(oauth_config.GOOGLE_CLIENT_SECRET)

    if google_client_id_missing or google_client_secret_missing:
        if google_client_id_missing and google_client_secret_missing:
            print("[WARN] Google OAuth: Not configured (missing CLIENT_ID and CLIENT_SECRET)")
        elif google_client_id_missing:
            print("[WARN] Google OAuth: Not configured (missing CLIENT_ID)")
        else:
            print("[WARN] Google OAuth: Not configured (missing CLIENT_SECRET)")
        providers_status['google'] = False
    elif google_has_placeholder:
        print("[WARN] Google OAuth: Not configured (placeholder values detected)")
        providers_status['google'] = False
    else:
        print("[OK] Google OAuth: Configured")
        providers_status['google'] = True

    # Check Facebook OAuth
    fb_client_id_missing = is_empty_or_whitespace(oauth_config.FACEBOOK_CLIENT_ID)
    fb_client_secret_missing = is_empty_or_whitespace(oauth_config.FACEBOOK_CLIENT_SECRET)
    fb_has_placeholder = is_exact_placeholder_value(oauth_config.FACEBOOK_CLIENT_ID) or is_exact_placeholder_value(oauth_config.FACEBOOK_CLIENT_SECRET)

    if fb_client_id_missing or fb_client_secret_missing:
        if fb_client_id_missing and fb_client_secret_missing:
            print("[WARN] Facebook OAuth: Not configured (missing CLIENT_ID and CLIENT_SECRET)")
        elif fb_client_id_missing:
            print("[WARN] Facebook OAuth: Not configured (missing CLIENT_ID)")
        else:
            print("[WARN] Facebook OAuth: Not configured (missing CLIENT_SECRET)")
        providers_status['facebook'] = False
    elif fb_has_placeholder:
        print("[WARN] Facebook OAuth: Not configured (placeholder values detected)")
        providers_status['facebook'] = False
    else:
        print("[OK] Facebook OAuth: Configured")
        providers_status['facebook'] = True

    # Check GitHub OAuth
    gh_client_id_missing = is_empty_or_whitespace(oauth_config.GITHUB_CLIENT_ID)
    gh_client_secret_missing = is_empty_or_whitespace(oauth_config.GITHUB_CLIENT_SECRET)
    gh_has_placeholder = is_exact_placeholder_value(oauth_config.GITHUB_CLIENT_ID) or is_exact_placeholder_value(oauth_config.GITHUB_CLIENT_SECRET)

    if gh_client_id_missing or gh_client_secret_missing:
        if gh_client_id_missing and gh_client_secret_missing:
            print("[WARN] GitHub OAuth: Not configured (missing CLIENT_ID and CLIENT_SECRET)")
        elif gh_client_id_missing:
            print("[WARN] GitHub OAuth: Not configured (missing CLIENT_ID)")
        else:
            print("[WARN] GitHub OAuth: Not configured (missing CLIENT_SECRET)")
        providers_status['github'] = False
    elif gh_has_placeholder:
        print("[WARN] GitHub OAuth: Not configured (placeholder values detected)")
        providers_status['github'] = False
    else:
        print("[OK] GitHub OAuth: Configured")
        providers_status['github'] = True

    print(f"[STATUS] OAuth Provider Status: {providers_status}")
    return providers_status

# Validate OAuth configuration at startup
oauth_providers = validate_oauth_configuration()

# ROOT ROUTE - CRITICAL: Must never return 404
@app.route('/')
def index():
    """Serve the main application page - redirects based on auth status"""
    if 'user_id' in session:
        # User is logged in, redirect to dashboard
        return send_from_directory('static', 'index.html')
    else:
        # User is not logged in, redirect to login
        return send_from_directory('static', 'login.html')

# AUTHENTICATION ROUTES
@app.route('/login')
def login_page():
    """Serve the login page"""
    error = request.args.get('error')
    # Since we can't pass variables to static files directly, we'll serve the login page
    # and the frontend will handle showing error messages via URL parameters
    return send_from_directory('static', 'login.html')

@app.route('/signup')
def signup_page():
    """Serve the signup page"""
    return send_from_directory('static', 'login.html')

@app.route('/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    session.pop('user_id', None)
    return send_from_directory('static', 'login.html')

@app.route('/dashboard')
def dashboard():
    """Serve the dashboard page - check authentication first"""
    if 'user_id' not in session:
        return send_from_directory('static', 'login.html')  # Redirect to login if not authenticated
    return send_from_directory('static', 'index.html')

@app.route('/tasks/<project_id>')
def tasks_page(project_id):
    """Serve the tasks page for a specific project"""
    if 'user_id' not in session:
        return send_from_directory('static', 'login.html')  # Redirect to login if not authenticated
    return send_from_directory('static', 'index.html')

# API ENDPOINTS
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()

        if not data or 'username' not in data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        username = data['username']
        email = data['email']
        password = data['password']
        confirm_password = data.get('confirm_password')

        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'error': 'Invalid email format'}), 400

        # Validate password confirmation if provided
        if confirm_password and password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400

        # Check if user already exists by looking through stored users
        users = storage.data.get("users", {})
        for user_id, user_data in users.items():
            if user_data.get('username') == username:
                return jsonify({'error': 'Username already taken'}), 400
            if user_data.get('email') == email:
                return jsonify({'error': 'Email already registered'}), 400

        # Hash password and create user
        password_hash = generate_password_hash(password)
        user_id = str(uuid.uuid4())

        # Store user in storage
        user_data = {
            'id': user_id,
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.now().isoformat()
        }

        # Add user to storage data
        storage.data["users"][user_id] = user_data
        storage.save_data()

        # Log the user in by storing user ID in session
        session['user_id'] = user_id

        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'username': username,
                'email': email
            }
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/signin', methods=['POST'])
def signin():
    """User authentication endpoint"""
    try:
        data = request.get_json()

        if not data or ('username' not in data and 'email' not in data) or 'password' not in data:
            return jsonify({'error': 'Missing email or username and password'}), 400

        identifier = data.get('username') or data.get('email')
        password = data['password']

        # Validate email format if it looks like an email
        if '@' in identifier:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, identifier):
                return jsonify({'error': 'Invalid email format'}), 400

        # Get user from storage - search by either username or email
        users = storage.data.get("users", {})
        user = None
        for user_id, user_data in users.items():
            if user_data.get('username') == identifier or user_data.get('email') == identifier:
                user = user_data
                break

        if not user or 'password_hash' not in user or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid email/username or password'}), 401

        # Log the user in by storing user ID in session
        session['user_id'] = user['id']

        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/signout', methods=['POST'])
def signout():
    """User signout endpoint"""
    session.pop('user_id', None)
    return jsonify({'success': True}), 200

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get current authenticated user"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        users = storage.data.get("users", {})
        user = users.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/token', methods=['POST'])
def get_auth_token():
    """Generate JWT token for authenticated user"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        users = storage.data.get("users", {})
        user = users.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Prepare user data for token
        user_data = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'logged_in_with': session.get('logged_in_with', 'email/password')
        }

        # Create access token (valid for 1 hour)
        access_token = TokenManager.create_access_token(user_data, timedelta(hours=1))

        # Create refresh token (valid for 30 days) - only for OAuth users
        refresh_token = None
        if session.get('logged_in_with') in ['google', 'facebook', 'github']:
            refresh_token = TokenManager.create_refresh_token(user_data, timedelta(days=30))

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600  # 1 hour in seconds
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/refresh', methods=['POST'])
def refresh_auth_token():
    """Refresh access token using refresh token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')

        if not refresh_token:
            return jsonify({'error': 'Refresh token required'}), 400

        # Decode and validate refresh token
        decoded_token = TokenManager.decode_token(refresh_token)
        if not decoded_token or decoded_token.get('type') != 'refresh':
            return jsonify({'error': 'Invalid refresh token'}), 401

        user_data = decoded_token.get('user_data')
        if not user_data:
            return jsonify({'error': 'Invalid token data'}), 401

        # Create new access token
        new_access_token = TokenManager.create_access_token(user_data, timedelta(hours=1))

        return jsonify({
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': 3600  # 1 hour in seconds
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# OAUTH ROUTES
@app.route('/login/google')
def google_login():
    """Initiate Google OAuth login"""
    try:
        # Check if Google OAuth is properly configured
        if not oauth_providers.get('google', False):
            error_msg = "Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
            print(f"Google OAuth blocked: {error_msg}")
            return redirect(url_for('login_page') + f'?error={error_msg}')

        # Google OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": oauth_config.GOOGLE_CLIENT_ID,
                    "client_secret": oauth_config.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [url_for('google_callback', _external=True)]  # Use dynamic callback URL
                }
            },
            scopes=["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid"]
        )

        flow.redirect_uri = url_for('google_callback', _external=True)

        authorization_url, state = flow.authorization_url(
            access_type='online',  # Changed to online for better security (no refresh tokens unless needed)
            include_granted_scopes='true'
        )

        # Store state in session for security
        session['oauth_state'] = state
        session['oauth_provider'] = 'google'

        print(f"Redirecting to Google OAuth: {authorization_url}")
        return redirect(authorization_url)

    except Exception as e:
        print(f"Error in google_login: {str(e)}")
        return redirect(url_for('login_page') + '?error=Google OAuth setup failed')




@app.route('/login/facebook')
def facebook_login():
    """Initiate Facebook OAuth login"""
    try:
        # Check if Facebook OAuth is properly configured
        if not oauth_providers.get('facebook', False):
            error_msg = "Facebook OAuth is not configured. Please set FACEBOOK_CLIENT_ID and FACEBOOK_CLIENT_SECRET environment variables."
            print(f"Facebook OAuth blocked: {error_msg}")
            return redirect(url_for('login_page') + f'?error={error_msg}')

        # Build authorization URL
        params = {
            'client_id': oauth_config.FACEBOOK_CLIENT_ID,
            'redirect_uri': url_for('facebook_callback', _external=True),
            'scope': 'email,public_profile',
            'state': os.urandom(24).hex()  # Generate random state
        }

        session['oauth_state'] = params['state']
        session['oauth_provider'] = 'facebook'

        auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        print(f"Redirecting to Facebook OAuth: {auth_url}")
        return redirect(auth_url)

    except Exception as e:
        print(f"Error in facebook_login: {str(e)}")
        return redirect(url_for('login_page') + '?error=Facebook OAuth setup failed')


@app.route('/auth/facebook/callback')
def facebook_callback():
    """Handle Facebook OAuth callback"""
    try:
        # Verify state parameter
        if request.args.get('state') != session.get('oauth_state'):
            print("Facebook OAuth: State mismatch error")
            return redirect(url_for('login_page') + '?error=Authentication failed: Invalid state')

        # Get authorization code
        code = request.args.get('code')
        if not code:
            print("Facebook OAuth: No authorization code received")
            return redirect(url_for('login_page') + '?error=Authentication failed: No code received')

        # Exchange code for access token
        token_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
        token_params = {
            'client_id': FACEBOOK_CLIENT_ID,
            'client_secret': FACEBOOK_CLIENT_SECRET,
            'redirect_uri': url_for('facebook_callback', _external=True),
            'code': code
        }

        token_response = requests.get(token_url, params=token_params)
        token_json = token_response.json()

        if 'access_token' not in token_json:
            error_msg = token_json.get("error", "Unknown error")
            print(f"Facebook OAuth: Failed to get access token - {error_msg}")
            return redirect(url_for('login_page') + f'?error=Failed to authenticate: {error_msg}')

        access_token = token_json['access_token']

        # Get user info
        user_fields = 'id,name,email'
        user_url = f'https://graph.facebook.com/me?fields={user_fields}&access_token={access_token}'
        user_response = requests.get(user_url)
        user_info = user_response.json()

        if 'id' not in user_info:
            print("Facebook OAuth: Could not retrieve user information")
            return redirect(url_for('login_page') + '?error=Could not retrieve user information')

        # Extract user data
        fb_id = user_info.get('id')
        name = user_info.get('name', f'FacebookUser_{fb_id}')
        email = user_info.get('email', f'facebook_{fb_id}@example.com')

        print(f"Facebook OAuth successful: {email}")

        # Use Facebook ID as user identifier
        user_id = f'facebook_{fb_id}'

        # Store user info in session
        session['user_id'] = user_id
        session['user_email'] = email
        session['user_name'] = name
        session['logged_in_with'] = 'facebook'

        # Add to users_db if not exists
        users = storage.data.get("users", {})
        if user_id not in users:
            user_data = {
                'id': user_id,
                'username': name,
                'email': email,
                'avatar': None,  # Facebook avatar would come from profile API
                'password_hash': None  # No password for OAuth users
            }
            storage.data["users"][user_id] = user_data
            storage.save_data()
        else:
            # Update existing user info if needed
            user_data = users[user_id]
            user_data.update({
                'username': name,
                'email': email
            })
            storage.save_data()

        # Generate JWT tokens for the authenticated user
        token_user_data = {
            'id': user_id,
            'username': name,
            'email': email,
            'avatar': None,  # Include avatar in token (None for Facebook for now)
            'provider': 'facebook'
        }

        # Create access token
        access_token = TokenManager.create_access_token(token_user_data, timedelta(hours=1))

        # Create refresh token for OAuth users
        refresh_token = TokenManager.create_refresh_token(token_user_data, timedelta(days=30))

        # Set tokens in session for server-side use
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token

        # Redirect to dashboard
        return redirect(url_for('dashboard'))

    except Exception as e:
        print(f"Facebook OAuth error: {str(e)}")
        return redirect(url_for('login_page') + f'?error=Facebook authentication failed: {str(e)}')


@app.route('/login/github')
def github_login():
    """Initiate GitHub OAuth login"""
    try:
        # Check if GitHub OAuth is properly configured
        if not oauth_providers.get('github', False):
            error_msg = "GitHub OAuth is not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables."
            print(f"GitHub OAuth blocked: {error_msg}")
            return redirect(url_for('login_page') + f'?error={error_msg}')

        # Build authorization URL
        params = {
            'client_id': oauth_config.GITHUB_CLIENT_ID,
            'redirect_uri': url_for('github_callback', _external=True),
            'scope': 'user:email',
            'state': os.urandom(24).hex()  # Generate random state
        }

        session['oauth_state'] = params['state']
        session['oauth_provider'] = 'github'

        auth_url = f"https://github.com/login/oauth/authorize?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        print(f"Redirecting to GitHub OAuth: {auth_url}")
        return redirect(auth_url)

    except Exception as e:
        print(f"Error in github_login: {str(e)}")
        return redirect(url_for('login_page') + '?error=GitHub OAuth setup failed')


@app.route('/auth/github/callback')
def github_callback():
    """Handle GitHub OAuth callback"""
    try:
        # Verify state parameter
        if request.args.get('state') != session.get('oauth_state'):
            print("GitHub OAuth: State mismatch error")
            return redirect(url_for('login_page') + '?error=Authentication failed: Invalid state')

        # Get authorization code
        code = request.args.get('code')
        if not code:
            print("GitHub OAuth: No authorization code received")
            return redirect(url_for('login_page') + '?error=Authentication failed: No code received')

        # Exchange code for access token
        token_url = 'https://github.com/login/oauth/access_token'
        token_data = {
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'redirect_uri': url_for('github_callback', _external=True),
            'code': code
        }

        headers = {'Accept': 'application/json'}
        token_response = requests.post(token_url, data=token_data, headers=headers)
        token_json = token_response.json()

        if 'access_token' not in token_json:
            error_msg = token_json.get("error", "Unknown error")
            print(f"GitHub OAuth: Failed to get access token - {error_msg}")
            return redirect(url_for('login_page') + f'?error=Failed to authenticate: {error_msg}')

        access_token = token_json['access_token']

        # Get user info
        user_headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/json'
        }

        user_response = requests.get('https://api.github.com/user', headers=user_headers)
        user_info = user_response.json()

        if 'id' not in user_info:
            print("GitHub OAuth: Could not retrieve user information")
            return redirect(url_for('login_page') + '?error=Could not retrieve user information')

        # Get user email (may need separate call)
        email_response = requests.get('https://api.github.com/user/emails', headers=user_headers)
        emails = email_response.json()
        email = None
        for email_obj in emails:
            if email_obj.get('primary') and email_obj.get('verified'):
                email = email_obj['email']
                break

        if not email:
            email = f"github_{user_info['id']}@example.com"  # Fallback

        # Extract user data
        name = user_info.get('name') or user_info.get('login')
        avatar = user_info.get('avatar_url')  # Get GitHub avatar
        user_id = f"github_{user_info['id']}"

        print(f"GitHub OAuth successful: {email}")

        # Store user info in session
        session['user_id'] = user_id
        session['user_email'] = email
        session['user_name'] = name
        session['user_avatar'] = avatar  # Store avatar
        session['logged_in_with'] = 'github'

        # Add to users_db if not exists
        users = storage.data.get("users", {})
        if user_id not in users:
            user_data = {
                'id': user_id,
                'username': name,
                'email': email,
                'avatar': avatar,  # Store avatar in user data
                'password_hash': None  # No password for OAuth users
            }
            storage.data["users"][user_id] = user_data
            storage.save_data()
        else:
            # Update existing user info if needed
            user_data = users[user_id]
            user_data.update({
                'username': name,
                'email': email,
                'avatar': avatar  # Update avatar
            })
            storage.save_data()

        # Generate JWT tokens for the authenticated user
        token_user_data = {
            'id': user_id,
            'username': name,
            'email': email,
            'avatar': avatar,  # Include avatar in token
            'provider': 'github'
        }

        # Create access token
        access_token = TokenManager.create_access_token(token_user_data, timedelta(hours=1))

        # Create refresh token for OAuth users
        refresh_token = TokenManager.create_refresh_token(token_user_data, timedelta(days=30))

        # Set tokens in session for server-side use
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token

        # Redirect to dashboard
        return redirect(url_for('dashboard'))

    except Exception as e:
        print(f"GitHub OAuth error: {str(e)}")
        return redirect(url_for('login_page') + f'?error=GitHub authentication failed: {str(e)}')


@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Verify state parameter to prevent CSRF attacks
        if request.args.get('state') != session.get('oauth_state'):
            print("Google OAuth: State mismatch error")
            return redirect(url_for('login_page') + '?error=Authentication failed: Invalid state')

        # Verify the oauth_provider is google
        if session.get('oauth_provider') != 'google':
            print("Google OAuth: Invalid provider in session")
            return redirect(url_for('login_page') + '?error=Authentication failed: Invalid provider')

        # Get authorization code
        code = request.args.get('code')
        if not code:
            print("Google OAuth: No authorization code received")
            return redirect(url_for('login_page') + '?error=Authentication failed: No code received')

        # Exchange code for token - this is where we need to validate the token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': url_for('google_callback', _external=True),
            'grant_type': 'authorization_code',
            'code': code
        }

        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if 'access_token' not in token_json:
            error_msg = token_json.get("error_description", "Unknown error")
            print(f"Google OAuth: Failed to get access token - {error_msg}")
            return redirect(url_for('login_page') + f'?error=Failed to authenticate: {error_msg}')

        access_token = token_json['access_token']

        # Validate the token by getting user info from Google
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        user_headers = {'Authorization': f'Bearer {access_token}'}

        # Additional security: Validate the token using Google's tokeninfo endpoint
        tokeninfo_url = 'https://oauth2.googleapis.com/tokeninfo'
        tokeninfo_params = {'access_token': access_token}
        tokeninfo_response = requests.get(tokeninfo_url, params=tokeninfo_params)
        tokeninfo_json = tokeninfo_response.json()

        if 'error' in tokeninfo_json:
            print(f"Google OAuth: Token validation failed - {tokeninfo_json.get('error_description', 'Token validation failed')}")
            return redirect(url_for('login_page') + '?error=Token validation failed')

        # Double-check that the token is for our client
        if tokeninfo_json.get('audience') != GOOGLE_CLIENT_ID:
            print(f"Google OAuth: Token audience mismatch - {tokeninfo_json.get('audience')} vs {GOOGLE_CLIENT_ID}")
            return redirect(url_for('login_page') + '?error=Invalid token audience')

        # Get user info
        user_response = requests.get(user_info_url, headers=user_headers)
        user_info = user_response.json()

        if 'email' not in user_info or not user_info.get('email_verified'):
            print("Google OAuth: Email not verified or not provided")
            return redirect(url_for('login_page') + '?error=Email not verified')

        # Extract user data
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0])
        user_id = str(user_info.get('id', email))  # Use Google ID or email as user ID

        # Additional security: Verify that the email domain is allowed if needed
        # (For now, accepting all Gmail accounts)

        print(f"Google OAuth successful: {email}")

        # Store user info in session
        session['user_id'] = user_id
        session['user_email'] = email
        session['user_name'] = name
        session['logged_in_with'] = 'google'

        # Add to users_db if not exists
        users = storage.data.get("users", {})
        if user_id not in users:
            user_data = {
                'id': user_id,
                'username': name,
                'email': email,
                'password_hash': None,  # No password for OAuth users
                'created_at': datetime.now().isoformat()
            }
            storage.data["users"][user_id] = user_data
            storage.save_data()
        else:
            # Update existing user info if needed
            user_data = users[user_id]
            user_data.update({
                'username': name,
                'email': email
            })
            storage.save_data()

        # Generate JWT tokens for the authenticated user
        user_data = {
            'id': user_id,
            'username': name,
            'email': email,
            'provider': 'google'
        }

        # Create access token
        access_token = TokenManager.create_access_token(user_data, timedelta(hours=1))

        # Create refresh token for OAuth users
        refresh_token = TokenManager.create_refresh_token(user_data, timedelta(days=30))

        # Set tokens in session for server-side use
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token

        # Clean up session state
        session.pop('oauth_state', None)
        session.pop('oauth_provider', None)

        # Redirect to dashboard
        return redirect(url_for('dashboard'))

    except Exception as e:
        print(f"Google OAuth error: {str(e)}")
        # Clean up session on error
        session.pop('oauth_state', None)
        session.pop('oauth_provider', None)
        return redirect(url_for('login_page') + f'?error=Google authentication failed: {str(e)}')

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all projects for current user"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        projects = storage.get_projects_for_user(user_id)

        return jsonify({
            'success': True,
            'projects': [project.to_dict() for project in projects]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/projects', methods=['GET'])
def get_user_projects():
    """Get all projects for the current user (specifically for tasks page dropdown)"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        projects = storage.get_projects_for_user(user_id)

        # Return simplified project list for dropdown
        project_options = [{'id': project.id, 'name': project.name} for project in projects]

        return jsonify({
            'success': True,
            'projects': project_options
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        data = request.get_json()

        if not data or 'name' not in data:
            return jsonify({'error': 'Project name is required'}), 400

        name = data['name']
        description = data.get('description', '')

        # Create new project
        project = Project(name=name, user_id=user_id)
        project.description = description

        # Save to storage
        storage.save_project(project)

        # Log the activity
        storage.log_activity(
            user_id=user_id,
            activity_type="project_created",
            project_id=project.id,
            description=f"Created project '{project.name}'"
        )

        # Create a default task for the project
        default_task = Task(
            title=f"Default task for {project.name}",
            description=f"This is the default task for the project '{project.name}'.",
            completed=False,
            created_by=user_id,
            project_id=project.id
        )
        storage.save_task(default_task)

        # Log the default task creation
        storage.log_activity(
            user_id=user_id,
            activity_type="task_created",
            project_id=project.id,
            task_id=default_task.id,
            description=f"Created default task '{default_task.title}' in project '{project.name}'"
        )

        return jsonify({
            'success': True,
            'project': project.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['PUT'])
def select_project(project_id):
    """Select an active project (for frontend compatibility)"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        # Verify that the project belongs to the user
        project = storage.get_project(project_id)
        if not project or project.user_id != user_id:
            return jsonify({'error': 'Project not found or access denied'}), 404

        # For now, just return the project to confirm selection
        return jsonify({
            'success': True,
            'project': project.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project and all related tasks and activities"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        # Verify that the project belongs to the user
        project = storage.get_project(project_id)
        if not project or project.user_id != user_id:
            return jsonify({'error': 'Project not found or access denied'}), 404

        # Delete the project and all related data
        storage.delete_project_and_related_data(user_id, project_id)

        # Log the activity
        storage.log_activity(
            user_id=user_id,
            activity_type="project_deleted",
            project_id=project_id,
            description=f"Deleted project '{project.name}'"
        )

        return jsonify({
            'success': True,
            'message': 'Project and all related tasks deleted successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get tasks for current user and optionally for a specific project"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        # Get project_id from query params
        project_id = request.args.get('project_id')

        if project_id:
            # Get tasks for specific project
            # Verify that the project belongs to the user
            project = storage.get_project(project_id)
            if not project or project.user_id != user_id:
                return jsonify({'error': 'Project not found or access denied'}), 404

            tasks = storage.get_tasks_for_project(user_id, project_id)
        else:
            # Get all tasks for the user across all projects
            tasks = storage.get_all_user_tasks(user_id)

        return jsonify({
            'success': True,
            'tasks': [task.to_dict() for task in tasks]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        data = request.get_json()

        if not data or 'title' not in data:
            return jsonify({'error': 'Task title is required'}), 400

        title = data['title']
        description = data.get('description', '')
        project_id = data.get('project_id')

        # Validate that project_id is provided
        if not project_id:
            return jsonify({'error': 'Project ID is required'}), 400

        # Verify that the project belongs to the user
        project = storage.get_project(project_id)
        if not project or project.user_id != user_id:
            return jsonify({'error': 'Project not found or access denied'}), 404

        completed = data.get('completed', False)

        # Create new task
        task = Task(
            title=title,
            description=description,
            completed=completed,
            created_by=user_id,
            project_id=project_id
        )

        # Save to storage
        storage.save_task(task)

        return jsonify({
            'success': True,
            'task': task.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        # Get all tasks for the user to find the specific task
        all_user_tasks = storage.get_all_user_tasks(user_id)
        task = None
        for t in all_user_tasks:
            if t.id == task_id:
                task = t
                break

        if not task:
            return jsonify({'error': 'Task not found'}), 404

        # Verify that the task belongs to a project owned by the user
        project = storage.get_project(task.project_id)
        if not project or project.user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update task fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'completed' in data:
            task.completed = data['completed']

        task.updated_at = datetime.now()

        # Save updated task
        storage.save_task(task)

        return jsonify({
            'success': True,
            'task': task.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Mark a task as completed (for frontend compatibility)"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        # Find the task among all user tasks to identify which project it belongs to
        user_projects = storage.get_projects_for_user(user_id)
        project_id = None
        task = None

        for proj in user_projects:
            tasks_in_proj = storage.get_tasks_for_project(user_id, proj.id)
            for t in tasks_in_proj:
                if t.id == task_id:
                    task = t
                    project_id = proj.id
                    break
            if task and project_id:
                break

        if not task or not project_id:
            return jsonify({'error': 'Task not found'}), 404

        # Mark task as completed
        task.completed = True
        task.updated_at = datetime.now()

        # Save updated task
        storage.save_task(task)

        return jsonify({
            'success': True,
            'task': task.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add DELETE endpoint for reopening tasks (opposite of completion)
@app.route('/api/tasks/<int:task_id>/complete', methods=['DELETE'])
def reopen_task(task_id):
    """Reopen a completed task (for frontend compatibility)"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        # Find the task among all user tasks to identify which project it belongs to
        user_projects = storage.get_projects_for_user(user_id)
        project_id = None
        task = None

        for proj in user_projects:
            tasks_in_proj = storage.get_tasks_for_project(user_id, proj.id)
            for t in tasks_in_proj:
                if t.id == task_id:
                    task = t
                    project_id = proj.id
                    break
            if task and project_id:
                break

        if not task or not project_id:
            return jsonify({'error': 'Task not found'}), 404

        # Mark task as not completed
        task.completed = False
        task.updated_at = datetime.now()

        # Save updated task
        storage.save_task(task)

        return jsonify({
            'success': True,
            'task': task.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        # Find the task among all user tasks to identify which project it belongs to
        user_projects = storage.get_projects_for_user(user_id)
        project_id = None
        task_to_delete = None

        for proj in user_projects:
            tasks_in_proj = storage.get_tasks_for_project(user_id, proj.id)
            for task in tasks_in_proj:
                if task.id == task_id:
                    task_to_delete = task
                    project_id = proj.id
                    break
            if project_id:
                break

        if not project_id or not task_to_delete:
            return jsonify({'error': 'Task not found'}), 404

        # Delete the task
        storage.delete_task(user_id, project_id, task_id)

        # Log the activity
        storage.log_activity(
            user_id=user_id,
            activity_type="task_deleted",
            project_id=project_id,
            task_id=task_id,
            description=f"Deleted task '{task_to_delete.title}'"
        )

        return jsonify({
            'success': True,
            'message': 'Task deleted successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent-activities', methods=['GET'])
def get_recent_activities():
    """Get recent activities for the current user"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        # Get recent activities
        activities = storage.get_recent_activities(user_id, limit=10)

        return jsonify({
            'success': True,
            'activities': activities
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/tasks', methods=['GET'])
def get_tasks_for_project(project_id):
    """Get all tasks for a specific project"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        # Verify that the project belongs to the user
        project = storage.get_project(project_id)
        if not project or project.user_id != user_id:
            return jsonify({'error': 'Project not found or access denied'}), 404

        # Get tasks for the project
        tasks = storage.get_tasks_for_project(user_id, project_id)

        return jsonify({
            'success': True,
            'tasks': [task.to_dict() for task in tasks]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/tasks', methods=['POST'])
def create_task_for_project(project_id):
    """Create a new task for a specific project"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        # Verify that the project belongs to the user
        project = storage.get_project(project_id)
        if not project or project.user_id != user_id:
            return jsonify({'error': 'Project not found or access denied'}), 404

        data = request.get_json()

        if not data or 'title' not in data:
            return jsonify({'error': 'Task title is required'}), 400

        title = data['title']
        description = data.get('description', '')
        completed = data.get('completed', False)

        # Create new task for the project
        task = Task(
            title=title,
            description=description,
            completed=completed,
            created_by=user_id,
            project_id=project_id
        )

        # Save to storage
        storage.save_task(task)

        # Log the activity
        storage.log_activity(
            user_id=user_id,
            activity_type="task_created",
            project_id=project_id,
            task_id=task.id,
            description=f"Created task '{task.title}' in project '{project.name}'"
        )

        return jsonify({
            'success': True,
            'task': task.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/tasks/<int:task_id>/toggle', methods=['PUT'])
def toggle_task_completion(project_id, task_id):
    """Toggle task completion status"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        # Verify that the project belongs to the user
        project = storage.get_project(project_id)
        if not project or project.user_id != user_id:
            return jsonify({'error': 'Project not found or access denied'}), 404

        # Find the task in the specific project
        tasks = storage.get_tasks_for_project(user_id, project_id)
        task = None
        for t in tasks:
            if t.id == task_id:
                task = t
                break

        if not task:
            return jsonify({'error': 'Task not found'}), 404

        # Toggle completion status
        task.completed = not task.completed
        task.updated_at = datetime.now()

        # Save updated task
        storage.save_task(task)

        # Log the activity
        status_text = "completed" if task.completed else "reopened"
        storage.log_activity(
            user_id=user_id,
            activity_type="task_updated",
            project_id=project_id,
            task_id=task_id,
            description=f"{status_text.capitalize()} task '{task.title}' in project '{project.name}'"
        )

        return jsonify({
            'success': True,
            'task': task.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve static files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)


@app.route('/favicon.ico')
def favicon():
    # Return an empty response with 200 status to prevent 404
    from flask import Response
    return Response(status=200)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)