# Project-Based Task Management Web Application - OAuth Implementation

## Overview
Complete authentication system with email/password login and OAuth 2.0 support for Google, Facebook, and GitHub.

## Features
- ✅ Email/password authentication
- ✅ Google OAuth 2.0 integration
- ✅ Facebook OAuth 2.0 integration
- ✅ GitHub OAuth 2.0 integration
- ✅ Modern flip-card UI design (preserved)
- ✅ Responsive design
- ✅ Secure session management

## Tech Stack
- Backend: Python Flask
- Frontend: HTML, CSS, Vanilla JavaScript
- Authentication: OAuth 2.0 (Google, Facebook, GitHub)

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

## OAuth Setup

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable "Google+ API" (or newer People API)
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Set Application Type to "Web Application"
6. Add redirect URI: `http://127.0.0.1:5000/auth/google/callback`
7. Download credentials and note your:
   - Client ID
   - Client Secret

### Facebook OAuth Setup
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Go to "Settings" → "Basic"
4. Note your:
   - App ID
   - App Secret
5. Go to "Products" → "+ Add Product" → "Facebook Login"
6. Add redirect URI: `http://127.0.0.1:5000/auth/facebook/callback`

### GitHub OAuth Setup
1. Go to GitHub → Settings → Developer settings
2. Click "OAuth Apps" → "New OAuth App"
3. Set:
   - Application name: Your app name
   - Homepage URL: `http://127.0.0.1:5000`
   - Authorization callback URL: `http://127.0.0.1:5000/auth/github/callback`
4. Note your:
   - Client ID
   - Client Secret

## Environment Variables

Create a `.env` file or set environment variables:

```bash
export GOOGLE_CLIENT_ID=your_google_client_id
export GOOGLE_CLIENT_SECRET=your_google_client_secret
export FACEBOOK_CLIENT_ID=your_facebook_client_id
export FACEBOOK_CLIENT_SECRET=your_facebook_client_secret
export GITHUB_CLIENT_ID=your_github_client_id
export GITHUB_CLIENT_SECRET=your_github_client_secret
export SECRET_KEY=your_secret_key
```

## Running the Application

```bash
python app.py
```

Visit: `http://127.0.0.1:5000`

## How OAuth Works

1. User clicks "Sign in with [Provider]" button
2. Browser redirects to OAuth provider (Google/Facebook/GitHub)
3. User authenticates with provider
4. Provider redirects back to our callback URL with authorization code
5. Our server exchanges code for access token
6. Our server retrieves user info from provider
7. User is logged in and redirected to dashboard

## OAuth Routes

- `/login/google` → Initiates Google OAuth
- `/auth/google/callback` → Handles Google OAuth callback
- `/login/facebook` → Initiates Facebook OAuth
- `/auth/facebook/callback` → Handles Facebook OAuth callback
- `/login/github` → Initiates GitHub OAuth
- `/auth/github/callback` → Handles GitHub OAuth callback

## Security Features

- State parameter validation for CSRF protection
- Secure session management
- OAuth tokens exchanged server-side (not client-side)
- Proper error handling

## Troubleshooting

### Common Issues:
1. **OAuth not configured**: Set environment variables
2. **Redirect URI mismatch**: Ensure exact match in provider settings
3. **Network errors**: Check if OAuth URLs are accessible

### Debug Steps:
1. Verify environment variables are set
2. Check redirect URIs match provider settings exactly
3. Ensure OAuth providers are enabled in cloud consoles
4. Look at server logs for specific error messages

## Test Checklist

- [ ] Email/password login works
- [ ] Google login opens Gmail consent screen
- [ ] Facebook login redirects correctly
- [ ] GitHub login works
- [ ] OAuth callbacks work properly
- [ ] User session is maintained after login
- [ ] Dashboard shows correct user info
- [ ] Logout works correctly
- [ ] No network errors in browser console
- [ ] UI design remains unchanged

## File Structure
```
app.py                 # Flask app with OAuth implementation
templates/login.html  # Login page template
static/login.html     # Static login page
static/css/login.css  # Styles (unchanged)
static/js/login.js    # Fixed OAuth redirects
requirements.txt      # Dependencies
README.md            # This file
```

## Production Notes

For production deployment:
1. Use HTTPS (required for OAuth)
2. Set secure secret key
3. Configure proper session storage
4. Set up OAuth providers with production URLs
5. Add proper error logging