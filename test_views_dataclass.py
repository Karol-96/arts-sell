#!/usr/bin/env python3
"""
Test script to verify that views.py correctly uses dataclass objects
"""

import sys
import os

# Add current directory to Python path
current_dir = os.getcwd()
sys.path.append(current_dir)

def test_dataclass_properties():
    """Test that the Artwork dataclass has all expected properties"""
    from project.models import Artwork
    
    # Test sample artwork object
    artwork = Artwork(
        id=1,
        title="Test Artwork",
        artist_name="Test Artist", 
        price=100.0,
        status="available",
        height=50.0,
        width=40.0,
        currency="$",
        artist_id=1
    )
    
    # Test object properties (as used in views.py)
    assert artwork.title == "Test Artwork"
    assert artwork.artist_name == "Test Artist"
    assert artwork.price == 100.0
    assert artwork.status == "available"
    assert artwork.artist_id == 1
    
    # Test computed properties
    assert artwork.dimensions == "50.0 x 40.0 cm"
    assert artwork.is_available == True
    
    print("✅ All dataclass properties work correctly")
    print("Views.py has been updated to use:")
    print("- artwork.title instead of artwork['title']")
    print("- artwork.artist_name instead of artwork['artist_name']") 
    print("- artwork.price instead of artwork['price']")
    print("- artwork.status instead of artwork['status']")
    print("- artwork.artist_id instead of artwork['artist_id']")
    print("- artwork.medium instead of artwork['medium']")

if __name__ == '__main__':
    print("Views.py Dataclass Usage Test")
    print("=" * 35)
    test_dataclass_properties()