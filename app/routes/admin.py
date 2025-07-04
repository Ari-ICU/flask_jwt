from flask import Blueprint, request, jsonify
from flask_restx import Namespace, Resource, fields
from ..services.ratelimit_service import reset_rate_limit_for_ip

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

admin_ns = Namespace('admin', description='Admin operations')

reset_limit_model = admin_ns.model('ResetRateLimitRequest', {
    'ip': fields.String(required=True, description='IP address to reset rate limit for', example='127.0.0.1')
})

reset_limit_response_model = admin_ns.model('ResetRateLimitResponse', {
    'message': fields.String(description='Success message')
})

@admin_ns.route('/reset-rate-limit')
class ResetRateLimit(Resource):
    @admin_ns.expect(reset_limit_model)
    @admin_ns.marshal_with(reset_limit_response_model)
    @admin_ns.doc(responses={
        200: 'Reset successful',
        400: 'IP address missing or invalid'
    })
    def post(self):
        data = request.json or {}
        ip = data.get('ip')
        if not ip:
            admin_ns.abort(400, 'IP address is required')

        deleted_keys = reset_rate_limit_for_ip(ip)
        return {
            'message': f'Reset {deleted_keys} rate limit keys for IP {ip}'
        }, 200


# Register Namespace routes to the blueprint
def register_admin_namespace(api):
    api.add_namespace(admin_ns, path='/admin')

