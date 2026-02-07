document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const signUpButton = document.getElementById('signUp');
    const signInButton = document.getElementById('signIn');
    const container = document.querySelector('.container');

    // Form elements
    const signInForm = document.getElementById('signInForm');
    const signUpForm = document.getElementById('signUpForm');

    // Password toggle elements
    const signInToggle = document.getElementById('signInToggle');
    const signUpToggle = document.getElementById('signUpToggle');
    const signUpConfirmToggle = document.getElementById('signUpConfirmToggle');

    // Social login buttons (these should redirect, not fetch)
    const googleSignIn = document.getElementById('googleSignIn');
    const facebookSignIn = document.getElementById('facebookSignIn');
    const githubSignIn = document.getElementById('githubSignIn');
    const googleSignUp = document.getElementById('googleSignUp');
    const facebookSignUp = document.getElementById('facebookSignUp');
    const githubSignUp = document.getElementById('githubSignUp');

    // Forgot password link
    const forgotPasswordLink = document.getElementById('forgotPassword');

    // Event Listeners
    signUpButton.addEventListener('click', () => {
        container.classList.add('right-panel-active');
    });

    signInButton.addEventListener('click', () => {
        container.classList.remove('right-panel-active');
    });

    // Password visibility toggles
    signInToggle.addEventListener('click', togglePasswordVisibility);
    signUpToggle.addEventListener('click', togglePasswordVisibility);
    signUpConfirmToggle.addEventListener('click', togglePasswordVisibility);

    // Form submissions
    signInForm.addEventListener('submit', handleSignIn);
    signUpForm.addEventListener('submit', handleSignUp);

    // SOCIAL LOGIN BUTTONS - REDIRECTS, NOT FETCH CALLS
    // Sign in social buttons
    googleSignIn.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = '/login/google';
    });

    facebookSignIn.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = '/login/facebook';
    });

    githubSignIn.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = '/login/github';
    });

    // Sign up social buttons (same as sign in for OAuth)
    googleSignUp.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = '/login/google';
    });

    facebookSignUp.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = '/login/facebook';
    });

    githubSignUp.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = '/login/github';
    });

    // Check for OAuth success message on page load
    const urlParams = new URLSearchParams(window.location.search);
    const errorParam = urlParams.get('error');
    if (errorParam) {
        showMessage(decodeURIComponent(errorParam), 'error');
        // Remove the error parameter from URL without reloading
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    // Forgot password
    forgotPasswordLink.addEventListener('click', handleForgotPassword);

    // Helper Functions
    function togglePasswordVisibility(e) {
        const icon = e.target.classList.contains('fa-eye') ?
                     e.target : e.target.querySelector('.fa-eye');
        const input = e.target.closest('.password-container').querySelector('input');

        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.replace('fa-eye', 'fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.replace('fa-eye-slash', 'fa-eye');
        }
    }

    async function handleSignIn(e) {
        e.preventDefault();

        const username = document.getElementById('signInUsername').value;
        const password = document.getElementById('signInPassword').value;

        // Show loading state
        const submitBtn = signInForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Signing In...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/auth/signin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (data.success) {
                showMessage(data.message || 'Login successful', 'success');

                // Redirect to dashboard after successful login
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1500);
            } else {
                showMessage(data.error || data.message || 'Sign in failed', 'error');
            }
        } catch (error) {
            showMessage('Network error. Please try again.', 'error');
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }

    async function handleSignUp(e) {
        e.preventDefault();

        const username = document.getElementById('signUpUsername').value;
        const email = document.getElementById('signUpEmail').value;
        const password = document.getElementById('signUpPassword').value;
        const confirmPassword = document.getElementById('signUpConfirmPassword').value;

        // Validate passwords match
        if (password !== confirmPassword) {
            showMessage('Passwords do not match', 'error');
            return;
        }

        // Show loading state
        const submitBtn = signUpForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Creating Account...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username,
                    email,
                    password,
                    confirm_password: confirmPassword
                })
            });

            const data = await response.json();

            if (data.success) {
                showMessage(data.message || 'Registration successful', 'success');

                // Clear form and switch to sign in after successful registration
                setTimeout(() => {
                    signUpForm.reset();
                    container.classList.remove('right-panel-active');
                    // Optionally redirect to dashboard
                    // window.location.href = '/dashboard';
                }, 2000);
            } else {
                showMessage(data.error || data.message || 'Sign up failed', 'error');
            }
        } catch (error) {
            showMessage('Network error. Please try again.', 'error');
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }

    function handleForgotPassword(e) {
        e.preventDefault();
        showMessage('Password reset instructions sent to your email!', 'info');
    }

    function showMessage(message, type) {
        const messageContainer = document.getElementById('messageContainer');
        const messageContent = document.getElementById('messageContent');

        // Remove existing classes
        messageContent.className = 'message-content';

        // Add appropriate class based on type
        switch(type) {
            case 'success':
                messageContent.classList.add('message-success');
                break;
            case 'error':
                messageContent.classList.add('message-error');
                break;
            case 'info':
                messageContent.classList.add('message-info');
                break;
            default:
                messageContent.classList.add('message-info');
        }

        messageContent.textContent = message;
        messageContainer.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            messageContainer.style.display = 'none';
        }, 5000);
    }

    // Initialize password icons to eye (closed)
    document.querySelectorAll('.password-toggle .fa-eye-slash').forEach(icon => {
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    });
});