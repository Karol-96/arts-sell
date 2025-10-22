#!/usr/bin/env python3
import sys
import os
from werkzeug.security import generate_password_hash

# Add current directory to Python path
current_dir = os.getcwd()
sys.path.append(current_dir)

from project import create_app
from project.db import mysql

def create_artists():
    app = create_app()
    with app.app_context():
        cur = mysql.connection.cursor()
        
        artists_data = [
            {
                'id': 1,
                'username': 'artist_test_1',
                'firstname': 'Vincent',
                'lastname': 'Monet',
                'email': 'vincent.monet@artsell.com',
                'phone': '+44 20 7123 4567',
                'bio': 'Contemporary landscape and architectural artist inspired by classical techniques. Specializes in watercolor and oil paintings with a focus on European landmarks and natural scenery.',
                'address': '15 Artist Quarter, London',
                'city': 'London',
                'state': 'England',
                'zip': 'SW1A 1AA',
                'country': 'United Kingdom'
            },
            {
                'id': 2,
                'username': 'artist_test_2',
                'firstname': 'Marie',
                'lastname': 'Rousseau',
                'email': 'marie.rousseau@artsell.com',
                'phone': '+33 1 42 34 56 78',
                'bio': 'French impressionist artist working in various media including watercolor, oil, and pen & ink. Known for capturing everyday life and scenic views with artistic sensitivity.',
                'address': '28 Rue des Artistes, Montmartre',
                'city': 'Paris',
                'state': 'Île-de-France',
                'zip': '75018',
                'country': 'France'
            },
            {
                'id': 3,
                'username': 'artist_test_3',
                'firstname': 'Alessandro',
                'lastname': 'Torres',
                'email': 'alessandro.torres@artsell.com',
                'phone': '+1 212 555 0123',
                'bio': 'Multi-disciplinary artist working across painting, photography, and printmaking. Explores themes of nature, spirituality, and human experience through diverse artistic expressions.',
                'address': '42 Studio Street, SoHo',
                'city': 'New York',
                'state': 'New York',
                'zip': '10013',
                'country': 'United States'
            }
        ]
        
        try:
            default_password = 'Artist123'
            password_hash = generate_password_hash(default_password)
            
            for artist in artists_data:
                cur.execute("""
                    INSERT INTO users (id, role, username, password_hash, email, firstname, lastname, 
                                     phone, bio, address, city, state, zip, country, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, (
                    artist['id'], 'artist', artist['username'], password_hash, artist['email'],
                    artist['firstname'], artist['lastname'], artist['phone'], artist['bio'],
                    artist['address'], artist['city'], artist['state'], artist['zip'], artist['country']
                ))
                
                print(f"✓ Created artist: {artist['firstname']} {artist['lastname']} (ID: {artist['id']})")
            
            mysql.connection.commit()
            print(f"\nSuccessfully created {len(artists_data)} artist users!")
            print(f"Default password for all artists: {default_password}")
            print("Artists should change their passwords on first login.")
            
            # Verify the creation
            cur.execute("SELECT id, username, firstname, lastname, email, role FROM users WHERE role = 'artist' ORDER BY id")
            created_artists = cur.fetchall()
            
            print("\nVerification - Artists in database:")
            for artist in created_artists:
                print(f"ID: {artist['id']}, Username: {artist['username']}, Name: {artist['firstname']} {artist['lastname']}")
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error creating artists: {e}")
            return False
        finally:
            cur.close()
    
    return True

if __name__ == '__main__':
    print("Creating Artist Users...")
    create_artists()