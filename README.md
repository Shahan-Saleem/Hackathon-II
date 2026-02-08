# Hackathon II - Secure Authentication System

A Flask-based web application featuring secure authentication with multiple OAuth providers (Google, Facebook, GitHub) and traditional email/password login.

## 🚀 Features

- **Multi-provider Authentication**: Support for Google, Facebook, and GitHub OAuth
- **Traditional Login**: Email/password authentication option
- **Secure Session Management**: Proper session handling with CSRF protection
- **Responsive UI**: Modern, mobile-friendly login interface
- **JWT Token Support**: Secure token-based authentication
- **Production Ready**: Includes Docker configuration for easy deployment

## 🛠️ Tech Stack

- **Backend**: Flask (Python 3.8+)
- **Authentication**: Google OAuth 2.0, Facebook OAuth, GitHub OAuth
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (with SQLAlchemy ORM)
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Git
- Docker (optional, for containerized deployment)

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Shahan-Saleem/Hackathon-II.git
cd Hackathon-II
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root with the following variables:

```env
SECRET_KEY=your_secret_key_here
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FACEBOOK_CLIENT_ID=your_facebook_client_id
FACEBOOK_CLIENT_SECRET=your_facebook_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

### 5. OAuth Provider Setup

#### Google OAuth Configuration:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client IDs
5. Set authorized redirect URI to: `http://127.0.0.1:5000/auth/google/callback`
6. Copy Client ID and Secret to your `.env` file

#### Facebook OAuth Configuration:
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Facebook Login product
4. Set valid OAuth redirect URIs to: `http://127.0.0.1:5000/auth/facebook/callback`
5. Copy App ID and Secret to your `.env` file

#### GitHub OAuth Configuration:
1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Create a new OAuth App
3. Set Authorization callback URL to: `http://127.0.0.1:5000/auth/github/callback`
4. Copy Client ID and Secret to your `.env` file

## 🏃‍♂️ Running the Application

### Development Mode

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

### Using Docker

Build and run with Docker Compose:

```bash
docker-compose up --build
```

The application will be available at `http://localhost:5000`

## 🧪 Testing the Application

1. Visit `http://127.0.0.1:5000`
2. Choose to sign in with Google, Facebook, or GitHub
3. Or use the traditional email/password form
4. After successful authentication, you'll be redirected to the dashboard

## 📁 Project Structure

```
Hackathon-II/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── templates/            # HTML templates
│   └── login.html
├── static/               # Static assets
│   ├── css/
│   │   └── login.css
│   └── js/
│       └── login.js
├── backend/              # Backend modules
│   ├── models.py
│   ├── storage.py
│   └── token_manager.py
└── README.md
```

## 🔐 Security Features

- **CSRF Protection**: State parameter validation for OAuth flows
- **Token Validation**: Verification of OAuth tokens with provider APIs
- **Audience Validation**: Ensuring tokens are issued for this application
- **HTTPS Enforcement**: Configured for secure connections in production
- **Session Management**: Secure session handling with proper cleanup
- **Input Validation**: Sanitization of user inputs and OAuth responses

## 🚀 Deployment

For production deployment:

1. Set `SECRET_KEY` to a strong, random value
2. Use HTTPS in production
3. Configure proper database (PostgreSQL recommended)
4. Set up proper logging and monitoring
5. Implement rate limiting for authentication endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the existing issues
2. Create a new issue with detailed information
3. Include your environment details and steps to reproduce

---

Made with ❤️ for Hackathon II