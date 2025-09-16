#!/usr/bin/env python
"""
Script to check for SKU conflicts in the database
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'holister_backend.settings')
django.setup()

from products.models import Product

def check_sku_conflicts():
    """Check for existing SKUs and potential conflicts"""
    print("=== SKU Conflict Analysis ===")
    print()
    
    # Get all products
    products = Product.objects.all()
    print(f"Total products in database: {products.count()}")
    print()
    
    if products.exists():
        print("Existing products and their SKUs:")
        print("-" * 50)
        for product in products:
            print(f"ID: {product.id:3d} | SKU: {product.sku:20s} | Name: {product.name}")
        print()
        
        # Check for duplicate SKUs (shouldn't happen due to unique constraint)
        skus = [p.sku for p in products]
        duplicate_skus = [sku for sku in set(skus) if skus.count(sku) > 1]
        
        if duplicate_skus:
            print("⚠️  DUPLICATE SKUs FOUND:")
            for sku in duplicate_skus:
                print(f"  - {sku}")
        else:
            print("✅ No duplicate SKUs found")
        
        print()
        print("Recent products (last 5):")
        print("-" * 30)
        recent_products = products.order_by('-created_at')[:5]
        for product in recent_products:
            print(f"  {product.sku} - {product.name} (Created: {product.created_at.strftime('%Y-%m-%d %H:%M')})")
    else:
        print("No products found in database")
    
    print()
    print("=== End Analysis ===")

if __name__ == "__main__":
    check_sku_conflicts()
