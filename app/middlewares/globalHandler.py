from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask import jsonify
import traceback
import sys
from werkzeug.exceptions import TooManyRequests  # Import for 429

api = Api()
jwt = JWTManager()

class GlobalHandler:
    @api.errorhandler(Exception)
    def handle_error(error):
        print("Error type:", type(error), file=sys.stderr)
        traceback.print_exc()
        msg = str(error)
        if not msg or msg.startswith('<'):
            msg = "Internal Server Error"
        return {'message': msg}, getattr(error, 'code', 500)

    @api.errorhandler(TooManyRequests)
    def handle_too_many_requests(error):
        return {'message': 'Too Many Requests: Limit is 10 per minute'}, 429

    @jwt.unauthorized_loader
    def custom_unauthorized_response(err_msg):
        return jsonify({'message': err_msg}), 401

    @jwt.invalid_token_loader
    def custom_invalid_token_response(err_msg):
        return jsonify({'message': err_msg}), 422

    @jwt.expired_token_loader
    def custom_expired_token_response(jwt_header, jwt_payload):
        return jsonify({'message': 'Token has expired'}), 401

    @jwt.revoked_token_loader
    def custom_revoked_token_response(jwt_header, jwt_payload):
        return jsonify({'message': 'Token has been revoked'}), 401