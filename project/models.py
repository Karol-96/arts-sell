from dataclasses import dataclass
from werkzeug.security import generate_password_hash, check_password_hash

@dataclass
class User:
    id: int
    role: str  # 'customer', 'artist', 'admin'
    username: str
    password_hash: str
    firstname: str
    lastname: str
    email: str
    phone: str
    bio: str = None
    address: str = None
    city: str = None
    state: str = None
    zip: str = None
    country: str = None

    def is_active(self):
        return True
    def is_authenticated(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.id
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)