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