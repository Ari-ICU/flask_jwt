import os
import redis
import logging
from flask import Flask, request
from flask_restx import Api
from flasgger import Swagger
from mongoengine import connect
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .dbconfigs import Config
from .middlewares.extensions import cache, jwt, bcrypt, limiter
from .middlewares.globalHandler import GlobalHandler
from app.api.auth import auth_ns
from app.api.protected import protected_ns
from .routes import admin_bp, register_admin_namespace

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # -------------------
    # CORS
    # -------------------
    CORS(app, resources={r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type"]
    }})

    # -------------------
    # Database Connection
    # -------------------
    try:
        connect(host=app.config['MONGO_URI'])
        logger.info("MongoDB connection successful.")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}", exc_info=True)
        raise

    # -------------------
    # Redis Connection
    # -------------------
    try:
        redis_client = redis.Redis.from_url(app.config['CACHE_REDIS_URL'], decode_responses=True)
        redis_client.ping()
        app.config['SESSION_REDIS'] = redis_client
        logger.info("Redis connection successful.")
    except redis.exceptions.ConnectionError as e:
        logger.error(f"Redis connection failed: {e}. Falling back to null cache.", exc_info=True)
        app.config['CACHE_TYPE'] = 'null'

    # -------------------
    # Extensions Init
    # -------------------
    cache.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    logger.info("Flask extensions initialized (Cache, JWT, Bcrypt, Limiter).")

    
    # -------------------
    # Flask-RestX API with Security
    # -------------------
    authorizations = {
        'BearerAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Enter: Bearer <JWT token>'
        }
    }

    api = Api(
        app,
        doc='/docs/',
        title='Flask JWT API',
        version='1.0',
        description='A scalable API with JWT, MongoDB, and Redis',
        authorizations=authorizations,
        security='BearerAuth'
    )

    # -------------------
    # Register Blueprints & Namespaces
    # -------------------
    app.register_blueprint(admin_bp)
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(protected_ns, path='/protected')
    register_admin_namespace(api)

    # -------------------
    # Flasgger Swagger Integration (Optional)
    # -------------------
    swagger_template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swagger.yml')
    if os.path.exists(swagger_template_path):
        try:
            Swagger(app, template_file=swagger_template_path)
            logger.info("Flasgger initialized with external swagger.yml.")
        except Exception as e:
            logger.error(f"Failed to initialize Flasgger: {e}", exc_info=True)

    # -------------------
    # Global Handler
    # -------------------
    try:
        app.config.from_object(GlobalHandler)
        logger.info("GlobalHandler config loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load GlobalHandler config: {e}", exc_info=True)

    return app
