#!/usr/bin/env python3
"""
Script to create a fixed admin user for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import create_app
from project.db import mysql
from werkzeug.security import generate_password_hash

def create_admin_user():
    app = create_app()
    
    with app.app_context():
        cur = mysql.connection.cursor()
        
        try:
            # Check if admin user already exists
            cur.execute("SELECT * FROM users WHERE username = 'admin'")
            existing_admin = cur.fetchone()
            
            if existing_admin:
                print("✅ Admin user already exists!")
                print(f"Username: admin")
                print(f"Password: admin123")
                print(f"Role: {existing_admin['role']}")
                return
            
            # Create admin user
            admin_password = generate_password_hash('admin123')
            cur.execute("""
                INSERT INTO users (role, username, firstname, lastname, email, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ('admin', 'admin', 'Admin', 'User', 'admin@artspace.com', admin_password))
            
            mysql.connection.commit()
            print("✅ Admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
            print("Email: admin@artspace.com")
            print("Role: admin")
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            mysql.connection.rollback()
        finally:
            cur.close()

if __name__ == "__main__":
    create_admin_user()
