from flask_restx import Namespace, Resource, fields
from flask import request
from ..services.user_service import UserService
from ..utils.security import generate_tokens
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.middlewares.extensions import limiter
import logging

logger = logging.getLogger(__name__)

auth_ns = Namespace('auth', description='Authentication operations')

# Input models
login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='Username', example='user1'),
    'password': fields.String(required=True, description='Password', example='pass123')
})

register_model = auth_ns.model('Register', {
    'username': fields.String(required=True, description='Username', example='user1'),
    'password': fields.String(required=True, description='Password', example='pass123'),
    'role': fields.String(description='User role', example='user', default='user')
})

# Output model
token_model = auth_ns.model('Token', {
    'access_token': fields.String(description='Access token'),
    'refresh_token': fields.String(description='Refresh token', allow_null=True)
})

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    @limiter.limit('200/day;50/hour;10/minutes')
    @auth_ns.marshal_with(token_model, code=201)
    @auth_ns.doc(responses={201: 'User created', 400: 'Username exists', 429: 'Too many requests'})
    def post(self):
        """Register a new user and return JWT tokens."""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            role = data.get('role', 'user')
            if not username or not password:
                auth_ns.abort(400, message="Username and password are required")
            user = UserService.create_user(username, password, role)
            access_token, refresh_token = generate_tokens(user)
            return {'access_token': access_token, 'refresh_token': refresh_token}, 201
        except ValueError as e:
            logger.error(f"Registration error: {str(e)}")
            auth_ns.abort(400, message=str(e))
        except Exception as e:
            logger.error(f"Unexpected error in Register: {str(e)}", exc_info=True)
            auth_ns.abort(500, message=f"Internal server error: {str(e)}")

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @limiter.limit('200/day;50/hour;10/minutes')
    @auth_ns.marshal_with(token_model)
    @auth_ns.doc(responses={
        200: 'Success',
        400: 'Bad Request',
        401: 'Invalid credentials',
        429: 'Too many login attempts'
    })
    def post(self):
        """Authenticate user and return JWT tokens."""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            if not username or not password:
                auth_ns.abort(400, message="Username and password are required")
            user = UserService.authenticate(username, password)
            if not user:
                auth_ns.abort(401, message="Invalid credentials")
            access_token, refresh_token = generate_tokens(user)
            return {'access_token': access_token, 'refresh_token': refresh_token}, 200
        except ValueError as e:
            logger.error(f"Login error: {str(e)}")
            auth_ns.abort(429, message=str(e))
        except Exception as e:
            logger.error(f"Unexpected error in Login: {str(e)}", exc_info=True)
            auth_ns.abort(500, message=f"Internal server error: {str(e)}")


            
@auth_ns.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    @auth_ns.marshal_with(token_model)
    @limiter.limit('200/day;50/hour;10/minutes')
    @auth_ns.doc(security='Bearer', responses={200: 'Success', 401: 'Invalid refresh token', 429: 'Too many requests'})
    def post(self):
        """Generate a new access token using a refresh token."""
        try:
            username = get_jwt_identity()
            if not username:
                auth_ns.abort(401, message="Invalid refresh token")
            user = UserService.get_user_by_username(username)
            if not user:
                auth_ns.abort(401, message="User not found")
            access_token = create_access_token(
                identity=username,
                additional_claims={'role': user.role}
            )
            return {'access_token': access_token, 'refresh_token': None}, 200
        except Exception as e:
            logger.error(f"Error in Refresh: {str(e)}", exc_info=True)
            auth_ns.abort(500, message=f"Internal server error: {str(e)}")