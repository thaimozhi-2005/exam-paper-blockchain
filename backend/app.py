"""
Flask REST API - Main application
Endpoints for authentication, paper storage, and verification
"""

from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import io

# Import services
from web3_client import Web3Client
from contract_loader import ContractLoader
from auth_service import AuthService
from paper_service import PaperService

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change this!
CORS(app, supports_credentials=True)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize services
try:
    print("🚀 Initializing services...")
    web3_client = Web3Client()
    contract_loader = ContractLoader(web3_client)
    auth_service = AuthService()
    paper_service = PaperService(contract_loader, auth_service)
    print("✅ All services initialized successfully\n")
except Exception as e:
    print(f"❌ Failed to initialize services: {str(e)}")
    print("⚠️  Make sure Ganache is running and contract is deployed!")
    # Continue anyway for testing

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_auth(role=None):
    """Decorator to require authentication"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            session_token = request.headers.get('Authorization')
            if not session_token:
                return jsonify({'success': False, 'error': 'No authorization token'}), 401
            
            valid, user_data = auth_service.verify_session(session_token)
            if not valid:
                return jsonify({'success': False, 'error': 'Invalid session'}), 401
            
            if role and user_data['role'] != role:
                return jsonify({'success': False, 'error': 'Unauthorized role'}), 403
            
            # Pass user_data to the route function
            return f(user_data, *args, **kwargs)
        
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# ============= AUTHENTICATION ENDPOINTS =============

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        success, message = auth_service.register(
            data['register_no'],
            data['email'],
            data['password'],
            data['role'],
            data['name'],
            data.get('college_id')
        )
        
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.json
        success, user_or_error, session_token = auth_service.login(
            data['register_no'],
            data['password']
        )
        
        if success:
            return jsonify({
                'success': True,
                'session_token': session_token,
                'user': {
                    'register_no': user_or_error['register_no'],
                    'email': user_or_error['email'],
                    'role': user_or_error['role'],
                    'name': user_or_error['name']
                }
            })
        else:
            return jsonify({'success': False, 'error': user_or_error}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout"""
    try:
        session_token = request.headers.get('Authorization')
        auth_service.logout(session_token)
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============= ADMIN ENDPOINTS =============

@app.route('/api/admin/store-paper', methods=['POST'])
@require_auth(role='admin')
def store_paper(user_data):
    """Admin endpoint to store exam paper"""
    try:
        # Check if PDF file is present
        if 'pdf_file' not in request.files:
            return jsonify({'success': False, 'error': 'No PDF file provided'}), 400
        
        pdf_file = request.files['pdf_file']
        
        if pdf_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(pdf_file.filename):
            return jsonify({'success': False, 'error': 'Only PDF files allowed'}), 400
        
        # Read PDF data
        pdf_data = pdf_file.read()
        
        # Get form data
        college_id = request.form.get('college_id')
        subject_code = request.form.get('subject_code')
        exam_datetime = request.form.get('exam_datetime')
        principal_email = request.form.get('principal_email')
        
        # Validate inputs
        if not all([college_id, subject_code, exam_datetime, principal_email]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Process paper storage
        success, result = paper_service.admin_store_paper(
            pdf_data,
            college_id,
            subject_code,
            exam_datetime,
            principal_email
        )
        
        if success:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({'success': False, 'error': result}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= PRINCIPAL ENDPOINTS =============

@app.route('/api/principal/verify-paper/<int:paper_id>', methods=['GET'])
@require_auth(role='principal')
def verify_paper(user_data, paper_id):
    """Principal endpoint to fetch paper details for verification"""
    try:
        success, result = paper_service.principal_verify_paper(paper_id)
        
        if success:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({'success': False, 'error': result}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/principal/decrypt-paper', methods=['POST'])
@require_auth(role='principal')
def decrypt_paper(user_data):
    """Principal endpoint to decrypt exam paper"""
    try:
        # Check if encrypted package file is present
        if 'package_file' not in request.files:
            return jsonify({'success': False, 'error': 'No package file provided'}), 400
        
        package_file = request.files['package_file']
        
        if package_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Read package data
        package_content = package_file.read()
        try:
            package_data = json.loads(package_content)
        except (ValueError, UnicodeDecodeError):
            return jsonify({
                'success': False, 
                'error': 'Invalid package file. Please upload the .json encrypted package file, not the PDF.'
            }), 400
        
        # Get paper ID and college ID from form
        paper_id = int(request.form.get('paper_id'))
        college_id = request.form.get('college_id') or user_data.get('college_id')
        
        # Decrypt paper
        success, result = paper_service.principal_decrypt_paper(
            paper_id,
            package_data,
            college_id
        )
        
        if success:
            # Return decrypted PDF as file
            decrypted_pdf = result['decrypted_pdf']
            
            return send_file(
                io.BytesIO(decrypted_pdf),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'exam_paper_{paper_id}.pdf'
            )
        else:
            return jsonify({'success': False, 'error': result}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= GENERAL ENDPOINTS =============

@app.route('/api/paper/<int:paper_id>', methods=['GET'])
def get_paper(paper_id):
    """Get paper metadata (public endpoint)"""
    try:
        success, result = paper_service.principal_verify_paper(paper_id)
        
        if success:
            # Remove sensitive data for public access
            public_data = {
                'paper_id': paper_id,
                'college_id': result['college_id'],
                'subject_code': result['subject_code'],
                'timestamp': result['timestamp'],
                'verified': result['verified'],
                'exam_datetime': result['exam_datetime']
            }
            return jsonify({
                'success': True,
                'data': public_data
            })
        else:
            return jsonify({'success': False, 'error': result}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get blockchain statistics"""
    try:
        total_papers = contract_loader.get_total_papers()
        block_number = web3_client.get_block_number()
        
        return jsonify({
            'success': True,
            'data': {
                'total_papers': total_papers,
                'block_number': block_number,
                'network': 'Ganache Local',
                'chain_id': web3_client.w3.eth.chain_id
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'API is running',
        'blockchain_connected': web3_client.w3.is_connected()
    })

# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ============= MAIN =============

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎓 BLOCKCHAIN EXAM PAPER VERIFICATION SYSTEM")
    print("="*60)
    print("📡 API Server starting...")
    print("🌐 Access at: http://localhost:5000")
    print("📚 API Documentation:")
    print("   POST   /api/register")
    print("   POST   /api/login")
    print("   POST   /api/logout")
    print("   POST   /api/admin/store-paper")
    print("   GET    /api/principal/verify-paper/<paper_id>")
    print("   POST   /api/principal/decrypt-paper")
    print("   GET    /api/paper/<paper_id>")
    print("   GET    /api/stats")
    print("   GET    /api/health")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
