// LOGIN.html — Access Control & Role Selection
const API_BASE_URL = `http://${window.location.hostname}:5000/api`;
let selectedRole = 'admin';

function selectRole(role, btn) {
    selectedRole = role;
    document.getElementById('role').value = role;

    // Update button styles
    const buttons = document.querySelectorAll('.role-toggle-btn');
    buttons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
}

async function handleLogin(event) {
    event.preventDefault();

    const formData = {
        register_no: document.getElementById('register_no').value,
        password: document.getElementById('password').value
    };

    const loginBtn = document.getElementById('loginBtn');
    const messageDiv = document.getElementById('message');

    // Show loading state
    loginBtn.classList.add('loading');
    loginBtn.disabled = true;
    messageDiv.className = 'message-toast';
    messageDiv.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        // Reset loading state
        loginBtn.classList.remove('loading');
        loginBtn.disabled = false;



        if (data.success) {
            // Store session token
            localStorage.setItem('session_token', data.session_token);
            localStorage.setItem('user_name', data.user.name);
            localStorage.setItem('user_role', data.user.role);
            localStorage.setItem('user_email', data.user.email);

            messageDiv.textContent = '✅ Login successful! Redirecting...';
            messageDiv.className = 'message-toast success';

            // Redirect based on role
            setTimeout(() => {
                if (data.user.role === 'admin') {
                    window.location.href = 'set.html';
                } else {
                    window.location.href = 'get.html';
                }
            }, 1000);
        } else {
            messageDiv.textContent = data.error || 'Login failed. Please check your credentials.';
            messageDiv.className = 'message-toast error';
        }
    } catch (error) {
        loginBtn.classList.remove('loading');
        loginBtn.disabled = false;
        messageDiv.textContent = 'Error connecting to server. Make sure the backend is running.';
        messageDiv.className = 'message-toast error';
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
