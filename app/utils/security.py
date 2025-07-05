from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, get_jwt_identity
from functools import wraps
from flask_restx import abort
import logging

logger = logging.getLogger(__name__)

def generate_tokens(user):
    """
    Generate JWT access and refresh tokens for a user.
    
    Args:
        user: User object with username and role attributes.
    
    Returns:
        Tuple of (access_token, refresh_token).
    
    Raises:
        ValueError: If user is None or missing required attributes.
    """
    if not user or not hasattr(user, 'username') or not hasattr(user, 'role'):
        logger.error("Invalid user object provided to generate_tokens")
        raise ValueError("User object must have username and role attributes")
    
    try:
        access_token = create_access_token(
            identity=user.username,
            additional_claims={'role': user.role}
        )
        refresh_token = create_refresh_token(identity=user.username)
        logger.info(f"Generated tokens for user: {user.username}")
        return access_token, refresh_token
    except Exception as e:
        logger.error(f"Error generating tokens for user {user.username}: {str(e)}")
        raise

def role_required(role):
    """
    Decorator to enforce role-based access control for a specific role.
    
    Args:
        role (str): The required role for accessing the endpoint.
    
    Returns:
        Decorator function that checks JWT role.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                claims = get_jwt()
                user_role = claims.get('role')
                user_identity = get_jwt_identity()
                
                logger.info(f"Checking role for user: {user_identity}, required role: {role}, user role: {user_role}")
                
                if not user_role:
                    logger.warning(f"No role found in JWT for user: {user_identity}")
                    abort(403, message="Role information missing in token")
                
                if user_role != role:
                    logger.warning(f"Access denied for user {user_identity}: required role {role}, found {user_role}")
                    abort(403, message=f"Role '{role}' required")
                
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in role_required decorator: {str(e)}")
                abort(401, message="Invalid or missing JWT")
        return decorated_function
    return decorator