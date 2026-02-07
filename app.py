from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import os
import requests
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# OAuth configuration
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Only for development

# OAuth credentials - set these as environment variables
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID_HERE')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'YOUR_GOOGLE_CLIENT_SECRET_HERE')
FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID', 'YOUR_FACEBOOK_CLIENT_ID_HERE')
FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_CLIENT_SECRET', 'YOUR_FACEBOOK_CLIENT_SECRET_HERE')
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', 'YOUR_GITHUB_CLIENT_ID_HERE')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', 'YOUR_GITHUB_CLIENT_SECRET_HERE')

# Mock user database (replace with real database in production)
users_db = {
    'test@gmail.com': {
        'email': 'test@gmail.com',
        'password': '123456',
        'name': 'Test User'
    }
}

@app.route('/')
def index():
    """Home route - redirect to login"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET'])
def login():
    """Login page route"""
    error = request.args.get('error')
    return render_template('login.html', error=error)

@app.route('/favicon.ico')
def favicon():
    """Empty favicon to prevent 404 errors"""
    from flask import Response
    return Response('', mimetype='image/x-icon')

@app.route('/api/auth/signin', methods=['POST'])
def signin():
    """Handle email/password sign in request"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400

        # Mock authentication - check if user exists and password matches
        if username in users_db and users_db[username]['password'] == password:
            # Store user in session
            session['user_id'] = username
            session['user_email'] = users_db[username]['email']
            session['user_name'] = users_db[username].get('name', username)

            return jsonify({
                'success': True,
                'message': 'Login successful'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred during sign in'
        }), 500

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Handle sign up request"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if not username or not email or not password:
            return jsonify({
                'success': False,
                'message': 'Username, email, and password are required'
            }), 400

        if password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'Passwords do not match'
            }), 400

        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters long'
            }), 400

        if username in users_db:
            return jsonify({
                'success': False,
                'message': 'Username already exists'
            }), 409

        # Store user (in production, hash passwords)
        users_db[username] = {
            'email': email,
            'password': password,  # In production, hash this!
            'name': username
        }

        # Store user in session after registration
        session['user_id'] = username
        session['user_email'] = email
        session['user_name'] = username

        return jsonify({
            'success': True,
            'message': 'Account created successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred during sign up'
        }), 500

@app.route('/login/google')
def google_login():
    """Initiate Google OAuth login"""
    try:
        if not GOOGLE_CLIENT_ID or GOOGLE_CLIENT_ID == 'YOUR_GOOGLE_CLIENT_ID_HERE':
            print("Google OAuth not configured: missing or default CLIENT_ID")
            return jsonify({
                'error': 'Google OAuth not configured. Please set GOOGLE_CLIENT_ID environment variable.'
            }), 500

        # Google OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://127.0.0.1:5000/auth/google/callback"]
                }
            },
            scopes=["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid"]
        )

        flow.redirect_uri = url_for('google_callback', _external=True)

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )

        # Store state in session for security
        session['oauth_state'] = state
        session['oauth_provider'] = 'google'

        print(f"Redirecting to Google OAuth: {authorization_url}")
        return redirect(authorization_url)

    except Exception as e:
        print(f"Error in google_login: {str(e)}")
        # Redirect back to login page with error message
        return redirect(url_for('login', error='Google OAuth setup failed'))

@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Verify state parameter
        if request.args.get('state') != session.get('oauth_state'):
            print("Google OAuth: State mismatch error")
            return redirect(url_for('login', error='Authentication failed: Invalid state'))

        # Get authorization code
        code = request.args.get('code')
        if not code:
            print("Google OAuth: No authorization code received")
            return redirect(url_for('login', error='Authentication failed: No code received'))

        # Exchange code for token
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
            return redirect(url_for('login', error=f'Failed to authenticate: {error_msg}'))

        access_token = token_json['access_token']

        # Get user info
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        user_headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(user_info_url, headers=user_headers)
        user_info = user_response.json()

        if 'email' not in user_info:
            print("Google OAuth: Could not retrieve user email")
            return redirect(url_for('login', error='Could not retrieve user information'))

        # Extract user data
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0])
        user_id = str(user_info.get('id', email))  # Use Google ID or email as user ID

        print(f"Google OAuth successful: {email}")

        # Store user info in session
        session['user_id'] = user_id
        session['user_email'] = email
        session['user_name'] = name
        session['logged_in_with'] = 'google'

        # Add to users_db if not exists
        if user_id not in users_db:
            users_db[user_id] = {
                'email': email,
                'name': name,
                'password': None  # No password for OAuth users
            }

        # Redirect to dashboard or home page
        return redirect(url_for('dashboard'))

    except Exception as e:
        print(f"Google OAuth error: {str(e)}")
        return redirect(url_for('login', error=f'Google authentication failed: {str(e)}'))

