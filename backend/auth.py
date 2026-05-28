# ============================================
# FILE: auth.py
# PURPOSE: Login, Password Hashing, JWT Tokens
# ============================================

import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from config import config

def hash_password(password):
    """
    Password को hash करो (secure)
    
    USAGE:
        hashed = hash_password("mypassword123")
    """
    try:
        salt = bcrypt.gensalt(rounds=config.BCRYPT_LOG_ROUNDS)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"❌ Password hash error: {e}")
        return None

def verify_password(password, hashed_password):
    """
    Password को verify करो (login के लिए)
    
    USAGE:
        is_correct = verify_password("mypassword123", hashed_pw)
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"❌ Password verify error: {e}")
        return False

def generate_jwt_token(user_id, username, role):
    """
    JWT token generate करो (login के बाद)
    
    USAGE:
        token = generate_jwt_token(1, "admin", "admin")
    """
    try:
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=config.JWT_EXPIRATION_HOURS)
        }
        
        token = jwt.encode(
            payload,
            config.JWT_SECRET_KEY,
            algorithm=config.JWT_ALGORITHM
        )
        
        return token
    except Exception as e:
        print(f"❌ JWT generation error: {e}")
        return None

def verify_jwt_token(token):
    """
    JWT token को verify करो (requests के लिए)
    
    USAGE:
        payload = verify_jwt_token(token)
    """
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        print("❌ Token expired")
        return None
    except jwt.InvalidTokenError:
        print("❌ Invalid token")
        return None
    except Exception as e:
        print(f"❌ Token verification error: {e}")
        return None

def require_login(f):
    """
    Decorator - सिर्फ logged-in users access कर सकें
    
    USAGE:
        @app.route('/dashboard')
        @require_login
        def dashboard():
            return "Secret data"
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Token header से लो
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token missing'}), 401
        
        # Token verify करो
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'message': 'Invalid or expired token'}), 401
        
        # User info context में store करो
        request.user_id = payload['user_id']
        request.username = payload['username']
        request.role = payload['role']
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(required_role):
    """
    Decorator - सिर्फ specific role के users access कर सकें
    
    USAGE:
        @app.route('/admin')
        @require_role('admin')
        def admin_panel():
            return "Admin only"
    """
    from functools import wraps
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # पहले login check करो
            token = None
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(" ")[1]
                except IndexError:
                    return jsonify({'message': 'Invalid token format'}), 401
            
            if not token:
                return jsonify({'message': 'Token missing'}), 401
            
            payload = verify_jwt_token(token)
            if not payload:
                return jsonify({'message': 'Invalid or expired token'}), 401
            
            # Role check करो
            if payload['role'] != required_role and payload['role'] != 'boss':
                return jsonify({'message': f'Only {required_role} can access'}), 403
            
            request.user_id = payload['user_id']
            request.username = payload['username']
            request.role = payload['role']
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator