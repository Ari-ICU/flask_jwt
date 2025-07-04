# services/ratelimit_service.py
from ..middlewares.extensions import limiter

def reset_rate_limit_for_ip(ip: str) -> int:
    """
    Delete all Redis keys for rate limiting of a given IP.
    Returns the number of keys deleted.
    """
    # Access Redis client correctly:
    redis_client = limiter.storage.storage  
    
    pattern = f"LIMITS:LIMITER/{ip}/*"
    keys = redis_client.keys(pattern)
    for key in keys:
        redis_client.delete(key)
    return len(keys)
