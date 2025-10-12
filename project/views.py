from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from project.forms import RegistrationForm, ArtistRegistrationForm, LoginForm, ProfileForm
from project.db import create_user, get_user_by_username, update_user_profile
from project.wrappers import admin_required, artist_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

# Routes for Registration and Login
@main.route('/register/customer', methods=['GET', 'POST'])
def register_customer():
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            create_user(form, role='customer')
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            flash('Registration failed. Please try again.', 'danger')
    return render_template('register.html', form=form, title='Customer Registration')

@main.route('/register/artist', methods=['GET', 'POST'])
def register_artist():
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    
    form = ArtistRegistrationForm()
    if form.validate_on_submit():
        try:
            create_user(form, role='artist')
            flash('Artist registration successful! Please log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            flash('Registration failed. Please try again.', 'danger')
    return render_template('register.html', form=form, title='Artist Registration')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)
        if user and user.check_password(form.password.data):
            # Regenerate session to prevent session fixation
            session.permanent = True
            login_user(user)
            flash(f'Logged in as {user.username}.', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            elif user.role == 'artist':
                return redirect(url_for('main.artist_dashboard'))
            else:
                return redirect(url_for('main.profile'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form, title='Login')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.login'))

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        update_user_profile(current_user.id, form)
        flash('Profile updated successfully', 'success')
        return redirect(url_for('main.profile'))
    return render_template('profile.html', form=form, title='Profile')
    
@main.route('/artist/dashboard')
@artist_required
def artist_dashboard():
    return render_template('artist_dashboard.html', title='Artist Dashboard')

@main.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html', title='Admin Dashboard')