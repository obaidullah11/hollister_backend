#!/usr/bin/env python3
"""
Comprehensive test script for Product and Variant Management API
Tests all CRUD operations with all parameters
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

# Test data
TEST_PRODUCT_DATA = {
    "name": "Test Premium T-Shirt",
    "sku": f"TEST-TSHIRT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "description": "High-quality cotton t-shirt with premium finish",
    "gender": "unisex",
    "category": "T-Shirts",
    "selling_price": "29.99",
    "purchasing_price": "15.00",
    "material_and_care": "100% Cotton. Machine wash cold, tumble dry low.",
    "is_active": True,
    "show_on_homepage": True
}

TEST_VARIANT_DATA = [
    {
        "name": "Classic Black",
        "color": "Black",
        "stock": 50,
        "sizes": ["XS", "S", "M", "L", "XL"]
    },
    {
        "name": "Ocean Blue",
        "color": "Blue",
        "stock": 30,
        "sizes": ["S", "M", "L", "XL"]
    },
    {
        "name": "Forest Green",
        "color": "Green",
        "stock": 25,
        "sizes": ["XS", "S", "M", "L"]
    }
]

# Enhanced product data with variants
ENHANCED_PRODUCT_DATA = {
    "name": "Test Enhanced Product",
    "sku": f"TEST-ENHANCED-{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "description": "Enhanced product with multiple variants",
    "gender": "men",
    "category": "Shirts",
    "selling_price": "49.99",
    "purchasing_price": "25.00",
    "material_and_care": "Premium cotton blend",
    "is_active": True,
    "show_on_homepage": False,
    "variants": TEST_VARIANT_DATA
}

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.created_products = []
        self.created_variants = []
        
    def print_separator(self, title):
        print("\n" + "="*80)
        print(f"🧪 {title}")
        print("="*80)
    
    def print_result(self, success, message, data=None):
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {message}")
        if data:
            print(f"Data: {json.dumps(data, indent=2)}")
        print("-" * 40)
    
    def authenticate(self):
        """Try to authenticate with the API"""
        self.print_separator("AUTHENTICATION TEST")
        
        # Try to access a protected endpoint without auth
        response = self.session.get(f"{API_BASE}/products/")
        
        if response.status_code == 401:
            print("🔒 Authentication required. Checking for admin user...")
            
            # Try to create a test admin user
            auth_data = {
                "username": "testadmin",
                "email": "testadmin@example.com",
                "password": "testpass123",
                "is_admin": True
            }
            
            # Try to register
            register_response = self.session.post(f"{API_BASE}/auth/register/", json=auth_data)
            
            if register_response.status_code in [200, 201]:
                print("✅ Test admin user created")
            else:
                print("ℹ️  Test admin user might already exist")
            
            # Try to login
            login_data = {
                "username": "testadmin",
                "password": "testpass123"
            }
            
            login_response = self.session.post(f"{API_BASE}/auth/login/", json=login_data)
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                if 'access' in login_result:
                    self.auth_token = login_result['access']
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}'
                    })
                    self.print_result(True, "Authentication successful")
                    return True
                elif 'token' in login_result:
                    self.auth_token = login_result['token']
                    self.session.headers.update({
                        'Authorization': f'Token {self.auth_token}'
                    })
                    self.print_result(True, "Authentication successful")
                    return True
            
            self.print_result(False, f"Authentication failed: {login_response.text}")
            return False
        
        elif response.status_code == 200:
            self.print_result(True, "No authentication required")
            return True
        
        else:
            self.print_result(False, f"Unexpected response: {response.status_code}")
            return False
    
    def test_product_list(self):
        """Test product listing"""
        self.print_separator("PRODUCT LIST TEST")
        
        response = self.session.get(f"{API_BASE}/products/")
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('data', data) if isinstance(data, dict) else data
            self.print_result(True, f"Retrieved {len(products)} products")
            return True
        else:
            self.print_result(False, f"Failed to retrieve products: {response.text}")
            return False
    
    def test_product_create(self):
        """Test product creation"""
        self.print_separator("PRODUCT CREATE TEST")
        
        response = self.session.post(f"{API_BASE}/products/create/", json=TEST_PRODUCT_DATA)
        
        if response.status_code in [200, 201]:
            data = response.json()
            product_data = data.get('data', data)
            product_id = product_data.get('id')
            
            if product_id:
                self.created_products.append(product_id)
                self.print_result(True, f"Product created with ID: {product_id}", product_data)
                return product_id
            else:
                self.print_result(False, "Product created but no ID returned", data)
                return None
        else:
            self.print_result(False, f"Failed to create product: {response.text}")
            return None
    
    def test_enhanced_product_create(self):
        """Test enhanced product creation with variants"""
        self.print_separator("ENHANCED PRODUCT CREATE TEST")
        
        response = self.session.post(f"{API_BASE}/products/create-with-variants/", json=ENHANCED_PRODUCT_DATA)
        
        if response.status_code in [200, 201]:
            data = response.json()
            product_data = data.get('data', data)
            product_id = product_data.get('id')
            
            if product_id:
                self.created_products.append(product_id)
                variants = product_data.get('variants', [])
                self.print_result(True, f"Enhanced product created with ID: {product_id}, Variants: {len(variants)}", product_data)
                return product_id
            else:
                self.print_result(False, "Enhanced product created but no ID returned", data)
                return None
        else:
            self.print_result(False, f"Failed to create enhanced product: {response.text}")
            return None
    
    def test_product_detail(self, product_id):
        """Test product detail retrieval"""
        self.print_separator(f"PRODUCT DETAIL TEST (ID: {product_id})")
        
        response = self.session.get(f"{API_BASE}/products/{product_id}/")
        
        if response.status_code == 200:
            data = response.json()
            product_data = data.get('data', data)
            variants = product_data.get('variants', [])
            self.print_result(True, f"Retrieved product details with {len(variants)} variants", product_data)
            return True
        else:
            self.print_result(False, f"Failed to retrieve product details: {response.text}")
            return False
    
    def test_product_update(self, product_id):
        """Test product update"""
        self.print_separator(f"PRODUCT UPDATE TEST (ID: {product_id})")
        
        update_data = {
            "name": "Updated Test Product",
            "selling_price": "39.99",
            "description": "Updated description with new features"
        }
        
        response = self.session.patch(f"{API_BASE}/products/{product_id}/", json=update_data)
        
        if response.status_code == 200:
            data = response.json()
            product_data = data.get('data', data)
            self.print_result(True, "Product updated successfully", product_data)
            return True
        else:
            self.print_result(False, f"Failed to update product: {response.text}")
            return False
    
    def test_variant_create(self, product_id):
        """Test variant creation"""
        self.print_separator(f"VARIANT CREATE TEST (Product ID: {product_id})")
        
        variant_data = {
            "name": "Ruby Red",
            "color": "Red",
            "stock": 20,
            "sizes": ["S", "M", "L"]
        }
        
        response = self.session.post(f"{API_BASE}/products/{product_id}/variants/", json=variant_data)
        
        if response.status_code in [200, 201]:
            data = response.json()
            variant_data = data.get('data', data)
            variant_id = variant_data.get('id')
            
            if variant_id:
                self.created_variants.append(variant_id)
                self.print_result(True, f"Variant created with ID: {variant_id}", variant_data)
                return variant_id
            else:
                self.print_result(False, "Variant created but no ID returned", data)
                return None
        else:
            self.print_result(False, f"Failed to create variant: {response.text}")
            return None
    
    def test_variant_update(self, product_id, variant_id):
        """Test variant update"""
        self.print_separator(f"VARIANT UPDATE TEST (ID: {variant_id})")
        
        update_data = {
            "name": "Updated Ruby Red",
            "stock": 35,
            "color": "Dark Red"
        }
        
        response = self.session.patch(f"{API_BASE}/products/{product_id}/variants/{variant_id}/", json=update_data)
        
        if response.status_code == 200:
            data = response.json()
            variant_data = data.get('data', data)
            self.print_result(True, "Variant updated successfully", variant_data)
            return True
        else:
            self.print_result(False, f"Failed to update variant: {response.text}")
            return False
    
    def test_bulk_stock_update(self):
        """Test bulk stock update"""
        if not self.created_variants:
            print("⚠️  No variants to test bulk update")
            return False
            
        self.print_separator("BULK STOCK UPDATE TEST")
        
        bulk_data = {
            "variants": [
                {"id": variant_id, "stock": 100}
                for variant_id in self.created_variants[:2]  # Update first 2 variants
            ]
        }
        
        response = self.session.post(f"{API_BASE}/admin/bulk-update-stock/", json=bulk_data)
        
        if response.status_code == 200:
            data = response.json()
            updated_variants = data.get('data', [])
            self.print_result(True, f"Bulk updated {len(updated_variants)} variants", data)
            return True
        else:
            self.print_result(False, f"Failed to bulk update stock: {response.text}")
            return False
    
    def test_product_stats(self):
        """Test product statistics"""
        self.print_separator("PRODUCT STATS TEST")
        
        response = self.session.get(f"{API_BASE}/admin/product-stats/")
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('data', data)
            self.print_result(True, "Retrieved product statistics", stats)
            return True
        else:
            self.print_result(False, f"Failed to retrieve product stats: {response.text}")
            return False
    
    def test_category_stats(self):
        """Test category statistics"""
        self.print_separator("CATEGORY STATS TEST")
        
        response = self.session.get(f"{API_BASE}/admin/category-stats/")
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('data', data)
            self.print_result(True, "Retrieved category statistics", stats)
            return True
        else:
            self.print_result(False, f"Failed to retrieve category stats: {response.text}")
            return False
    
    def test_categories(self):
        """Test category management"""
        self.print_separator("CATEGORY MANAGEMENT TEST")
        
        # List categories
        response = self.session.get(f"{API_BASE}/categories/")
        if response.status_code == 200:
            data = response.json()
            categories = data.get('data', data)
            self.print_result(True, f"Retrieved {len(categories)} categories")
        else:
            self.print_result(False, f"Failed to retrieve categories: {response.text}")
            return False
        
        # Create category
        category_data = {
            "name": f"Test Category {datetime.now().strftime('%H%M%S')}",
            "description": "Test category for API testing",
            "is_active": True
        }
        
        response = self.session.post(f"{API_BASE}/categories/", json=category_data)
        if response.status_code in [200, 201]:
            data = response.json()
            category = data.get('data', data)
            category_id = category.get('id')
            self.print_result(True, f"Category created with ID: {category_id}", category)
            return category_id
        else:
            self.print_result(False, f"Failed to create category: {response.text}")
            return None
    
    def cleanup(self):
        """Clean up created test data"""
        self.print_separator("CLEANUP")
        
        # Delete created products (this will also delete variants)
        for product_id in self.created_products:
            response = self.session.delete(f"{API_BASE}/products/{product_id}/")
            if response.status_code in [200, 204]:
                print(f"✅ Deleted product {product_id}")
            else:
                print(f"⚠️  Failed to delete product {product_id}: {response.text}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting comprehensive Product and Variant Management API tests...")
        
        # Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Test product operations
        self.test_product_list()
        
        # Test basic product creation
        product_id = self.test_product_create()
        if product_id:
            self.test_product_detail(product_id)
            self.test_product_update(product_id)
            
            # Test variant operations
            variant_id = self.test_variant_create(product_id)
            if variant_id:
                self.test_variant_update(product_id, variant_id)
        
        # Test enhanced product creation
        enhanced_product_id = self.test_enhanced_product_create()
        if enhanced_product_id:
            self.test_product_detail(enhanced_product_id)
        
        # Test admin operations
        self.test_bulk_stock_update()
        self.test_product_stats()
        self.test_category_stats()
        
        # Test category management
        self.test_categories()
        
        # Cleanup
        self.cleanup()
        
        print("\n🎉 All tests completed!")
        return True

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
