// Login Page JavaScript

const API_BASE_URL = 'http://localhost:5000/api';
let selectedRole = 'admin';

function selectRole(role) {
    selectedRole = role;
    document.getElementById('role').value = role;

    // Update button styles
    const buttons = document.querySelectorAll('.role-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
}

async function handleLogin(event) {
    event.preventDefault();

    const formData = {
        register_no: document.getElementById('register_no').value,
        password: document.getElementById('password').value
    };

    const messageDiv = document.getElementById('message');
    messageDiv.textContent = 'Logging in...';
    messageDiv.className = 'message';
    messageDiv.style.display = 'block';

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            // Store session token
            localStorage.setItem('session_token', data.session_token);
            localStorage.setItem('user_name', data.user.name);
            localStorage.setItem('user_role', data.user.role);
            localStorage.setItem('user_email', data.user.email);

            messageDiv.textContent = 'Login successful! Redirecting...';
            messageDiv.className = 'message success';

            // Redirect based on role
            setTimeout(() => {
                if (data.user.role === 'admin') {
                    window.location.href = 'set.html';
                } else {
                    window.location.href = 'get.html';
                }
            }, 1000);
        } else {
            messageDiv.textContent = data.error || 'Login failed';
            messageDiv.className = 'message error';
        }
    } catch (error) {
        messageDiv.textContent = 'Error connecting to server. Make sure the backend is running.';
        messageDiv.className = 'message error';
        console.error('Login error:', error);
    }
}

// Check if already logged in
window.addEventListener('DOMContentLoaded', () => {
    const sessionToken = localStorage.getItem('session_token');
    const userRole = localStorage.getItem('user_role');

    if (sessionToken && userRole) {
        // Redirect to appropriate page
        if (userRole === 'admin') {
            window.location.href = 'set.html';
        } else {
            window.location.href = 'get.html';
        }
    }
});
