from project.db import get_user_by_id
from project import login_manager
from .db import get_cart_count, get_user_orders, get_favorites_count, is_favorite

@login_manager.user_loader
def load_user(user_id):
    if user_id is None:
        return None
    try:
        user_id = int(user_id)
    except ValueError:
        return None
    return get_user_by_id(user_id)

def setup_context_processor(app):
    """Setup context processor for template injection"""
    @app.context_processor
    def inject_user():
        from flask_login import current_user
        cart_count = 0
        favorites_count = 0
        user_orders = []
        if current_user.is_authenticated:
            cart_count = get_cart_count(current_user.id)
            favorites_count = get_favorites_count(current_user.id)
            user_orders = get_user_orders(current_user.id)
        return dict(current_user=current_user, get_cart_count=get_cart_count, 
                   get_user_orders=get_user_orders, get_favorites_count=get_favorites_count,
                   is_favorite=is_favorite)