from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import request
from ..utils.security import role_required
import logging

logger = logging.getLogger(__name__)

protected_ns = Namespace('protected', description='Protected operations')

resource_model = protected_ns.model('ProtectedResponse', {
    'user': fields.String(description='User identity from JWT', example='user1'),
    'role': fields.String(description='User role from JWT claims', example='user'),
    'message': fields.String(description='Response message', example='Access granted')
})

admin_model = protected_ns.model('AdminResponse', {
    'message': fields.String(description='Response message', example='Admin access granted')
})


@protected_ns.route('/resource')
class ProtectedResource(Resource):
    @jwt_required()
    @protected_ns.marshal_with(resource_model)
    @protected_ns.doc(security='BearerAuth', responses={
        200: 'Success',
        401: 'Unauthorized',
        500: 'Internal Server Error'
    })
    def get(self):
        """Retrieve protected resource for authenticated users."""
        try:
            logger.info("Authorization header: %s", request.headers.get("Authorization"))
            claims = get_jwt()
            user_identity = get_jwt_identity()
            if not user_identity:
                protected_ns.abort(401, message="Invalid or missing user identity")
            role = claims.get('role', 'unknown')
            return {
                'user': user_identity,
                'role': role,
                'message': 'Access granted'
            }, 200
        except Exception as e:
            logger.error(f"Error in ProtectedResource: {str(e)}", exc_info=True)
            protected_ns.abort(500, message=f"Internal server error: {str(e)}")

@protected_ns.route('/admin')
class AdminResource(Resource):
    @jwt_required()
    @role_required('admin')
    @protected_ns.marshal_with(admin_model)
    @protected_ns.doc(security='BearerAuth', responses={
        200: 'Success',
        401: 'Unauthorized',
        403: 'Forbidden',
        500: 'Internal Server Error'
    })
    def get(self):
        """Retrieve admin resource for users with admin role."""
        try:
            logger.info("Authorization header: %s", request.headers.get("Authorization"))
            return {'message': 'Admin access granted'}, 200
        except Exception as e:
            logger.error(f"Error in AdminResource: {str(e)}", exc_info=True)
            protected_ns.abort(500, message=f"Internal server error: {str(e)}")