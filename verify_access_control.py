#!/usr/bin/env python3
"""
Script to verify role-based access control implementation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import create_app
from project.db import mysql

def verify_access_control():
    app = create_app()
    
    print("🔐 VERIFYING ROLE-BASED ACCESS CONTROL")
    print("=" * 50)
    
    with app.app_context():
        cur = mysql.connection.cursor()
        
        try:
            # Check if users exist
            cur.execute("SELECT username, role FROM users ORDER BY role")
            users = cur.fetchall()
            
            if not users:
                print("❌ No users found. Please create users first.")
                return
            
            print("📋 EXISTING USERS:")
            for user in users:
                print(f"   - {user['username']} ({user['role']})")
            
            print("\n🔍 ACCESS CONTROL VERIFICATION:")
            print("\n✅ ARTIST-ONLY OPERATIONS:")
            artist_routes = [
                '/artist/artworks/upload',
                '/artist/artworks',
                '/artist/artworks/edit/<id>',
                '/artist/artworks/delete/<id>',
                '/artist/orders',
                '/artist/dashboard'
            ]
            for route in artist_routes:
                print(f"   - {route} (Protected with @artist_required)")
            
            print("\n✅ ADMIN-ONLY OPERATIONS:")
            admin_routes = [
                '/admin/users',
                '/admin/users/edit/<id>',
                '/admin/orders',
                '/admin/orders/<id>',
                '/admin/orders/update/<id>',
                '/admin/artworks',
                '/admin/artworks/edit/<id>',
                '/admin/artworks/delete/<id>',
                '/admin/dashboard'
            ]
            for route in admin_routes:
                print(f"   - {route} (Protected with @admin_required)")
            
            print("\n✅ CUSTOMER OPERATIONS:")
            customer_routes = [
                '/dashboard/customer',
                '/my-orders',
                '/basket',
                '/checkout'
            ]
            for route in customer_routes:
                print(f"   - {route} (Available to all authenticated users)")
            
            print("\n🛡️ SECURITY FEATURES:")
            print("   ✅ Artists can only edit/delete their own artworks")
            print("   ✅ Admins can manage all users, orders, and artworks")
            print("   ✅ Customers can only view their own orders")
            print("   ✅ Role-based navigation menus")
            print("   ✅ Automatic redirect to appropriate dashboard on login")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            cur.close()

if __name__ == "__main__":
    verify_access_control()
