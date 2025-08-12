#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'holister_backend.settings')
django.setup()

from accounts.models import User
from products.models import Product, ProductVariant, ProductSize
from django.contrib.auth.hashers import make_password

def create_test_data():
    print("Creating test data...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email='mike@example.com',
        defaults={
            'username': 'mike@example.com',
            'first_name': 'Mike',
            'last_name': 'Test',
            'role': 'customer',
            'is_active': True
        }
    )
    
    if created:
        user.password = make_password('testpass123')
        user.save()
        print(f"Created user: {user.email}")
    else:
        print(f"User already exists: {user.email}")
    
    # Create test products
    products_data = [
        {
            'name': 'Classic White T-Shirt',
            'sku': 'TSHIRT-001',
            'description': 'Premium cotton classic white t-shirt',
            'selling_price': '29.99',
            'purchasing_price': '15.00',
            'category': 'T-Shirts',
            'gender': 'unisex'
        },
        {
            'name': 'Blue Denim Jeans',
            'sku': 'JEANS-001',
            'description': 'Comfortable blue denim jeans',
            'selling_price': '79.99',
            'purchasing_price': '40.00',
            'category': 'Jeans',
            'gender': 'unisex'
        },
        {
            'name': 'Hooded Sweatshirt',
            'sku': 'HOODIE-001',
            'description': 'Warm and comfortable hooded sweatshirt',
            'selling_price': '59.99',
            'purchasing_price': '25.00',
            'category': 'Hoodies',
            'gender': 'unisex'
        }
    ]
    
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            sku=product_data['sku'],
            defaults=product_data
        )
        
        if created:
            print(f"Created product: {product.name}")
            
            # Add variants for the first product
            if product.sku == 'TSHIRT-001':
                variants_data = [
                    {'name': 'White', 'color': '#FFFFFF', 'stock_quantity': 20},
                    {'name': 'Black', 'color': '#000000', 'stock_quantity': 15},
                    {'name': 'Gray', 'color': '#808080', 'stock_quantity': 15}
                ]
                
                for variant_data in variants_data:
                    variant, v_created = ProductVariant.objects.get_or_create(
                        product=product,
                        name=variant_data['name'],
                        defaults=variant_data
                    )
                    if v_created:
                        print(f"  - Created variant: {variant.name}")
                
                # Add sizes
                sizes_data = [
                    {'name': 'S', 'stock_quantity': 10},
                    {'name': 'M', 'stock_quantity': 15},
                    {'name': 'L', 'stock_quantity': 15},
                    {'name': 'XL', 'stock_quantity': 10}
                ]
                
                for size_data in sizes_data:
                    size, s_created = ProductSize.objects.get_or_create(
                        product=product,
                        name=size_data['name'],
                        defaults=size_data
                    )
                    if s_created:
                        print(f"  - Created size: {size.name}")
        else:
            print(f"Product already exists: {product.name}")
    
    print("Test data setup complete!")

if __name__ == '__main__':
    create_test_data()
