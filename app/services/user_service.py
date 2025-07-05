from ..middlewares.extensions import cache
from ..models.user import User
from mongoengine.errors import NotUniqueError
import logging
import re
from flask_caching.backends.rediscache import RedisCache

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def validate_username(username: str) -> None:
        """Validate username format."""
        if not username or len(username) < 3 or len(username) > 80:
            raise ValueError("Username must be between 3 and 80 characters")
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError("Username can only contain letters, numbers, and underscores")

    @staticmethod
    def validate_email(email: str) -> None:
        """Validate email format."""
        if not email or len(email) > 120:
            raise ValueError("Email must be valid and less than 120 characters")
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValueError("Invalid email format")

    @staticmethod
    def validate_password(password: str) -> None:
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password):
            raise ValueError("Password must contain at least one uppercase letter and one number")

    @staticmethod
    @cache.memoize(timeout=300)
    def get_user_by_username_or_email(identifier: str) -> User:
        """Retrieve a user by username or email."""
        try:
            return User.objects(username=identifier).first() or User.objects(email=identifier).first()
        except Exception as e:
            logger.error(f"Error fetching user by identifier {identifier}: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def create_user(username: str, email: str, password: str, role: str = 'user') -> User:
        """Create a new user with validated inputs."""
        try:
            # Validate inputs
            UserService.validate_username(username)
            UserService.validate_email(email)
            UserService.validate_password(password)

            user = User(username=username, email=email, role=role)
            user.set_password(password)
            user.save()
            cache.delete_memoized(UserService.get_user_by_username_or_email, username)
            cache.delete_memoized(UserService.get_user_by_username_or_email, email)
            logger.info(f"Created user: {username} ({email})")
            return user
        except NotUniqueError:
            logger.warning(f"Failed to create user: username {username} or email {email} already exists")
            raise ValueError("Username or email already exists")
        except Exception as e:
            logger.error(f"Error creating user {username}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def increment_login_attempt(identifier: str) -> int:
        """Increment login attempts for a user."""
        try:
            key = f"login_attempts:{identifier}"
            if isinstance(cache.cache, RedisCache):
                attempts = cache.cache.incr(key)
                if attempts == 1:
                    cache.set(key, attempts, timeout=3600)  # 1-hour expiration
                logger.debug(f"Login attempts for {identifier}: {attempts}")
                return attempts
            else:
                logger.warning("Cache backend is not Redis. Skipping login attempt tracking.")
                return 0
        except Exception as e:
            logger.error(f"Failed to increment login attempts for {identifier}: {str(e)}", exc_info=True)
            return 0

    @staticmethod
    def reset_login_attempt(identifier: str) -> None:
        """Reset login attempts for a user."""
        try:
            key = f"login_attempts:{identifier}"
            if isinstance(cache.cache, RedisCache):
                cache.delete(key)
                logger.debug(f"Reset login attempts for {identifier}")
        except Exception as e:
            logger.error(f"Failed to reset login attempts for {identifier}: {str(e)}", exc_info=True)

    @staticmethod
    def authenticate(identifier: str, password: str) -> User:
        """Authenticate a user by username or email."""
        try:
            attempts = UserService.increment_login_attempt(identifier)
            max_attempts = 5
            if attempts > max_attempts:
                logger.warning(f"Too many login attempts for {identifier}")
                raise ValueError("Too many login attempts, please try again later")

            user = UserService.get_user_by_username_or_email(identifier)
            if user and user.check_password(password):
                UserService.reset_login_attempt(identifier)
                logger.info(f"Successful authentication for {identifier}")
                return user
            logger.warning(f"Failed authentication attempt for {identifier}")
            return None
        except Exception as e:
            logger.error(f"Authentication error for {identifier}: {str(e)}", exc_info=True)
            raise