from project import mysql
from project.models import User
from werkzeug.security import generate_password_hash

# Authentication and User Management Functions
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

def get_user_by_username(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    if row:
        return User(
            id=row['id'], role=row['role'], username=row['username'], password_hash=row['password_hash'],
            firstname=row['firstname'], lastname=row['lastname'], email=row['email'], phone=row['phone'], 
            bio=row['bio'], address=row['address'], city=row['city'], state=row['state'], 
            zip=row['zip'], country=row['country']
        )
    return None

def get_user_by_id(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    if row:
        return User(
            id=row['id'], role=row['role'], username=row['username'], password_hash=row['password_hash'],
            firstname=row['firstname'], lastname=row['lastname'], email=row['email'], phone=row['phone'], 
            bio=row['bio'], address=row['address'], city=row['city'], state=row['state'], 
            zip=row['zip'], country=row['country']
        )
    return None

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

def get_all_artworks():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM artworks WHERE status = 'available'")
    artworks = cur.fetchall()
    cur.close()
    return artworks

def get_artwork_by_id(artwork_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM artworks WHERE id = %s", (artwork_id,))
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
        SELECT c.id, c.artwork_id, c.quantity, a.title, a.artist_name, 
               a.price, a.image_url, a.medium, a.dimensions
        FROM cart c
        JOIN artworks a ON c.artwork_id = a.id
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
        SELECT oi.*, a.title, a.artist_name, a.image_url
        FROM order_items oi
        JOIN artworks a ON oi.artwork_id = a.id
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

def upload_artwork(form, artist_id, image_filename):
    """Upload new artwork by artist"""
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            INSERT INTO artworks (title, artist_name, artist_id, description, medium, dimensions, price, image_url, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            form.title.data,
            form.artist_name.data,
            artist_id,
            form.description.data,
            form.medium.data,
            form.dimensions.data,
            form.price.data,
            f'img/uploads/{image_filename}',
            'available'
        ))
        mysql.connection.commit()
        return cur.lastrowid
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cur.close()

def get_artist_artworks(artist_id):
    """Get all artworks by a specific artist"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM artworks WHERE artist_id = %s ORDER BY created_at DESC", (artist_id,))
    artworks = cur.fetchall()
    cur.close()
    return artworks

def update_artwork(artwork_id, form, artist_id=None):
    """Update artwork details"""
    cur = mysql.connection.cursor()
    try:
        if artist_id:
            # Artist can only update their own artworks
            cur.execute("""
                UPDATE artworks 
                SET title = %s, artist_name = %s, description = %s, medium = %s, dimensions = %s, price = %s
                WHERE id = %s AND artist_id = %s
            """, (form.title.data, form.artist_name.data, form.description.data, 
                  form.medium.data, form.dimensions.data, form.price.data, artwork_id, artist_id))
        else:
            # Admin can update any artwork
            cur.execute("""
                UPDATE artworks 
                SET title = %s, artist_name = %s, description = %s, medium = %s, dimensions = %s, price = %s, status = %s
                WHERE id = %s
            """, (form.title.data, form.artist_name.data, form.description.data, 
                  form.medium.data, form.dimensions.data, form.price.data, form.status.data, artwork_id))
        mysql.connection.commit()
        return True
    except Exception as e:
        mysql.connection.rollback()
        return False
    finally:
        cur.close()

def delete_artwork(artwork_id, artist_id=None):
    """Delete artwork"""
    cur = mysql.connection.cursor()
    try:
        if artist_id:
            # Artist can only delete their own artworks
            cur.execute("DELETE FROM artworks WHERE id = %s AND artist_id = %s", (artwork_id, artist_id))
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

def get_artist_orders(artist_id):
    """Get orders for artworks by a specific artist"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DISTINCT o.*, u.firstname, u.lastname, u.email
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN artworks a ON oi.artwork_id = a.id
        JOIN users u ON o.user_id = u.id
        WHERE a.artist_id = %s
        ORDER BY o.created_at DESC
    """, (artist_id,))
    orders = cur.fetchall()
    cur.close()
    return orders

def get_artist_statistics(artist_id):
    """Get statistics for artist dashboard"""
    cur = mysql.connection.cursor()
    
    # Total artworks by artist
    cur.execute("SELECT COUNT(*) as total FROM artworks WHERE artist_id = %s", (artist_id,))
    total_artworks = cur.fetchone()['total']
    
    # Total sales
    cur.execute("""
        SELECT COUNT(DISTINCT o.id) as total
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN artworks a ON oi.artwork_id = a.id
        WHERE a.artist_id = %s AND o.status != 'cancelled'
    """, (artist_id,))
    total_sales = cur.fetchone()['total']
    
    # Total revenue
    cur.execute("""
        SELECT SUM(oi.price * oi.quantity) as total
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN artworks a ON oi.artwork_id = a.id
        WHERE a.artist_id = %s AND o.status != 'cancelled'
    """, (artist_id,))
    total_revenue = cur.fetchone()['total'] or 0
    
    cur.close()
    return {
        'total_artworks': total_artworks,
        'total_sales': total_sales,
        'total_revenue': total_revenue
    }

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