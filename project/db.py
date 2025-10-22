from project import mysql
from project.models import User, Artist, Artwork, Order, PaymentInfo, RentedArtwork
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

# Authentication and User Management Functions
def _row_to_user(row):
    if not row:
        return None
    return User(
        id=row['id'], role=row['role'], username=row['username'], 
        password_hash=row['password_hash'], firstname=row['firstname'], 
        lastname=row['lastname'], email=row['email'], phone=row['phone'], 
        bio=row['bio'], address=row['address'], city=row['city'], 
        state=row['state'], zip=row['zip'], country=row['country']
    )

def create_user(form, role):
    cur = mysql.connection.cursor()
    try:
        hashed_password = generate_password_hash(form.password.data)
        cur.execute("""
            INSERT INTO users (role, username, firstname, lastname, email, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (role, form.username.data, form.firstname.data, form.lastname.data, form.email.data, hashed_password))
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cur.close()
    return True

def get_user_by_username(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    return _row_to_user(row)

def get_user_by_id(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    return _row_to_user(row)

def check_username(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    return True if row else False

def check_email(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    row = cur.fetchone()
    cur.close()
    return True if row else False

def update_user_profile(user_id, form):
    cur = mysql.connection.cursor()
    try:
        bio_data = form.bio.data if form.bio.data else None
        phone_data = form.phone.data if form.phone.data else None
        address_data = form.address.data if form.address.data else None
        city_data = form.city.data if form.city.data else None
        state_data = form.state.data if form.state.data else None
        zip_data = form.zip.data if form.zip.data else None
        country_data = form.country.data if form.country.data else None
        
        cur.execute("""
            UPDATE users
            SET firstname = %s, lastname = %s, email = %s, phone = %s, bio = %s,
                address = %s, city = %s, state = %s, zip = %s, country = %s
            WHERE id = %s
        """, (form.firstname.data, form.lastname.data, form.email.data,
              phone_data, bio_data,  address_data, city_data, state_data, zip_data, country_data, user_id))
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cur.close()

# Artwork and Cart Management Functions
def _row_to_artwork(row):
    if not row:
        return None
    return Artwork(
        id=row['id'], title=row['title'], artist_name=row['artist_name'], 
        price=float(row['price']), status=row['status'], height=float(row['height']), 
        width=float(row['width']), size_category=row['size_category'], 
        category=row['category'], medium=row['medium'], art_origin=row['art_origin'], 
        year_of_publish=row['year_of_publish'], image_url=row['image_url'], 
        description=row['description'], currency=row['currency'], created_at=row['created_at'],
        artist_id=row.get('artist_id')
    )

def _row_to_order(row):
    if not row:
        return None
    return Order(
        id=row['id'], user_id=row['user_id'], total_amount=float(row['total_amount']),
        shipping_cost=float(row.get('shipping_cost', 0.0)), tax=float(row.get('tax', 0.0)),
        status=row.get('status', 'pending'), shipping_address=row.get('shipping_address'),
        payment_method=row.get('payment_method'), created_at=row.get('created_at')
    )

def _row_to_rented_artwork(row):
    if not row:
        return None
    return RentedArtwork(
        id=row['id'], order_id=row['order_id'], artwork_id=row['artwork_id'],
        user_id=row['user_id'], rental_start_date=row['rental_start_date'],
        rental_end_date=row['rental_end_date'], monthly_price=row['monthly_price'],
        status=row.get('status', 'active'), created_at=row.get('created_at')
    )

def get_all_artworks(sort_by=None):
    cur = mysql.connection.cursor()
    
    base_query = """
        SELECT a.*, CONCAT(a.height, ' x ', a.width, ' cm') as dimensions,
               CONCAT(u.firstname, ' ', u.lastname) as artist_name
        FROM artworks a
        JOIN users u ON a.artist_id = u.id
    """

    if sort_by == 'price_low':
        query = base_query + " ORDER BY a.price ASC"
    elif sort_by == 'price_high':
        query = base_query + " ORDER BY a.price DESC"
    elif sort_by == 'oldest':
        query = base_query + " ORDER BY a.id ASC"
    else:
        query = base_query + " ORDER BY a.id DESC"
    
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    return [_row_to_artwork(row) for row in rows]

def get_artwork_by_id(artwork_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT a.*, CONCAT(a.height, ' x ', a.width, ' cm') as dimensions,
               CONCAT(u.firstname, ' ', u.lastname) as artist_name
        FROM artworks a
        JOIN users u ON a.artist_id = u.id
        WHERE a.id = %s
    """, (artwork_id,))
    row = cur.fetchone()
    cur.close()
    return _row_to_artwork(row)

