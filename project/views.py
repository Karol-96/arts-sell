from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from project.forms import (RegistrationForm, ArtistRegistrationForm, LoginForm, ProfileForm,
                          ArtworkUploadForm, ArtworkEditForm, UserManagementForm, OrderStatusForm)
from project.db import (create_user, get_user_by_username, get_user_by_id, update_user_profile, 
                        get_all_artworks, get_artwork_by_id, add_to_cart, 
                        get_cart_items, remove_from_cart, get_cart_total,
                        create_order, get_user_orders, get_cart_count,
                        get_all_users, update_user_role, get_all_orders, 
                        update_order_status, get_order_details, get_order_items,
                        get_admin_statistics, upload_artwork, get_artist_artworks,
                        update_artwork, delete_artwork, get_artist_orders,
                        get_artist_statistics, get_customer_dashboard_data)
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
            elif user.role == 'customer':
                return redirect(url_for('main.profile'))
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

# ============ ADMIN ROUTES ============

@main.route('/admin/users')
@admin_required
def admin_users():
    users = get_all_users()
    return render_template('admin_users.html', title='User Management', users=users)

@main.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('main.admin_users'))
    
    form = UserManagementForm(obj=user)
    if form.validate_on_submit():
        if update_user_role(user_id, form.role.data):
            flash(f'User {user.username} updated successfully', 'success')
        else:
            flash('Failed to update user', 'danger')
        return redirect(url_for('main.admin_users'))
    
    return render_template('admin_edit_user.html', title='Edit User', form=form, user=user)

@main.route('/admin/orders')
@admin_required
def admin_orders():
    orders = get_all_orders()
    return render_template('admin_orders.html', title='Order Management', orders=orders)

@main.route('/admin/orders/<int:order_id>')
@admin_required
def admin_order_detail(order_id):
    order = get_order_details(order_id)
    if not order:
        flash('Order not found', 'danger')
        return redirect(url_for('main.admin_orders'))
    
    items = get_order_items(order_id)
    return render_template('admin_order_detail.html', title='Order Details', order=order, items=items)

@main.route('/admin/orders/update/<int:order_id>', methods=['POST'])
@admin_required
def admin_update_order_status(order_id):
    new_status = request.form.get('status')
    if update_order_status(order_id, new_status):
        flash('Order status updated successfully', 'success')
    else:
        flash('Failed to update order status', 'danger')
    return redirect(url_for('main.admin_order_detail', order_id=order_id))

@main.route('/admin/artworks')
@admin_required
def admin_artworks():
    artworks = get_all_artworks()
    return render_template('admin_artworks.html', title='Artwork Management', artworks=artworks)

@main.route('/admin/artworks/edit/<int:artwork_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_artwork(artwork_id):
    artwork = get_artwork_by_id(artwork_id)
    if not artwork:
        flash('Artwork not found', 'danger')
        return redirect(url_for('main.admin_artworks'))
    
    form = ArtworkEditForm(obj=artwork)
    if form.validate_on_submit():
        if update_artwork(artwork_id, form):
            flash('Artwork updated successfully', 'success')
        else:
            flash('Failed to update artwork', 'danger')
        return redirect(url_for('main.admin_artworks'))
    
    return render_template('admin_edit_artwork.html', title='Edit Artwork', form=form, artwork=artwork)

@main.route('/admin/artworks/delete/<int:artwork_id>', methods=['POST'])
@admin_required
def admin_delete_artwork(artwork_id):
    if delete_artwork(artwork_id):
        flash('Artwork deleted successfully', 'success')
    else:
        flash('Failed to delete artwork', 'danger')
    return redirect(url_for('main.admin_artworks'))

@main.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    stats = get_admin_statistics()
    return render_template('admin_dashboard.html', title='Admin Dashboard', stats=stats)

# ============ ARTIST ROUTES ============

@main.route('/artist/artworks/upload', methods=['GET', 'POST'])
@artist_required
def artist_upload_artwork():
    form = ArtworkUploadForm()
    if form.validate_on_submit():
        if form.image.data:
            # Handle file upload
            file = form.image.data
            filename = secure_filename(file.filename)
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join('project', 'static', 'img', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            try:
                upload_artwork(form, current_user.id, filename)
                flash('Artwork uploaded successfully!', 'success')
                return redirect(url_for('main.artist_artworks'))
            except Exception as e:
                flash('Failed to upload artwork', 'danger')
        else:
            flash('Please select an image file', 'warning')
    
    return render_template('artist_upload.html', title='Upload Artwork', form=form)

@main.route('/artist/artworks')
@artist_required
def artist_artworks():
    artworks = get_artist_artworks(current_user.id)
    return render_template('artist_artworks.html', title='My Artworks', artworks=artworks)

@main.route('/artist/artworks/edit/<int:artwork_id>', methods=['GET', 'POST'])
@artist_required
def artist_edit_artwork(artwork_id):
    artwork = get_artwork_by_id(artwork_id)
    if not artwork or artwork['artist_id'] != current_user.id:
        flash('Artwork not found or access denied', 'danger')
        return redirect(url_for('main.artist_artworks'))
    
    form = ArtworkEditForm(obj=artwork)
    # Remove status field for artists
    del form.status
    
    if form.validate_on_submit():
        if update_artwork(artwork_id, form, current_user.id):
            flash('Artwork updated successfully', 'success')
        else:
            flash('Failed to update artwork', 'danger')
        return redirect(url_for('main.artist_artworks'))
    
    return render_template('artist_edit_artwork.html', title='Edit Artwork', form=form, artwork=artwork)

@main.route('/artist/artworks/delete/<int:artwork_id>', methods=['POST'])
@artist_required
def artist_delete_artwork(artwork_id):
    if delete_artwork(artwork_id, current_user.id):
        flash('Artwork deleted successfully', 'success')
    else:
        flash('Failed to delete artwork', 'danger')
    return redirect(url_for('main.artist_artworks'))

@main.route('/artist/orders')
@artist_required
def artist_orders():
    orders = get_artist_orders(current_user.id)
    return render_template('artist_orders.html', title='My Orders', orders=orders)

@main.route('/artist/dashboard')
@artist_required
def artist_dashboard():
    stats = get_artist_statistics(current_user.id)
    return render_template('artist_dashboard.html', title='Artist Dashboard', stats=stats)

# ============ CUSTOMER ROUTES ============

@main.route('/dashboard/customer')
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    data = get_customer_dashboard_data(current_user.id)
    return render_template('customer_dashboard.html', title='My Dashboard', data=data)