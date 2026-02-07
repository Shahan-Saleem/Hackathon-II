/**
 * Google OAuth Integration - Frontend JavaScript
 * Handles client-side integration with the OAuth flow
 */

class GoogleAuthHandler {
    constructor() {
        this.accessToken = null;
        this.refreshToken = null;
        this.tokenExpiry = null;
    }

    /**
     * Initialize the Google OAuth flow by redirecting to the backend endpoint
     */
    initiateGoogleLogin() {
        // Redirect to backend to handle OAuth flow
        window.location.href = '/login/google';
    }

    /**
     * Check if user is currently authenticated
     */
    isAuthenticated() {
        // Check if we have an access token that hasn't expired
        if (!this.accessToken || !this.tokenExpiry) {
            return false;
        }

        const now = new Date();
        return now < this.tokenExpiry;
    }

    /**
     * Get user info from the backend API
     */
    async getCurrentUser() {
        try {
            const response = await fetch('/api/auth/me', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                return data.user;
            } else {
                throw new Error('Failed to get user info');
            }
        } catch (error) {
            console.error('Error getting user info:', error);
            return null;
        }
    }

    /**
     * Get JWT token from backend after successful OAuth
     */
    async getAuthToken() {
        try {
            const response = await fetch('/api/auth/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include' // Include session cookies
            });

            if (response.ok) {
                const data = await response.json();

                this.accessToken = data.access_token;
                if (data.refresh_token) {
                    this.refreshToken = data.refresh_token;
                }

                // Calculate expiry time (usually 1 hour from now)
                this.tokenExpiry = new Date(Date.now() + data.expires_in * 1000);

                return {
                    success: true,
                    accessToken: this.accessToken,
                    refreshToken: this.refreshToken
                };
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to get auth token');
            }
        } catch (error) {
            console.error('Error getting auth token:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Refresh the access token using the refresh token
     */
    async refreshAccessToken() {
        if (!this.refreshToken) {
            throw new Error('No refresh token available');
        }

        try {
            const response = await fetch('/api/auth/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    refresh_token: this.refreshToken
                })
            });

            if (response.ok) {
                const data = await response.json();

                this.accessToken = data.access_token;
                this.tokenExpiry = new Date(Date.now() + data.expires_in * 1000);

                return {
                    success: true,
                    accessToken: this.accessToken
                };
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to refresh token');
            }
        } catch (error) {
            console.error('Error refreshing token:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Logout the user
     */
    async logout() {
        try {
            await fetch('/api/auth/signout', {
                method: 'POST',
                credentials: 'include' // Include session cookies
            });

            // Clear local tokens
            this.accessToken = null;
            this.refreshToken = null;
            this.tokenExpiry = null;

            // Redirect to login
            window.location.href = '/login';
        } catch (error) {
            console.error('Error during logout:', error);
            // Still clear local tokens even if backend call fails
            this.accessToken = null;
            this.refreshToken = null;
            this.tokenExpiry = null;
            window.location.href = '/login';
        }
    }

    /**
     * Make authenticated API request
     */
    async makeAuthenticatedRequest(url, options = {}) {
        // Check if token needs refresh
        if (this.isAuthenticated()) {
            // Token is still valid, use it
            options.headers = {
                ...options.headers,
                'Authorization': `Bearer ${this.accessToken}`
            };
        } else if (this.refreshToken) {
            // Token expired, try to refresh
            const refreshResult = await this.refreshAccessToken();
            if (!refreshResult.success) {
                // Refresh failed, redirect to login
                this.logout();
                return null;
            }

            // Use new token
            options.headers = {
                ...options.headers,
                'Authorization': `Bearer ${this.accessToken}`
            };
        } else {
            // No way to authenticate, redirect to login
            window.location.href = '/login';
            return null;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            return response;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
}

// Initialize the Google Auth Handler
const googleAuth = new GoogleAuthHandler();

// Example usage:
document.addEventListener('DOMContentLoaded', function() {
    // Google sign-in button
    const googleSignInBtn = document.getElementById('googleSignIn');

    if (googleSignInBtn) {
        googleSignInBtn.addEventListener('click', function(e) {
            e.preventDefault();
            googleAuth.initiateGoogleLogin();
        });
    }

    // Check authentication status on page load
    googleAuth.getAuthToken().then(result => {
        if (result.success) {
            console.log('User is authenticated');
            // Update UI to show logged-in state
            updateUIForLoggedIn();
        } else {
            console.log('User is not authenticated');
            // Keep login UI
        }
    });
});

function updateUIForLoggedIn() {
    // Example: Update UI elements to reflect logged-in state
    const loginElements = document.querySelectorAll('.login-required');
    const logoutElements = document.querySelectorAll('.logout-required');

    loginElements.forEach(el => el.style.display = 'none');
    logoutElements.forEach(el => el.style.display = 'block');
}

// Export for use in other modules if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GoogleAuthHandler;
}