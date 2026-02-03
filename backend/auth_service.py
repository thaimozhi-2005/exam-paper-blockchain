"""
Authentication Service - User registration and login
"""

import json
import os
import hashlib
import secrets

class AuthService:
    def __init__(self, users_file='config/users.json'):
        """Initialize authentication service"""
        self.users_file = users_file
        self.sessions = {}  # In-memory session storage
        
        # Create users file if it doesn't exist
        if not os.path.exists(self.users_file):
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            self._create_default_users()
    
    def _create_default_users(self):
        """Create default admin and principal users"""
        default_users = {
            "ADMIN001": {
                "register_no": "ADMIN001",
                "email": "admin@university.edu",
                "password": self._hash_password("admin123"),
                "role": "admin",
                "name": "University Admin"
            },
            "PRIN001": {
                "register_no": "PRIN001",
                "email": "principal@college.edu",
                "password": self._hash_password("principal123"),
                "role": "principal",
                "name": "College Principal",
                "college_id": "COL001"
            }
        }
        
        with open(self.users_file, 'w') as f:
            json.dump(default_users, f, indent=2)
        
        print(f"✅ Created default users file at {self.users_file}")
    
    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_users(self):
        """Load users from file"""
        with open(self.users_file, 'r') as f:
            return json.load(f)
    
    def _save_users(self, users):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def register(self, register_no, email, password, role, name, college_id=None):
        """
        Register a new user
        Returns: (success, message)
        """
        users = self._load_users()
        
        # Check if user already exists
        if register_no in users:
            return False, "User already exists"
        
        # Validate role
        if role not in ['admin', 'principal']:
            return False, "Invalid role"
        
        # Create user
        users[register_no] = {
            "register_no": register_no,
            "email": email,
            "password": self._hash_password(password),
            "role": role,
            "name": name
        }
        
        if role == 'principal' and college_id:
            users[register_no]['college_id'] = college_id
        
        self._save_users(users)
        
        return True, "User registered successfully"
    
    def login(self, register_no, password):
        """
        Authenticate user
        Returns: (success, user_data or error_message, session_token)
        """
        users = self._load_users()
        
        # Check if user exists
        if register_no not in users:
            return False, "Invalid credentials", None
        
        user = users[register_no]
        
        # Verify password
        if user['password'] != self._hash_password(password):
            return False, "Invalid credentials", None
        
        # Generate session token
        session_token = secrets.token_hex(32)
        
        # Store session
        self.sessions[session_token] = {
            'register_no': register_no,
            'role': user['role'],
            'email': user['email'],
            'name': user['name']
        }
        
        if 'college_id' in user:
            self.sessions[session_token]['college_id'] = user['college_id']
        
        return True, user, session_token
    
    def verify_session(self, session_token):
        """
        Verify session token
        Returns: (valid, user_data or None)
        """
        if session_token in self.sessions:
            return True, self.sessions[session_token]
        return False, None
    
    def logout(self, session_token):
        """Logout user by removing session"""
        if session_token in self.sessions:
            del self.sessions[session_token]
            return True
        return False
    
    def get_user(self, register_no):
        """Get user data by register number"""
        users = self._load_users()
        return users.get(register_no)
