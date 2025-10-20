from project import mysql
from project.models import User, Artist, Artwork, Cart, Order, OrderItem
from werkzeug.security import generate_password_hash

# Authentication and User Management Functions
def _row_to_user(row):
    if not row:
        return None
    return User(
        id=row['id'], role=row['role'], username=row['username'], 
        password_hash=row['password_hash'], firstname=row['firstname'], 
        lastname=row['lastname'], email=row['email'], phone=row['phone'], 
        bio=row['bio']
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
def get_all_artworks():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT a.*, CONCAT(a.height, ' x ', a.width, ' cm') as dimensions,
               CONCAT(u.firstname, ' ', u.lastname) as artist_name
        FROM artworks a
        JOIN users u ON a.artist_id = u.id
        ORDER BY a.created_at DESC
    """)
    artworks = cur.fetchall()
    cur.close()
    return artworks

def get_artwork_by_id(artwork_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT a.*, CONCAT(a.height, ' x ', a.width, ' cm') as dimensions,
               CONCAT(u.firstname, ' ', u.lastname) as artist_name
        FROM artworks a
        JOIN users u ON a.artist_id = u.id
        WHERE a.id = %s
    """, (artwork_id,))
    artwork = cur.fetchone()
    cur.close()
    return artwork

def add_to_cart(user_id, artwork_id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT * FROM cart WHERE user_id = %s AND artwork_id = %s", (user_id, artwork_id))
        existing = cur.fetchone()
        
        if existing:
            cur.execute("UPDATE cart SET quantity = quantity + 1 WHERE user_id = %s AND artwork_id = %s",
                       (user_id, artwork_id))
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

def create_order(user_id, total, shipping, tax, address, payment_method):
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            INSERT INTO orders (user_id, total_amount, shipping_cost, tax, shipping_address, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, total, shipping, tax, address, payment_method))
        
        order_id = cur.lastrowid
        
        cur.execute("""
            INSERT INTO order_items (order_id, artwork_id, price, quantity)
            SELECT %s, c.artwork_id, a.price, c.quantity
            FROM cart c
            JOIN artworks a ON c.artwork_id = a.id
            WHERE c.user_id = %s
        """, (order_id, user_id))
        
        # Mark artworks as unavailable when order is placed
        cur.execute("""
            UPDATE artworks 
            SET status = 'unavailable' 
            WHERE id IN (
                SELECT artwork_id FROM cart WHERE user_id = %s
            )
        """, (user_id,))
        
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
        SELECT * FROM orders 
        WHERE user_id = %s 
        ORDER BY created_at DESC
    """, (user_id,))
    orders = cur.fetchall()
    cur.close()
    return orders

def get_cart_count(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT SUM(quantity) as count FROM cart WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    return result['count'] if result and result['count'] else 0

# ============ ADMIN FUNCTIONS ============

def get_all_users():
    """Get all users for admin management"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    cur.close()
    return users

def update_user_role(user_id, new_role):
    """Update user role (admin function)"""
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

def get_all_orders():
    """Get all orders for admin management"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT o.*, u.firstname, u.lastname, u.email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
    """)
    orders = cur.fetchall()
    cur.close()
    return orders

def update_order_status(order_id, new_status):
    """Update order status (admin function)"""
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
    """Get detailed order information"""
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
    """Get items in an order"""
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
    """Get statistics for admin dashboard"""
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

# ============ ARTIST FUNCTIONS ============

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
            SELECT *, CONCAT(height, ' x ', width, ' cm') as dimensions 
            FROM artworks WHERE artist_id = %s ORDER BY created_at DESC
        """, (user_id,))
        artworks = cur.fetchall()
        cur.close()
        return artworks
    except Exception as e:
        cur.close()
        return []

def update_artwork(artwork_id, form, user_id=None):
    """Update artwork details"""
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
            # Admin can update any artwork
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
    """Delete artwork"""
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
    """Get orders for artworks by a specific artist"""
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
    """Get statistics for artist dashboard"""
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

# ============ CUSTOMER FUNCTIONS ============

def add_to_wishlist(user_id, artwork_id):
    """Add artwork to customer wishlist (if wishlist table exists)"""
    # Note: This would require a wishlist table in the database
    # For now, we'll skip this feature as it's not in the current schema
    pass

def get_customer_dashboard_data(user_id):
    """Get data for customer dashboard"""
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