import redis
from mongoengine.errors import NotUniqueError
from app.middlewares.extensions import cache
from ..models.user import User

class UserService:
    @staticmethod
    @cache.memoize(timeout=300)  # Cache user lookup for 5 minutes in Redis
    def get_user_by_username(username):
        return User.objects(username=username).first()
    
    @staticmethod
    def create_user(username, password, role='user'):
        try:
            user = User(username=username, role=role)
            user.set_password(password)
            user.save()
            # Invalidate cache for this username after creation
            cache.delete_memoized(UserService.get_user_by_username, username)
            return user
        except NotUniqueError:
            raise ValueError('Username already exists')
    
    @staticmethod
    def increment_login_attempt(username):
        redis_client: redis.Redis = cache.cache._client  
        key = f"login_attempts:{username}"
        attempts = redis_client.incr(key)
        if attempts == 1:
            redis_client.expire(key, 3600)  
        return attempts

    @staticmethod
    def reset_login_attempt(username):
        redis_client: redis.Redis = cache.cache._client
        key = f"login_attempts:{username}"
        redis_client.delete(key)

    @staticmethod
    def authenticate(username, password):
        # Check login attempts before authenticating
        attempts = UserService.increment_login_attempt(username)
        max_attempts = 5
        if attempts > max_attempts:
            raise ValueError("Too many login attempts, please try again later.")

        user = UserService.get_user_by_username(username)
        if user and user.check_password(password):
            # Reset login attempts on successful login
            UserService.reset_login_attempt(username)
            return user

        return None
