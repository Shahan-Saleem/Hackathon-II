"""
JWT Token Management for Secure Authentication
Handles creating, validating, and managing JWT tokens for authenticated users
"""
import jwt
import datetime
from typing import Dict, Optional
from flask import current_app


class TokenManager:
    """
    Manages JWT tokens for secure authentication
    """

    @staticmethod
    def create_access_token(user_data: Dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
        """
        Create an access token for the user

        Args:
            user_data: Dictionary containing user information to encode in token
            expires_delta: Optional timedelta for token expiration (defaults to 1 hour)

        Returns:
            Encoded JWT token as string
        """
        if expires_delta is None:
            expires_delta = datetime.timedelta(hours=1)

        payload = {
            'user_data': user_data,
            'exp': datetime.datetime.utcnow() + expires_delta,
            'iat': datetime.datetime.utcnow()
        }

        secret_key = current_app.config.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
        return jwt.encode(payload, secret_key, algorithm='HS256')

    @staticmethod
    def create_refresh_token(user_data: Dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
        """
        Create a refresh token for the user

        Args:
            user_data: Dictionary containing user information to encode in token
            expires_delta: Optional timedelta for token expiration (defaults to 30 days)

        Returns:
            Encoded JWT token as string
        """
        if expires_delta is None:
            expires_delta = datetime.timedelta(days=30)

        payload = {
            'user_data': user_data,
            'exp': datetime.datetime.utcnow() + expires_delta,
            'iat': datetime.datetime.utcnow(),
            'type': 'refresh'
        }

        secret_key = current_app.config.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
        return jwt.encode(payload, secret_key, algorithm='HS256')

    @staticmethod
    def decode_token(token: str) -> Optional[Dict]:
        """
        Decode and validate a JWT token

        Args:
            token: JWT token string to decode

        Returns:
            Decoded token payload if valid, None if invalid
        """
        try:
            secret_key = current_app.config.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            print("Token expired")
            return None
        except jwt.InvalidTokenError:
            print("Invalid token")
            return None

    @staticmethod
    def verify_access_token(token: str) -> Optional[Dict]:
        """
        Verify an access token and return user data if valid

        Args:
            token: Access token to verify

        Returns:
            User data from token if valid, None if invalid
        """
        decoded = TokenManager.decode_token(token)
        if decoded and 'user_data' in decoded:
            return decoded['user_data']
        return None