from flask_restx import Namespace, Resource, fields
from flask import request, jsonify, make_response
from ..services.user_service import UserService
from ..utils.security import generate_tokens
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from app.middlewares.extensions import limiter
import logging

logger = logging.getLogger(__name__)

auth_ns = Namespace('auth', description='Authentication operations')

login_model = auth_ns.model('Login', {
    'identifier': fields.String(required=True, example='user1 or user1@example.com'),
    'password': fields.String(required=True, example='Pass123!')
})

register_model = auth_ns.model('Register', {
    'username': fields.String(required=True, example='user1'),
    'email': fields.String(required=True, example='user1@example.com'),
    'password': fields.String(required=True, example='Pass123!'),
    'role': fields.String(example='user', default='user')
})

def create_auth_response(access_token, refresh_token, user, status_code=200):
    resp_body = {
        "data": {
            "access_token": access_token,
            "user": {
                "username": user.username,
                "email": user.email
            }
        },
        "error": None
    }
    resp = make_response(jsonify(resp_body), status_code)
    set_refresh_cookies(resp, refresh_token)  # Set refresh token cookie properly
    return resp

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @limiter.limit('200/day;50/hour;10/minute')
    def post(self):
        data = request.get_json()
        identifier = data.get('identifier')
        password = data.get('password')

        if not identifier or not password:
            auth_ns.abort(400, message="Identifier and password required")

        user = UserService.authenticate(identifier, password)
        if not user:
            auth_ns.abort(401, message="Invalid credentials")

        access_token, refresh_token = generate_tokens(user)
        logger.info(f"User logged in: {identifier}")

        return create_auth_response(access_token, refresh_token, user)

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    @limiter.limit('200/day;50/hour;10/minute')
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if not username or not email or not password:
            auth_ns.abort(400, message="Username, email, and password required")

        user = UserService.create_user(username, email, password, role)
        access_token, refresh_token = generate_tokens(user)
        logger.info(f"User registered: {username} ({email})")

        return create_auth_response(access_token, refresh_token, user, status_code=201)

@auth_ns.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        user = UserService.get_user_by_username_or_email(current_user)
        if not user:
            auth_ns.abort(401, message="User not found")

        new_access_token = create_access_token(identity=current_user, additional_claims={'role': user.role})
        new_refresh_token, _ = generate_tokens(user)

        logger.info(f"Tokens refreshed for user: {current_user}")
        return create_auth_response(new_access_token, new_refresh_token, user)

@auth_ns.route('/me')
class Me(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = UserService.get_user_by_username_or_email(current_user)
        if not user:
            auth_ns.abort(404, message="User not found")
        return {
            "username": user.username,
            "email": user.email,
        }, 200

@auth_ns.route('/logout')
class Logout(Resource):
    @jwt_required(refresh=True)
    def post(self):
        resp = make_response(jsonify({"msg": "Logged out"}), 200)
        unset_jwt_cookies(resp)  # Clear access and refresh cookies
        return resp
