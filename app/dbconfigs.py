import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Load environment variables with fallbacks
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-secret-key')  # Fallback for development

    RATELIMIT_DEFAULT = "100 per minute"

    # Database and Cache URLs with Docker-friendly fallbacks
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo:27017/flask_api')
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8080')

    # JWT Configuration
    PROPAGATE_EXCEPTIONS = True
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False  # For development with HTTP
    JWT_COOKIE_CSRF_PROTECT = False  # Disable CSRF for simplicity (enable in production)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)  # Short-lived access token
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)    # Long-lived refresh token

    # Cache Configuration
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_CONFIG = {
        'URL': os.getenv('REDIS_URL', 'redis://redis:6379/0'),  # Use URL directly
        'CONNECTION_POOL_KWARGS': {'max_connections': 10}
    }
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = 'flask_cache_'

    # Validate required environment variables
    @classmethod
    def validate(cls):
        if not cls.SECRET_KEY or not cls.JWT_SECRET_KEY:
            raise ValueError("SECRET_KEY and JWT_SECRET_KEY must be set in environment variables")

# Validate configuration on import
Config.validate()