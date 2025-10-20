#!/usr/bin/env python3
"""
Script to create test users for different roles
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import create_app
from project.db import mysql
from werkzeug.security import generate_password_hash

def create_test_users():
    app = create_app()
    
    with app.app_context():
        cur = mysql.connection.cursor()
        
        try:
            # Create test artist
            artist_password = generate_password_hash('artist123')
            cur.execute("""
                INSERT INTO users (role, username, firstname, lastname, email, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ('artist', 'artist', 'John', 'Painter', 'artist@artspace.com', artist_password))
            
            # Create test customer
            customer_password = generate_password_hash('customer123')
            cur.execute("""
                INSERT INTO users (role, username, firstname, lastname, email, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ('customer', 'customer', 'Jane', 'Buyer', 'customer@artspace.com', customer_password))
            
            mysql.connection.commit()
            print("✅ Test users created successfully!")
            print("\n📋 Test User Credentials:")
            print("🎨 ARTIST:")
            print("   Username: artist")
            print("   Password: artist123")
            print("   Role: artist")
            print("\n🛒 CUSTOMER:")
            print("   Username: customer")
            print("   Password: customer123")
            print("   Role: customer")
            
        except Exception as e:
            print(f"❌ Error creating test users: {e}")
            mysql.connection.rollback()
        finally:
            cur.close()

if __name__ == "__main__":
    create_test_users()
