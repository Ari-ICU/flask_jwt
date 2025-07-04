import os
import redis
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from mongoengine import connect
from flask_caching import Cache
from flasgger import Swagger
from .dbconfigs import Config
from .middlewares.globalHandler import GlobalHandler
from app.api.auth import auth_ns
from app.api.protected import protected_ns
from .middlewares.extensions import cache, jwt, bcrypt, limiter

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    # Test Redis connection
    try:
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_REDIS'] = app.config['CACHE_REDIS_URL']
        redis_client = redis.Redis.from_url(
            app.config['SESSION_REDIS'], decode_responses=True
        )
        redis_client.ping()
        app.logger.info("Redis Cloud connection successful")
    except redis.exceptions.ConnectionError as e:
        app.logger.error(f"Redis Cloud connection failed: {str(e)}. Falling back to null cache.")
        app.config['CACHE_TYPE'] = 'null'

    
   # Initialize MongoDB
    try:
        connect(host=app.config['MONGO_URI'])
        app.logger.info("MongoDB connection successful")
    except Exception as e:
        app.logger.error(f"MongoDB connection failed: {str(e)}")
        raise
    
    # Initialize extensions
    # Initialize Cache
    try:
        cache.init_app(app)
        app.logger.info("Cache initialized successfully.")
    except Exception as e:
        app.logger.error(f"Failed to initialize Cache: {e}", exc_info=True)

    # Initialize JWT
    try:
        jwt.init_app(app)
        app.logger.info("JWT Manager initialized successfully.")
    except Exception as e:
        app.logger.error(f"Failed to initialize JWT Manager: {e}", exc_info=True)

    # Initialize Bcrypt
    try:
        bcrypt.init_app(app)
        app.logger.info("Bcrypt initialized successfully.")
    except Exception as e:
        app.logger.error(f"Failed to initialize Bcrypt: {e}", exc_info=True)


    try:
        limiter.init_app(app)
        app.logger.info("Rate Limiter initialized successfully.")
    except Exception as e:
        app.logger.error(f"Failed to initialize Rate Limiter: {e}", exc_info=True)
   

    # Initialize Flask-RESTX API
    api = Api(
        app,
        title='Flask JWT API with MongoDB and Redis',
        description='A scalable Flask API with JWT, Swagger, MongoDB, and Redis',
        security='Bearer',
        authorizations={
            'Bearer': {'type': 'apiKey', 'in': 'header', 'name': 'Authorization', 'description': 'Enter: Bearer <token>'}
        }
    )
    
    # Initialize Flasgger with correct path to swagger.yaml
    swagger = Swagger(app, template_file=os.path.join(os.path.dirname(__file__), 'swagger.yaml'))
    
  
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(protected_ns, path='/protected')
    
    try:
        app.config.from_object(GlobalHandler)
        app.logger.info("GlobalHandler config loaded successfully")
    except Exception as e:
        app.logger.error(f"Failed to load GlobalHandler config: {e}", exc_info=True)

    return app