#!/usr/bin/env python3
"""
Test script for the Enhanced Product Creation endpoint
This script tests creating a product with variants using the /products/create-with-variants/ endpoint
"""

import requests
import json
import os
from io import BytesIO
from PIL import Image

# Configuration
BASE_URL = "http://localhost:8000/api/products"
ENDPOINT = f"{BASE_URL}/products/create-with-variants/"

# Test credentials - you may need to adjust these
USERNAME = "admin"  # Replace with your admin username
PASSWORD = "admin"  # Replace with your admin password

def get_auth_token():
    """Get authentication token"""
    auth_url = "http://localhost:8000/api/accounts/login/"
    auth_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(auth_url, json=auth_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'access' in data.get('data', {}):
                return data['data']['access']
            else:
                print(f"❌ Auth failed: {data}")
                return None
        else:
            print(f"❌ Auth request failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_enhanced_product_creation():
    """Test the enhanced product creation endpoint"""
    print("🚀 Testing Enhanced Product Creation Endpoint")
    print("=" * 60)
    
    # Get auth token
    print("🔐 Getting authentication token...")
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token. Please check your credentials.")
        return False
    
    print("✅ Authentication successful")
    
    # Prepare headers
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # Create test images
    print("🖼️ Creating test images...")
    test_icon = create_test_image()
    test_image = create_test_image()
    
    # Prepare form data
    print("📝 Preparing form data...")
    form_data = {
        # Basic product fields
        'name': 'Test Product with Variants',
        'sku': f'TEST-PRODUCT-{os.urandom(4).hex().upper()}',
        'description': 'This is a test product created via the enhanced endpoint',
        'gender': 'unisex',
        'category': '1',  # Adjust category ID as needed
        'selling_price': '99.99',
        'purchasing_price': '49.99',
        'material_and_care': 'Test material and care instructions',
        'is_active': 'true',
        
        # Variant 1 data
        'variants[0][name]': 'Red Variant',
        'variants[0][color]': '#FF0000',
        'variants[0][stock]': '10',
        'variants[0][selling_price]': '99.99',
        'variants[0][is_active]': 'true',
        'variants[0][sizes]': 'S,M,L',
        'variants[0][size_stocks]': json.dumps([
            {'size': 'S', 'stock': 3},
            {'size': 'M', 'stock': 4},
            {'size': 'L', 'stock': 3}
        ]),
        
        # Variant 2 data
        'variants[1][name]': 'Blue Variant',
        'variants[1][color]': '#0000FF',
        'variants[1][stock]': '15',
        'variants[1][selling_price]': '99.99',
        'variants[1][is_active]': 'true',
        'variants[1][sizes]': 'M,L,XL',
        'variants[1][size_stocks]': json.dumps([
            {'size': 'M', 'stock': 5},
            {'size': 'L', 'stock': 5},
            {'size': 'XL', 'stock': 5}
        ]),
    }
    
    # Prepare files
    files = {
        'variants[0][variant_icon]': ('test_icon_1.png', test_icon, 'image/png'),
        'variants[0][variant_picture]': ('test_image_1.png', test_image, 'image/png'),
    }
    
    print("📤 Sending request to enhanced endpoint...")
    print(f"URL: {ENDPOINT}")
    print(f"Form data keys: {list(form_data.keys())}")
    print(f"Files: {list(files.keys())}")
    
    try:
        response = requests.post(
            ENDPOINT,
            data=form_data,
            files=files,
            headers=headers
        )
        
        print(f"\n📨 Response Status: {response.status_code}")
        print(f"📨 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📨 Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📨 Response Text: {response.text}")
        
        if response.status_code == 201:
            print("✅ SUCCESS: Product with variants created successfully!")
            if 'data' in response_data:
                product_data = response_data['data']
                print(f"   Product ID: {product_data.get('id')}")
                print(f"   Product Name: {product_data.get('name')}")
                print(f"   Variants Count: {len(product_data.get('variants', []))}")
                
                # Print variant details
                for i, variant in enumerate(product_data.get('variants', [])):
                    print(f"   Variant {i+1}: {variant.get('name')} (ID: {variant.get('id')})")
                    print(f"     Color: {variant.get('color')}")
                    print(f"     Stock: {variant.get('stock')}")
                    print(f"     Sizes: {len(variant.get('sizes', []))}")
            
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

if __name__ == "__main__":
    success = test_enhanced_product_creation()
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