def get_unique_mediums():
    """Get all unique mediums from artworks database"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT medium FROM artworks WHERE medium IS NOT NULL AND medium != '' ORDER BY medium")
    rows = cur.fetchall()
    cur.close()
    return [row['medium'] for row in rows]

def add_to_cart(user_id, artwork_id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT * FROM cart WHERE user_id = %s AND artwork_id = %s", (user_id, artwork_id))
        existing = cur.fetchone()
        
        if existing:
            return False
        else:
            cur.execute("INSERT INTO cart (user_id, artwork_id) VALUES (%s, %s)", (user_id, artwork_id))
        mysql.connection.commit()
        return True
    except Exception as e:
        mysql.connection.rollback()
        return False
    finally:
        cur.close()

def get_cart_items(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.id, c.artwork_id, c.quantity, a.title, 
               CONCAT(u.firstname, ' ', u.lastname) as artist_name,
               a.price, a.image_url, a.medium, a.height, a.width,
               CONCAT(a.height, ' x ', a.width, ' cm') as dimensions
        FROM cart c
        JOIN artworks a ON c.artwork_id = a.id
        JOIN users u ON a.artist_id = u.id
        WHERE c.user_id = %s
    """, (user_id,))
    items = cur.fetchall()
    cur.close()
    return items

def remove_from_cart(cart_id, user_id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM cart WHERE id = %s AND user_id = %s", (cart_id, user_id))
        mysql.connection.commit()
        return True
    except:
        mysql.connection.rollback()
        return False
    finally:
        cur.close()

def clear_user_cart(user_id: int) -> bool:
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        mysql.connection.commit()
        return True
    except:
        mysql.connection.rollback()
        return False

def get_cart_total(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT SUM(a.price * c.quantity) as total
        FROM cart c
        JOIN artworks a ON c.artwork_id = a.id
        WHERE c.user_id = %s
    """, (user_id,))
    result = cur.fetchone()
    cur.close()
    return result['total'] if result['total'] else 0

def create_order(user_id, total, shipping, tax, address, payment_method, account_name=None, card_number=None):
    cur = mysql.connection.cursor()
    try:
        # Step 1: Create the order with initial 'pending' status
        cur.execute("""
            INSERT INTO orders (user_id, total_amount, shipping_cost, tax, shipping_address, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, total, shipping, tax, address, payment_method))
        
        order_id = cur.lastrowid
        
        # Create order items
        cur.execute("""
            INSERT INTO order_items (order_id, artwork_id, price, quantity)
            SELECT %s, c.artwork_id, a.price, c.quantity
            FROM cart c
            JOIN artworks a ON c.artwork_id = a.id
            WHERE c.user_id = %s
        """, (order_id, user_id))
        
        # Step 3: Process payment with random status
        payment_statuses = ['pending', 'completed', 'failed']
        payment_status = random.choice(payment_statuses)
        
        # Get last 4 digits of card number for security
        account_number_masked = None
        if card_number:
            card_number_clean = card_number.replace(' ', '').replace('-', '')
            if len(card_number_clean) >= 4:
                account_number_masked = f"****{card_number_clean[-4:]}"
        
        # Create payment info record
        cur.execute("""
            INSERT INTO payment_info (order_id, payment_method, account_name, account_number, payment_status)
            VALUES (%s, %s, %s, %s, %s)
        """, (order_id, payment_method, account_name, account_number_masked, payment_status))
        
        # Step 4: Update order status based on payment status
        if payment_status == 'pending':
            order_status = 'pending'
        elif payment_status == 'completed':
            order_status = 'success'
        else:  # failed
            order_status = 'cancelled'
        
        cur.execute("UPDATE orders SET status = %s WHERE id = %s", (order_status, order_id))
        
        # If payment successful, handle artwork and rental
        if payment_status == 'completed':
            # Mark artworks as unavailable
            cur.execute("""
                UPDATE artworks 
                SET status = 'unavailable' 
                WHERE id IN (
                    SELECT artwork_id FROM cart WHERE user_id = %s
                )
            """, (user_id,))
            
            # Create rental entries (1 month rental period)
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30)
            
            cur.execute("""
                INSERT INTO rented_artworks (order_id, artwork_id, user_id, rental_start_date, rental_end_date, monthly_price)
                SELECT %s, c.artwork_id, %s, %s, %s, a.price
                FROM cart c
                JOIN artworks a ON c.artwork_id = a.id
                WHERE c.user_id = %s
            """, (order_id, user_id, start_date, end_date, user_id))
        
        # Clear cart regardless of payment status
        cur.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        
        mysql.connection.commit()
        return order_id
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cur.close()

