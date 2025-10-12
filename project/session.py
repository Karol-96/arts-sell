from project.db import get_user_by_id
from project import login_manager

@login_manager.user_loader
def load_user(user_id):
    if user_id is None:
        return None
    try:
        user_id = int(user_id)
    except ValueError:
        return None
    return get_user_by_id(user_id)