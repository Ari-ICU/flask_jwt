from mongoengine import Document, StringField
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class User(Document):
    username = StringField(required=True, unique=True, max_length=80)
    password_hash = StringField(required=True, max_length=128)
    role = StringField(default='user', max_length=20)
    
    meta = {'collection': 'users', 'indexes': ['username']}
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'