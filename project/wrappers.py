from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user, login_required

def role_required(required_role):
    def decorator(f):
        @login_required
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role != required_role:
                flash('Access denied. You do not have the required permission', 'danger')
                return redirect(url_for('main.profile'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

admin_required = role_required('admin')
artist_required = role_required('artist')