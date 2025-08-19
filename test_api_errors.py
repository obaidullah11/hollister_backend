import requests
import json

# Base URL
BASE_URL = "http://localhost:8000/api"

# Test credentials
TEST_EMAIL = "admin@holister.com"
TEST_PASSWORD = "admin123"

def get_auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/accounts/login/", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        return data.get('data', {}).get('access')
    else:
        print(f"Login failed: {response.status_code}")
        print(response.json())
        return None

def test_products_api(token):
    """Test products API"""
    print("\n=== Testing Products API ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test GET products
    print("\n1. GET /products/products/")
    response = requests.get(f"{BASE_URL}/products/products/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        data = response.json()
        print(f"Success: Found {len(data.get('data', []))} products")

def test_categories_api(token):
    """Test categories API"""
    print("\n=== Testing Categories API ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test GET categories
    print("\n1. GET /products/categories/")
    response = requests.get(f"{BASE_URL}/products/categories/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        data = response.json()
        categories = data.get('data', [])
        print(f"Success: Found {len(categories)} categories")
        for cat in categories[:3]:  # Show first 3
            print(f"  - ID: {cat['id']}, Name: {cat['display_name']}")

def test_orders_api(token):
    """Test orders API"""
    print("\n=== Testing Orders API ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test GET orders
    print("\n1. GET /orders/orders/")
    response = requests.get(f"{BASE_URL}/orders/orders/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        data = response.json()
        print(f"Success: Found {len(data.get('data', []))} orders")

def test_product_creation(token):
    """Test creating a product with new category system"""
    print("\n=== Testing Product Creation ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # First get a category ID
    response = requests.get(f"{BASE_URL}/products/categories/", headers=headers)
    if response.status_code == 200:
        categories = response.json().get('data', [])
        if categories:
            category_id = categories[0]['id']
            print(f"Using category ID: {category_id} ({categories[0]['display_name']})")
            
            # Create product
            product_data = {
                "name": "Test Product API",
                "sku": "TEST-API-001",
                "description": "Testing product creation with category ID",
                "gender": "unisex",
                "category": category_id,  # Use ID instead of string
                "selling_price": "29.99",
                "purchasing_price": "15.00",
                "material_and_care": "Test material",
                "is_active": True,
                "show_on_homepage": False
            }
            
            print("\n2. POST /products/products/")
            response = requests.post(f"{BASE_URL}/products/products/", headers=headers, json=product_data)
            print(f"Status: {response.status_code}")
            if response.status_code not in [200, 201]:
                print(f"Error: {response.text}")
            else:
                print("Success: Product created")
                print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    # Get auth token
    token = get_auth_token()
    
    if token:
        print(f"Authenticated successfully. Token: {token[:20]}...")
        
        # Run tests
        test_products_api(token)
        test_categories_api(token)
        test_orders_api(token)
        test_product_creation(token)
    else:
        print("Failed to authenticate. Please check credentials.")
