import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

    # Use Docker service names for Mongo and Redis:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo:27017/flask_api')
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8080')

    JWT_ACCESS_TOKEN_EXPIRES = 3600  
    JWT_REFRESH_TOKEN_EXPIRES = 2592000 
    PROPAGATE_EXCEPTIONS = True 

    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_CONFIG = {
        'CONNECTION_POOL_KWARGS': {'max_connections': 10}
    }
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = 'flask_cache_'
