"""
JWT Authentication utilities
"""
import jwt
from functools import wraps
from flask import request, jsonify
import os
from dotenv import load_dotenv
from constants import ERROR_TOKEN_NOT_PROVIDED, ERROR_INVALID_TOKEN

# Load environment variables
load_dotenv()

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is not set")

def verify_token(token):
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_request():
    """
    Extract JWT token from request headers
    
    Returns:
        str: JWT token or None if not found
    """
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None


def get_account_id_from_token():
    """
    Get account ID from JWT token in request
    
    Returns:
        int: Account ID or None if token is invalid/missing
    """
    token = get_token_from_request()
    if not token:
        return None
    
    payload = verify_token(token)
    if payload:
        return int(payload.get('sub'))
    return None


def require_auth(f):
    """
    Decorator to require JWT authentication for routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            return jsonify({'error': ERROR_TOKEN_NOT_PROVIDED}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': ERROR_INVALID_TOKEN}), 401
        
        # Add account_id to kwargs for the route function
        kwargs['account_id'] = int(payload.get('sub'))
        return f(*args, **kwargs)
    
    return decorated_function
