from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from functools import wraps
from flask_restx import abort
from flask import jsonify

def generate_tokens(user):
    access_token = create_access_token(identity=user.username, additional_claims={'role': user.role})
    refresh_token = create_refresh_token(identity=user.username)
    return access_token, refresh_token

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') != role:
                return jsonify({'message': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
