from ..models.user import User
from app.middlewares.extensions import cache
from mongoengine.errors import NotUniqueError

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
    def authenticate(username, password):
        user = UserService.get_user_by_username(username)
        if user and user.check_password(password):
            return user
        return None
