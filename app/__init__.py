import os
import redis
import logging
from flask import Flask
from flask_restx import Api
from flasgger import Swagger
from mongoengine import connect
from flask_cors import CORS

from .dbconfigs import Config
from .middlewares.extensions import cache, jwt, bcrypt, limiter
from .middlewares.globalHandler import GlobalHandler
from app.api.auth import auth_ns
from app.api.protected import protected_ns
from .routes import admin_bp, register_admin_namespace
from app.api.download import download_ns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token_cookie'

    # CORS
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://localhost:5173"], "supports_credentials": True}})

    # Database
    try:
        connect(host=app.config['MONGO_URI'])
        logger.info("MongoDB connected.")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}", exc_info=True)
        raise

    # Redis
    try:
        redis_client = redis.Redis.from_url(app.config['CACHE_REDIS_URL'], decode_responses=True)
        redis_client.ping()
        app.config['SESSION_REDIS'] = redis_client
        logger.info("Redis connected.")
    except redis.exceptions.ConnectionError as e:
        logger.error(f"Redis connection failed: {e}", exc_info=True)
        app.config['CACHE_TYPE'] = 'null'

    # Extensions
    cache.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)

    # API with global /api prefix
    authorizations = {
        'BearerAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Bearer <JWT token>'
        }
    }

    api = Api(
        app,
        doc='/docs/',
        title='Flask JWT API',
        version='1.0',
        description='A scalable API with JWT, MongoDB, Redis',
        authorizations=authorizations,
        security='BearerAuth',
        prefix='/api'  # Apply to all routes
    )

    # Register
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(protected_ns, path='/protected')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    api.add_namespace(download_ns, path="/video")
    register_admin_namespace(api)

    # Flasgger Swagger
    swagger_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swagger.yml')
    if os.path.exists(swagger_path):
        Swagger(app, template_file=swagger_path)

    # Global Handler
    try:
        app.config.from_object(GlobalHandler)
    except Exception as e:
        logger.error(f"Failed to load GlobalHandler: {e}", exc_info=True)

    return app
