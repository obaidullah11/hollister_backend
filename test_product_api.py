import requests
import json

# Base URL for your API
BASE_URL = "http://localhost:8000/api"

def create_product_with_variants():
    """Test creating a product with variants using the API"""
    
    print("=== Creating Product with Variants ===")
    
    # Sample product data with variants
    product_data = {
        "name": "Premium Cotton T-Shirt",
        "sku": "TSHIRT-002",
        "description": "High-quality cotton t-shirt with multiple color options",
        "gender": "unisex",
        "category": "T-Shirts",
        "selling_price": "39.99",
        "purchasing_price": "18.00",
        "material_and_care": "100% Premium Cotton. Machine wash cold.",
        "variants_data": [
            {
                "name": "Classic White",
                "color": "White",
                "stock": 75,
                "sizes": ["XS", "S", "M", "L", "XL"]
            },
            {
                "name": "Navy Blue",
                "color": "Navy",
                "stock": 60,
                "sizes": ["S", "M", "L", "XL"]
            }
        ]
    }
    
    print("Product data to send:")
    print(json.dumps(product_data, indent=2))
    
    print("\n⚠️  NOTE: This method doesn't support images in variants_data")
    print("   Images must be added separately after variant creation")

def show_api_structure():
    """Show the API structure and how variants work"""
    
    print("\n=== API Structure ===")
    print("1. Create Product: POST /api/products/products/create/")
    print("   - Include variants_data array for variants")
    print("   - Each variant can have sizes array")
    print("   - ❌ Images NOT supported in this method")
    
    print("\n2. List Products: GET /api/products/products/")
    print("   - Returns products with variants array")
    print("   - Each variant includes sizes array")
    print("   - ✅ Images are included if they exist")
    
    print("\n3. Product Detail: GET /api/products/products/{id}/")
    print("   - Returns single product with all variants and sizes")
    
    print("\n4. Create Variant: POST /api/products/products/{product_id}/variants/")
    print("   - Add variants to existing products")
    print("   - ✅ Supports images (variant_icon, variant_picture)")
    
    print("\n5. Update Variant: PUT/PATCH /api/products/products/{product_id}/variants/{variant_id}/")
    print("   - Update existing variants including images")
    
    print("\n=== Variant Structure ===")
    print("Each variant includes:")
    print("- name: Variant name (e.g., 'Blue Denim')")
    print("- color: Color description")
    print("- stock: Total stock for this variant")
    print("- sizes: Array of size strings")
    print("- variant_icon: Optional icon image (URL)")
    print("- variant_picture: Optional variant image (URL)")

def show_image_handling():
    """Show how to handle images for variants"""
    
    print("\n=== Image Handling ===")
    print("❌ Current Limitation:")
    print("   - variants_data in product creation doesn't support file uploads")
    print("   - Images must be added separately")
    
    print("\n✅ Solutions:")
    print("1. Create product first, then add variants with images:")
    print("   POST /api/products/products/{product_id}/variants/")
    print("   - Use multipart/form-data")
    print("   - Include variant_icon and variant_picture files")
    
    print("\n2. Update existing variants with images:")
    print("   PUT/PATCH /api/products/products/{product_id}/variants/{variant_id}/")
    print("   - Use multipart/form-data")
    print("   - Include variant_icon and variant_picture files")
    
    print("\n3. Example multipart request:")
    print("   Content-Type: multipart/form-data")
    print("   Fields:")
    print("     - name: 'Classic White'")
    print("     - color: 'White'")
    print("     - stock: 75")
    print("     - variant_icon: [icon file]")
    print("     - variant_picture: [picture file]")
    print("     - sizes: ['XS', 'S', 'M', 'L', 'XL']")

def show_enhanced_api_usage():
    """Show enhanced API usage with images"""
    
    print("\n=== Enhanced API Usage ===")
    print("Step 1: Create product without variants")
    print("POST /api/products/products/create/")
    print("Body: {name, sku, description, gender, category, selling_price, ...}")
    
    print("\nStep 2: Add variants with images")
    print("POST /api/products/products/{product_id}/variants/")
    print("Body: multipart/form-data with files")
    
    print("\nStep 3: Add sizes to variants")
    print("The variant creation automatically handles sizes")
    
    print("\nStep 4: View product with complete data")
    print("GET /api/products/products/{product_id}/")
    print("Response will include:")
    print("  - Product details")
    print("  - Variants with images")
    print("  - Sizes for each variant")

if __name__ == "__main__":
    create_product_with_variants()
    show_api_structure()
    show_image_handling()
    show_enhanced_api_usage()
