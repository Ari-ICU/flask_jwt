import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = '21ccb69dab7ebc6010a087f638606305bb50a71d15fa97c980aa26179b59c7f1'
    JWT_SECRET_KEY = '21ccb69dab7ebc6010a087f638606305bb50a71d15fa97c980aa26179b59c7f1'
    # MongoDB configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/flask_api')
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8080')
    
    
    JWT_ACCESS_TOKEN_EXPIRES = 3600  
    JWT_REFRESH_TOKEN_EXPIRES = 2592000 
    PROPAGATE_EXCEPTIONS = True 

    # Redis Cache Configuration
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = os.getenv('REDIS_URL')  
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = 'flask_cache_'
    CACHE_REDIS_CONFIG = {
        'CONNECTION_POOL_KWARGS': {'max_connections': 10}  
    }