from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
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
    phone: str = None
    bio: str = None
    address: str = None
    city: str = None
    state: str = None
    zip: str = None
    country: str = None
    created_at: Optional[datetime] = None

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

@dataclass
@dataclass
class Artist:
    user_id: int  # References users.id
    firstname: str
    lastname: str
    email: str
    username: str = None
    phone: str = None
    bio: str = None
    created_at: Optional[datetime] = None
    
    @property
    def full_name(self):
        return f"{self.firstname} {self.lastname}"
    
    @property
    def artist_id(self):
        return self.user_id
    
    @classmethod
    def from_user_data(cls, user_data):
        """Create Artist instance from user database row"""
        return cls(
            user_id=user_data.get('id'),
            firstname=user_data.get('firstname', ''),
            lastname=user_data.get('lastname', ''),
            email=user_data.get('email', ''),
            username=user_data.get('username', ''),
            phone=user_data.get('phone'),
            bio=user_data.get('bio'),
            created_at=user_data.get('created_at')
        )
    
@dataclass
class Artwork:
    id: int
    title: str
    artist_name: str
    price: float
    status: str  # 'available', 'unavailable'
    height: float = field(default=0.0)
    width: float = field(default=0.0)
    currency: str = "$"
    size_category: Optional[str] = None
    category: Optional[str] = None
    medium: Optional[str] = None
    art_origin: Optional[str] = None
    year_of_publish: Optional[int] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    
    @property
    def dimensions(self):
        return f"{self.height} x {self.width} cm"
    
    @property
    def is_available(self):
        return self.status == 'available'

@dataclass
class Cart:
    id: int
    user_id: int
    artwork_id: int
    quantity: int = 1
    added_at: Optional[datetime] = None

@dataclass
class Order:
    id: int
    user_id: int
    total_amount: float
    shipping_cost: float = 45.00
    tax: float = 0.0
    status: str = 'pending'  # 'pending', 'confirmed', 'shipped', 'delivered', 'cancelled'
    shipping_address: str = None
    payment_method: str = None
    created_at: Optional[datetime] = None

@dataclass
class OrderItem:
    id: int
    order_id: int
    artwork_id: int
    price: float
    quantity: int = 1

@dataclass
class PaymentInfo:
    order_id: int
    payment_method: str  # 'credit card', 'paypal', 'stripe'
    account_name: str = None
    account_number: str = None
    payment_date: Optional[datetime] = None
    payment_status: str = 'pending'  # 'pending', 'completed', 'failed'

@dataclass
class RentedArtwork:
    id: int
    order_id: int
    artwork_id: int
    user_id: int
    rental_start_date: datetime
    rental_end_date: datetime
    monthly_price: float
    status: str = 'active'  # 'active', 'returned', 'extended'
    created_at: Optional[datetime] = None