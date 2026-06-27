#!/usr/bin/env python
"""
Simple script to set up product codes for existing menu items
"""
import os
import sys
import django

# Add the project directory (backend root, parent of scripts/) to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_backend.settings')
django.setup()

from menu.models import MenuItem

def setup_product_codes():
    """Set up product codes for existing menu items"""
    print("🔧 Setting up product codes for existing menu items...")
    
    # Get all menu items without product codes
    items_without_codes = MenuItem.objects.filter(product_code__isnull=True)
    
    if not items_without_codes.exists():
        print("✅ All menu items already have product codes!")
        return
    
    print(f"Found {items_without_codes.count()} items without product codes:")
    
    for i, item in enumerate(items_without_codes, 1):
        # Generate a simple product code based on name and ID
        code = f"ITEM_{item.id:03d}"
        
        # Check if code already exists
        if MenuItem.objects.filter(product_code=code).exists():
            code = f"ITEM_{item.id:03d}_{i}"
        
        item.product_code = code
        item.save()
        
        print(f"  {i}. {item.name} → {code}")
    
    print(f"\n✅ Set up product codes for {items_without_codes.count()} items!")
    print("\n📋 Current menu items with codes:")
    print("=" * 50)
    
    for item in MenuItem.objects.all():
        print(f"Code: {item.product_code} | Name: {item.name} | Price: {item.price}")

if __name__ == "__main__":
    setup_product_codes()
