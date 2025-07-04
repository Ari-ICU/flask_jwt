from ..middlewares.extensions import cache
from ..models.user import User
from mongoengine.errors import NotUniqueError
import logging
from flask_caching.backends.rediscache import RedisCache


logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    @cache.memoize(timeout=300)
    def get_user_by_username(username):
        return User.objects(username=username).first()
    
    @staticmethod
    def create_user(username, password, role='user'):
        try:
            user = User(username=username, role=role)
            user.set_password(password)
            user.save()
            cache.delete_memoized(UserService.get_user_by_username, username)
            return user
        except NotUniqueError:
            raise ValueError('Username already exists')
    
    @staticmethod
    def increment_login_attempt(username):
        try:
            key = f"login_attempts:{username}"
            if isinstance(cache.cache, RedisCache):
                attempts = cache.cache.incr(key)
                if attempts == 1:
                    cache.set(key, attempts, timeout=3600)
                return attempts
            else:
                logger.warning("Cache backend is not Redis. Skipping login attempt tracking.")
                return 0
        except Exception as e:
            logger.error(f"Failed to increment login attempts: {str(e)}", exc_info=True)
            return 0
        
    @staticmethod
    def reset_login_attempt(username):
        try:
            key = f"login_attempts:{username}"
            if hasattr(cache, 'incr'):
                cache.delete(key)
        except Exception as e:
            logger.error(f"Failed to reset login attempts: {str(e)}", exc_info=True)
    
    @staticmethod
    def authenticate(username, password):
        try:
            attempts = UserService.increment_login_attempt(username)
            max_attempts = 5
            if attempts > max_attempts:
                raise ValueError("Too many login attempts, please try again later.")
            user = UserService.get_user_by_username(username)
            if user and user.check_password(password):
                UserService.reset_login_attempt(username)
                return user
            return None
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            raise