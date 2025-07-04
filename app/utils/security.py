from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, get_jwt_identity
from functools import wraps
from flask_restx import abort
import logging

logger = logging.getLogger(__name__)

def generate_tokens(user):
    access_token = create_access_token(
        identity=user.username,
        additional_claims={'role': user.role}
    )
    refresh_token = create_refresh_token(identity=user.username)
    return access_token, refresh_token

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            claims = get_jwt()

            logger.info(f"JWT Claims: {get_jwt()}")
            logger.info(f"JWT Identity: {get_jwt_identity()}")
            user_role = claims.get('role')
            if user_role != role:
                abort(403, message=f"Role '{role}' required")
            return f(*args, **kwargs)
        return decorated_function
    return decorator