@app.route('/login/facebook')
def facebook_login():
    """Initiate Facebook OAuth login"""
    try:
        if not FACEBOOK_CLIENT_ID or FACEBOOK_CLIENT_ID == 'YOUR_FACEBOOK_CLIENT_ID_HERE':
            print("Facebook OAuth not configured: missing or default CLIENT_ID")
            return redirect(url_for('login', error='Facebook OAuth not configured'))

        # Build authorization URL
        params = {
            'client_id': FACEBOOK_CLIENT_ID,
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
        return redirect(url_for('login', error='Facebook OAuth setup failed'))

@app.route('/auth/facebook/callback')
def facebook_callback():
    """Handle Facebook OAuth callback"""
    try:
        # Verify state parameter
        if request.args.get('state') != session.get('oauth_state'):
            print("Facebook OAuth: State mismatch error")
            return redirect(url_for('login', error='Authentication failed: Invalid state'))

        # Get authorization code
        code = request.args.get('code')
        if not code:
            print("Facebook OAuth: No authorization code received")
            return redirect(url_for('login', error='Authentication failed: No code received'))

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
            return redirect(url_for('login', error=f'Failed to authenticate: {error_msg}'))

        access_token = token_json['access_token']

        # Get user info
        user_fields = 'id,name,email'
        user_url = f'https://graph.facebook.com/me?fields={user_fields}&access_token={access_token}'
        user_response = requests.get(user_url)
        user_info = user_response.json()

        if 'id' not in user_info:
            print("Facebook OAuth: Could not retrieve user information")
            return redirect(url_for('login', error='Could not retrieve user information'))

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
        if user_id not in users_db:
            users_db[user_id] = {
                'email': email,
                'name': name,
                'password': None  # No password for OAuth users
            }

        # Redirect to dashboard or home page
        return redirect(url_for('dashboard'))

    except Exception as e:
        print(f"Facebook OAuth error: {str(e)}")
        return redirect(url_for('login', error=f'Facebook authentication failed: {str(e)}'))

@app.route('/login/github')
def github_login():
    """Initiate GitHub OAuth login"""
    try:
        if not GITHUB_CLIENT_ID or GITHUB_CLIENT_ID == 'YOUR_GITHUB_CLIENT_ID_HERE':
            print("GitHub OAuth not configured: missing or default CLIENT_ID")
            return redirect(url_for('login', error='GitHub OAuth not configured'))

        # Build authorization URL
        params = {
            'client_id': GITHUB_CLIENT_ID,
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
        return redirect(url_for('login', error='GitHub OAuth setup failed'))

@app.route('/auth/github/callback')
def github_callback():
    """Handle GitHub OAuth callback"""
    try:
        # Verify state parameter
        if request.args.get('state') != session.get('oauth_state'):
            print("GitHub OAuth: State mismatch error")
            return redirect(url_for('login', error='Authentication failed: Invalid state'))

        # Get authorization code
        code = request.args.get('code')
        if not code:
            print("GitHub OAuth: No authorization code received")
            return redirect(url_for('login', error='Authentication failed: No code received'))

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
            return redirect(url_for('login', error=f'Failed to authenticate: {error_msg}'))

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
            return redirect(url_for('login', error='Could not retrieve user information'))

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
        user_id = f"github_{user_info['id']}"

        print(f"GitHub OAuth successful: {email}")

        # Store user info in session
        session['user_id'] = user_id
        session['user_email'] = email
        session['user_name'] = name
        session['logged_in_with'] = 'github'

        # Add to users_db if not exists
        if user_id not in users_db:
            users_db[user_id] = {
                'email': email,
                'name': name,
                'password': None  # No password for OAuth users
            }

        # Redirect to dashboard or home page
        return redirect(url_for('dashboard'))

    except Exception as e:
        print(f"GitHub OAuth error: {str(e)}")
        return redirect(url_for('login', error=f'GitHub authentication failed: {str(e)}'))

@app.route('/dashboard')
def dashboard():
    """Dashboard page after login"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return f"""
     <html>
    <html>
    <head>
        <title>Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .container {{ max-width: 600px; margin: 0 auto; text-align: center; }}
            .user-info {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .btn {{ background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin: 10px; display: inline-block; }}
            .btn:hover {{ background: #5a6fd8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome, {session.get('user_name', session.get('user_id'))}!</h1>
            <div class="user-info">
                <p><strong>Email:</strong> {session.get('user_email')}</p>
                <p><strong>Logged in with:</strong> {session.get('logged_in_with', 'email/password')}</p>
            </div>
            <a href="/logout" class="btn">Logout</a>
            <a href="/" class="btn">Back to Login</a>
        </div>
    </body>
    </html>
    """

@app.route('/logout')
def logout():
    """Logout route"""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Create required directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)

    print("Starting Flask application...")
    print("Visit http://127.0.0.1:5000 to access the login page")
    print("\nFor Google OAuth, set these environment variables:")
    print("  GOOGLE_CLIENT_ID=your_google_client_id")
    print("  GOOGLE_CLIENT_SECRET=your_google_client_secret")
    print("\nFor Facebook OAuth, set these environment variables:")
    print("  FACEBOOK_CLIENT_ID=your_facebook_client_id")
    print("  FACEBOOK_CLIENT_SECRET=your_facebook_client_secret")
    print("\nFor GitHub OAuth, set these environment variables:")
    print("  GITHUB_CLIENT_ID=your_github_client_id")
    print("  GITHUB_CLIENT_SECRET=your_github_client_secret")

    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)