def get_user_orders(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT o.*, p.payment_status
        FROM orders o
        LEFT JOIN payment_info p ON o.id = p.order_id
        WHERE o.user_id = %s 
        ORDER BY o.created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    return [_row_to_order(row) for row in rows]

def get_cart_count(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT SUM(quantity) as count FROM cart WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    return result['count'] if result and result['count'] else 0

# Admin Functions: CRUD
def get_all_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    cur.close()
    return users

def update_user_role(user_id, new_role):
    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
        mysql.connection.commit()
        return True
    except Exception as e:
        mysql.connection.rollback()
        return False
    finally:
        cur.close()

def delete_user(user_id):
    cur = mysql.connection.cursor()
    try:
        # Check if user exists
        cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cur.fetchone():
            return False
        
        # Delete user (CASCADE will handle related records)
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        mysql.connection.commit()
        return True
    except Exception as e:
        mysql.connection.rollback()
        return False
    finally:
        cur.close()

def get_all_orders():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT o.*, u.firstname, u.lastname, u.email, p.payment_status
        FROM orders o
        JOIN users u ON o.user_id = u.id
        LEFT JOIN payment_info p ON o.id = p.order_id
        ORDER BY o.created_at DESC
    """)
    orders = cur.fetchall()
    cur.close()
    return orders

def update_order_status(order_id, new_status):
    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE orders SET status = %s WHERE id = %s", (new_status, order_id))
        mysql.connection.commit()
        return True
    except Exception as e:
        mysql.connection.rollback()
        return False
    finally:
        cur.close()

def get_order_details(order_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT o.*, u.firstname, u.lastname, u.email, u.phone
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.id = %s
    """, (order_id,))
    order = cur.fetchone()
    cur.close()
    return order

def get_order_items(order_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT oi.*, a.title, CONCAT(u.firstname, ' ', u.lastname) as artist_name, a.image_url
        FROM order_items oi
        JOIN artworks a ON oi.artwork_id = a.id
        JOIN users u ON a.artist_id = u.id
        WHERE oi.order_id = %s
    """, (order_id,))
    items = cur.fetchall()
    cur.close()
    return items

def get_admin_statistics():
    cur = mysql.connection.cursor()
    
    # Total users
    cur.execute("SELECT COUNT(*) as total FROM users")
    total_users = cur.fetchone()['total']
    
    # Total artists
    cur.execute("SELECT COUNT(*) as total FROM users WHERE role = 'artist'")
    total_artists = cur.fetchone()['total']
    
    # Total artworks
    cur.execute("SELECT COUNT(*) as total FROM artworks")
    total_artworks = cur.fetchone()['total']
    
    # Total revenue
    cur.execute("SELECT SUM(total_amount) as total FROM orders WHERE status != 'cancelled'")
    total_revenue = cur.fetchone()['total'] or 0
    
    cur.close()
    return {
        'total_users': total_users,
        'total_artists': total_artists,
        'total_artworks': total_artworks,
        'total_revenue': total_revenue
    }

# Artist DB Functions

def get_artist_by_user_id(user_id):
    """Get artist information by user_id"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s AND role = 'artist'", (user_id,))
    row = cur.fetchone()
    cur.close()
    if row:
        return Artist(
            user_id=row['id'],
            firstname=row['firstname'],
            lastname=row['lastname'],
            email=row['email'],
            phone=row['phone'],
            bio=row['bio'],
            created_at=row['created_at']
        )
    return None

def upload_artwork(form, user_id, image_filename):
    """Upload new artwork by artist"""
    cur = mysql.connection.cursor()
    try:
        # Get artist info
        artist = get_artist_by_user_id(user_id)
        if not artist:
            raise Exception("User is not an artist")
        
        # Determine size category
        area = form.height.data * form.width.data
        if area < 1000:
            size_category = 'small'
        elif area < 5000:
            size_category = 'medium'
        else:
            size_category = 'large'
        
        cur.execute("""
            INSERT INTO artworks (title, artist_id, description, medium, height, width, 
                                price, image_url, status, category, art_origin, year_of_publish, 
                                currency, size_category)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            form.title.data,
            user_id,
            form.description.data,
            form.medium.data,
            form.height.data,
            form.width.data,
            form.price.data,
            f'img/uploads/{image_filename}',
            'available',
            form.category.data if hasattr(form, 'category') else None,
            form.art_origin.data if hasattr(form, 'art_origin') else None,
            form.year_of_publish.data if hasattr(form, 'year_of_publish') else None,
            '$',
            size_category
        ))
        mysql.connection.commit()
        return cur.lastrowid
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cur.close()

def get_artist_artworks(user_id):
    """Get all artworks by a specific artist user_id"""
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT a.*, CONCAT(a.height, ' x ', a.width, ' cm') as dimensions,
                   CONCAT(u.firstname, ' ', u.lastname) as artist_name
            FROM artworks a
            JOIN users u ON a.artist_id = u.id
            WHERE a.artist_id = %s ORDER BY a.created_at DESC
        """, (user_id,))
        rows = cur.fetchall()
        cur.close()
        return [_row_to_artwork(row) for row in rows]
    except Exception as e:
        cur.close()
        return []

def update_artwork(artwork_id, form, user_id=None):
    cur = mysql.connection.cursor()
    try:
        # Calculate size category
        area = form.height.data * form.width.data
        if area < 1000:
            size_category = 'small'
        elif area < 5000:
            size_category = 'medium'
        else:
            size_category = 'large'
            
        if user_id:
            # Artist can only update their own artworks
            cur.execute("""
                UPDATE artworks 
                SET title = %s, description = %s, medium = %s, height = %s, width = %s, 
                    price = %s, category = %s, art_origin = %s, year_of_publish = %s, size_category = %s
                WHERE id = %s AND artist_id = %s
            """, (form.title.data, form.description.data, form.medium.data, 
                  form.height.data, form.width.data, form.price.data,
                  form.category.data if hasattr(form, 'category') else None,
                  form.art_origin.data if hasattr(form, 'art_origin') else None,
                  form.year_of_publish.data if hasattr(form, 'year_of_publish') else None,
                  size_category, artwork_id, user_id))
        else:
            # But admin can update them all
            cur.execute("""
                UPDATE artworks 
                SET title = %s, description = %s, medium = %s, height = %s, width = %s, 
                    price = %s, status = %s, category = %s, art_origin = %s, year_of_publish = %s, size_category = %s
                WHERE id = %s
            """, (form.title.data, form.description.data, 
                  form.medium.data, form.height.data, form.width.data, form.price.data, form.status.data,
                  form.category.data if hasattr(form, 'category') else None,
                  form.art_origin.data if hasattr(form, 'art_origin') else None,
                  form.year_of_publish.data if hasattr(form, 'year_of_publish') else None,
                  size_category, artwork_id))
        mysql.connection.commit()
        return True
    except Exception as e:
        mysql.connection.rollback()
        return False
    finally:
        cur.close()

def delete_artwork(artwork_id, user_id=None):
    cur = mysql.connection.cursor()
    try:
        if user_id:
            # Artist can only delete their own artworks
            cur.execute("DELETE FROM artworks WHERE id = %s AND artist_id = %s", (artwork_id, user_id))
        else:
            # Admin can delete any artwork
            cur.execute("DELETE FROM artworks WHERE id = %s", (artwork_id,))
        mysql.connection.commit()
        return True
    except Exception as e:
        mysql.connection.rollback()
        return False
    finally:
        cur.close()

def get_artist_orders(user_id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT DISTINCT o.*, u.firstname, u.lastname, u.email
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN artworks a ON oi.artwork_id = a.id
            JOIN users u ON o.user_id = u.id
            WHERE a.artist_id = %s
            ORDER BY o.created_at DESC
        """, (user_id,))
        orders = cur.fetchall()
        cur.close()
        return orders
    except Exception as e:
        cur.close()
        return []

def get_artist_statistics(user_id):
    cur = mysql.connection.cursor()
    try:
        # Total artworks by artist
        cur.execute("SELECT COUNT(*) as total FROM artworks WHERE artist_id = %s", (user_id,))
        total_artworks = cur.fetchone()['total']
        
        # Total sales
        cur.execute("""
            SELECT COUNT(DISTINCT o.id) as total
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN artworks a ON oi.artwork_id = a.id
            WHERE a.artist_id = %s AND o.status != 'cancelled'
        """, (user_id,))
        total_sales = cur.fetchone()['total']
        
        # Total revenue
        cur.execute("""
            SELECT SUM(oi.price * oi.quantity) as total
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN artworks a ON oi.artwork_id = a.id
            WHERE a.artist_id = %s AND o.status != 'cancelled'
        """, (user_id,))
        total_revenue = cur.fetchone()['total'] or 0
        
        cur.close()
        return {
            'total_artworks': total_artworks,
            'total_sales': total_sales,
            'total_revenue': total_revenue
        }
    except Exception as e:
        cur.close()
        return {'total_artworks': 0, 'total_sales': 0, 'total_revenue': 0}

# Favorite DB Functions

def add_to_favorites(user_id, artwork_id):
    """Add artwork to user's favorites"""
    cur = mysql.connection.cursor()
    try:
        # Check if already in favorites
        cur.execute("SELECT * FROM favorites WHERE user_id = %s AND artwork_id = %s", (user_id, artwork_id))
        existing = cur.fetchone()
        
        if existing:
            return False  # Already in favorites
        
        cur.execute("INSERT INTO favorites (user_id, artwork_id) VALUES (%s, %s)", (user_id, artwork_id))
        mysql.connection.commit()
        return True
    except Exception as e:
        mysql.connection.rollback()
        return False
    finally:
        cur.close()

def remove_from_favorites(user_id, artwork_id):
    """Remove artwork from user's favorites"""
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM favorites WHERE user_id = %s AND artwork_id = %s", (user_id, artwork_id))
        mysql.connection.commit()
        return cur.rowcount > 0  # Return True if something was deleted
    except Exception as e:
        mysql.connection.rollback()
        return False
    finally:
        cur.close()

def is_favorite(user_id, artwork_id):
    """Check if artwork is in user's favorites"""
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT id FROM favorites WHERE user_id = %s AND artwork_id = %s", (user_id, artwork_id))
        result = cur.fetchone()
        cur.close()
        return result is not None
    except Exception as e:
        cur.close()
        return False

def get_user_favorites(user_id):
    """Get all artworks in user's favorites with artwork details"""
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT f.id as favorite_id, f.added_at as favorited_at,
                   a.id, a.title, a.price, a.status, a.height, a.width, 
                   a.medium, a.image_url, a.description, a.currency,
                   CONCAT(u.firstname, ' ', u.lastname) as artist_name,
                   CONCAT(a.height, ' x ', a.width, ' cm') as dimensions
            FROM favorites f
            JOIN artworks a ON f.artwork_id = a.id
            JOIN users u ON a.artist_id = u.id
            WHERE f.user_id = %s
            ORDER BY f.added_at DESC
        """, (user_id,))
        favorites = cur.fetchall()
        cur.close()
        return favorites
    except Exception as e:
        cur.close()
        return []

def get_favorites_count(user_id):
    """Get count of user's favorites"""
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT COUNT(*) as count FROM favorites WHERE user_id = %s", (user_id,))
        result = cur.fetchone()
        cur.close()
        return result['count'] if result and result['count'] else 0
    except Exception as e:
        cur.close()
        return 0

# Customer Functions

def get_customer_dashboard_data(user_id):
    cur = mysql.connection.cursor()
    # Recent orders
    cur.execute("""
        SELECT * FROM orders 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT 5
    """, (user_id,))
    recent_orders = cur.fetchall()
    
    # Total orders
    cur.execute("SELECT COUNT(*) as total FROM orders WHERE user_id = %s", (user_id,))
    total_orders = cur.fetchone()['total']
    
    # Total spent
    cur.execute("""
        SELECT SUM(total_amount) as total 
        FROM orders 
        WHERE user_id = %s AND status != 'cancelled'
    """, (user_id,))
    total_spent = cur.fetchone()['total'] or 0
    
    cur.close()
    return {
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'total_spent': total_spent
    }

# Payment DB Functions

def create_payment_info(order_id, payment_method, account_name=None, account_number=None):
    """Create payment information for an order"""
    cur = mysql.connection.cursor()
    try:
        # Randomly select payment status because we do not implement real payment and we are not suppose to edit a payment
        payment_statuses = ['pending', 'completed', 'failed']
        payment_status = random.choice(payment_statuses)
        
        cur.execute("""
            INSERT INTO payment_info (order_id, payment_method, account_name, account_number, payment_status)
            VALUES (%s, %s, %s, %s, %s)
        """, (order_id, payment_method, account_name, account_number, payment_status))
        
        mysql.connection.commit()
        
        payment_info = PaymentInfo(
            order_id=order_id,
            payment_method=payment_method,
            account_name=account_name,
            account_number=account_number,
            payment_status=payment_status
        )
        return payment_info
    except Exception as e:
        mysql.connection.rollback()
        return None
    finally:
        cur.close()

def get_payment_info_by_order(order_id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT * FROM payment_info WHERE order_id = %s
        """, (order_id,))
        row = cur.fetchone()
        cur.close()
        
        if row:
            return PaymentInfo(
                order_id=row['order_id'],
                payment_method=row['payment_method'],
                account_name=row.get('account_name'),
                account_number=row.get('account_number'),
                payment_date=row.get('payment_date'),
                payment_status=row['payment_status']
            )
        return None
    except Exception as e:
        cur.close()
        return None

# Record Rented Artworks

def create_rental(order_id, artwork_id, user_id, start_date, end_date, monthly_price):
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            INSERT INTO rented_artworks (order_id, artwork_id, user_id, rental_start_date, rental_end_date, monthly_price)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (order_id, artwork_id, user_id, start_date, end_date, monthly_price))
        mysql.connection.commit()
        
        rental_id = cur.lastrowid
        return get_rental_by_id(rental_id)
    except Exception as e:
        mysql.connection.rollback()
        return None
    finally:
        cur.close()

def get_rental_by_id(rental_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM rented_artworks WHERE id = %s", (rental_id,))
    row = cur.fetchone()
    cur.close()
    return _row_to_rented_artwork(row)

def get_user_rentals(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT ra.*, a.title as artwork_title 
        FROM rented_artworks ra
        JOIN artworks a ON ra.artwork_id = a.id
        WHERE ra.user_id = %s
        ORDER BY ra.created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    return [_row_to_rented_artwork(row) for row in rows]

def update_rental_status(rental_id, status):
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            UPDATE rented_artworks 
            SET status = %s 
            WHERE id = %s
        """, (status, rental_id))
        mysql.connection.commit()
        return True
    except Exception as e:
        mysql.connection.rollback()
        return False
    finally:
        cur.close()