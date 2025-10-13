from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from project.forms import RegistrationForm, ArtistRegistrationForm, LoginForm, ProfileForm
from project.db import (create_user, get_user_by_username, update_user_profile, 
                        get_all_artworks, get_artwork_by_id, add_to_cart, 
                        get_cart_items, remove_from_cart, get_cart_total,
                        create_order, get_user_orders, get_cart_count)
from project.wrappers import admin_required, artist_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    tiles = [
        {'title': 'Abstract Art', 'img': 'img/feature-slide-1.png', 'url': url_for('main.artworks'), 'link_title': 'Explore Collection'},
        {'title': 'Landscape', 'img': 'img/feature-slide-2.png', 'url': url_for('main.artworks'), 'link_title': 'View Gallery'},
        {'title': 'Modern Art', 'img': 'img/feature-slide-3.png', 'url': url_for('main.artworks'), 'link_title': 'Discover More'},
        {'title': 'Portrait', 'img': 'img/feature-slide-1.png', 'url': url_for('main.artworks'), 'link_title': 'Browse Artworks'}
    ]
    return render_template('index.html', tiles=tiles)

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
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)
        if user and user.check_password(form.password.data):
            session.permanent = True
            login_user(user)
            flash(f'Welcome back, {user.firstname}!', 'success')
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            elif user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            elif user.role == 'artist':
                return redirect(url_for('main.artist_dashboard'))
            else:
                return redirect(url_for('main.index'))
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

@main.route('/artworks')
def artworks():
    # Get search query and filters
    query = request.args.get('query', '').strip()
    sort_by = request.args.get('sort', 'featured')
    medium_filter = request.args.get('medium', '')
    price_min = request.args.get('price_min', '')
    price_max = request.args.get('price_max', '')
    
    # Get all artworks
    artworks_list = get_all_artworks()
    
    # Apply search filter
    if query:
        artworks_list = [artwork for artwork in artworks_list 
                        if query.lower() in artwork['title'].lower() 
                        or query.lower() in artwork['artist_name'].lower()
                        or query.lower() in artwork['medium'].lower()]
    
    # Apply medium filter
    if medium_filter:
        artworks_list = [artwork for artwork in artworks_list 
                        if medium_filter.lower() in artwork['medium'].lower()]
    
    # Apply price filters
    if price_min:
        try:
            min_price = float(price_min)
            artworks_list = [artwork for artwork in artworks_list if artwork['price'] >= min_price]
        except ValueError:
            pass
    
    if price_max:
        try:
            max_price = float(price_max)
            artworks_list = [artwork for artwork in artworks_list if artwork['price'] <= max_price]
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'price_low':
        artworks_list.sort(key=lambda x: x['price'])
    elif sort_by == 'price_high':
        artworks_list.sort(key=lambda x: x['price'], reverse=True)
    elif sort_by == 'newest':
        artworks_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    elif sort_by == 'popular':
        # For now, just sort by price as a proxy for popularity
        artworks_list.sort(key=lambda x: x['price'], reverse=True)
    
    # Get unique mediums for filter dropdown
    mediums = list(set([artwork['medium'] for artwork in get_all_artworks() if artwork['medium']]))
    
    return render_template('artworks.html', 
                         title='Browse Artworks', 
                         artworks=artworks_list,
                         query=query,
                         sort_by=sort_by,
                         medium_filter=medium_filter,
                         price_min=price_min,
                         price_max=price_max,
                         mediums=mediums)

@main.route('/artwork/<int:artwork_id>')
def artwork_detail(artwork_id):
    artwork = get_artwork_by_id(artwork_id)
    if not artwork:
        flash('Artwork not found', 'danger')
        return redirect(url_for('main.artworks'))
    return render_template('artwork_detail.html', title=artwork['title'], artwork=artwork)

@main.route('/add-to-cart/<int:artwork_id>', methods=['POST'])
@login_required
def add_cart(artwork_id):
    artwork = get_artwork_by_id(artwork_id)
    if not artwork:
        flash('Artwork not found', 'danger')
        return redirect(url_for('main.artworks'))
    
    if add_to_cart(current_user.id, artwork_id):
        flash(f'"{artwork["title"]}" added to cart!', 'success')
    else:
        flash('Failed to add item to cart', 'danger')
    
    referrer = request.referrer
    if referrer and referrer.endswith(f'/artwork/{artwork_id}'):
        return redirect(url_for('main.artwork_detail', artwork_id=artwork_id))
    else:
        return redirect(request.referrer or url_for('main.artworks'))

@main.route('/basket')
@login_required
def basket():
    items = get_cart_items(current_user.id)
    subtotal = get_cart_total(current_user.id)
    shipping = 45.00 if subtotal > 0 else 0
    tax = float(subtotal) * 0.08
    total = float(subtotal) + shipping + tax
    return render_template('basket.html', title='Shopping Basket', 
                         items=items, subtotal=subtotal, shipping=shipping, 
                         tax=tax, total=total)

@main.route('/remove-from-cart/<int:cart_id>', methods=['POST'])
@login_required
def remove_cart(cart_id):
    if remove_from_cart(cart_id, current_user.id):
        flash('Item removed from cart', 'success')
    else:
        flash('Could not remove item', 'danger')
    return redirect(url_for('main.basket'))

@main.route('/checkout')
@login_required
def checkout():
    items = get_cart_items(current_user.id)
    if not items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('main.artworks'))
    
    subtotal = get_cart_total(current_user.id)
    shipping = 45.00
    tax = float(subtotal) * 0.08
    total = float(subtotal) + shipping + tax
    return render_template('checkout.html', title='Checkout',
                         items=items, subtotal=subtotal, shipping=shipping,
                         tax=tax, total=total)

@main.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    items = get_cart_items(current_user.id)
    if not items:
        flash('Cart is empty', 'danger')
        return redirect(url_for('main.artworks'))
    
    subtotal = get_cart_total(current_user.id)
    shipping = 45.00
    tax = float(subtotal) * 0.08
    total = float(subtotal) + shipping + tax
    
    card_number = request.form.get('card_number')
    payment_method = request.form.get('payment_method', 'credit_card')
    
    shipping_addr = f"{current_user.address}, {current_user.city}, {current_user.state} {current_user.zip}"
    
    try:
        order_id = create_order(current_user.id, total, shipping, tax, 
                               shipping_addr, payment_method)
        flash('Payment successful! Order placed.', 'success')
        return redirect(url_for('main.order_success', order_id=order_id))
    except Exception as e:
        flash('Payment failed. Please try again.', 'danger')
        return redirect(url_for('main.checkout'))

@main.route('/order-success/<int:order_id>')
@login_required
def order_success(order_id):
    return render_template('order_success.html', order_id=order_id)

@main.route('/my-orders')
@login_required
def my_orders():
    orders = get_user_orders(current_user.id)
    return render_template('my_orders.html', orders=orders)