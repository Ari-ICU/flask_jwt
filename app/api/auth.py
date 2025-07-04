from flask_restx import Namespace, Resource, fields
from flask import request
from ..services.user_service import UserService
from ..utils.security import generate_tokens
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.middlewares.extensions import limiter

auth_ns = Namespace('auth', description='Authentication operations')

login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='Username', example='user1'),
    'password': fields.String(required=True, description='Password', example='pass123')
})

register_model = auth_ns.model('Register', {
    'username': fields.String(required=True, description='Username', example='user1'),
    'password': fields.String(required=True, description='Password', example='pass123'),
    'role': fields.String(description='User role', example='user', default='user')
})

token_model = auth_ns.model('Token', {
    'access_token': fields.String(description='Access token'),
    'refresh_token': fields.String(description='Refresh token')
})

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    @limiter.limit('100/day;50/hour')
    @auth_ns.marshal_with(token_model, code=201)
    @auth_ns.doc(responses={201: 'User created', 400: 'Username exists'})
    def post(self):
        data = request.get_json()
        try:
            user = UserService.create_user(data['username'], data['password'], data.get('role', 'user'))
            access_token, refresh_token = generate_tokens(user)
            return {'access_token': access_token, 'refresh_token': refresh_token}, 201
        except ValueError as e:
            auth_ns.abort(400, str(e))

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @limiter.limit('100/day;50/hour')
    @auth_ns.marshal_with(token_model)
    @auth_ns.doc(responses={200: 'Success', 401: 'Invalid credentials'})
    def post(self):
        data = request.get_json()
        user = UserService.authenticate(data['username'], data['password'])
        if not user:
            auth_ns.abort(401, 'Invalid credentials')
        access_token, refresh_token = generate_tokens(user)
        return {'access_token': access_token, 'refresh_token': refresh_token}

@auth_ns.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    @auth_ns.marshal_with(token_model)
    @limiter.limit('100/day;50/hour')
    @auth_ns.doc(security='Bearer', responses={200: 'Success', 401: 'Invalid refresh token'})
    def post(self):
        username = get_jwt_identity()
        access_token = create_access_token(identity=username)
        return {'access_token': access_token, 'refresh_token': None}