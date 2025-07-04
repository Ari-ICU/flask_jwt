from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..utils.security import role_required
from flask import request


protected_ns = Namespace('protected', description='Protected operations')

@protected_ns.route('/resource')
class ProtectedResource(Resource):
    @jwt_required()
    def get(self):
        print("Authorization header:", request.headers.get("Authorization"))
        claims = get_jwt()
        return {
            'user': get_jwt_identity(),
            'role': claims.get('role'),
            'message': 'Access granted'
        }

@protected_ns.route('/admin')
class AdminResource(Resource):
    @jwt_required()
    @role_required('admin')
    @protected_ns.doc(security='Bearer', responses={200: 'Success', 401: 'Unauthorized', 403: 'Forbidden'})
    def get(self):
        return {'message': 'Admin access granted'}