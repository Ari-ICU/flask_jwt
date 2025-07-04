from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from limits.storage import RedisStorage

cache = Cache()
jwt = JWTManager()
bcrypt = Bcrypt()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour", "10 per minutes"],
    storage_uri="redis://redis:6379",  
    strategy="moving-window",
)
