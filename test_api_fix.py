import os
import django
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'holister_backend.settings')
django.setup()

from products.models import Product, Category, ProductVariant
from django.contrib.auth import get_user_model

User = get_user_model()

# Check categories
print("=== Available Categories ===")
categories = Category.objects.all()
for cat in categories:
    print(f"ID: {cat.id}, Name: {cat.name}, Display: {cat.display_name}")

# Check products
print("\n=== Current Products ===")
products = Product.objects.all()
for product in products:
    print(f"\nProduct: {product.name}")
    print(f"  SKU: {product.sku}")
    if hasattr(product, 'category_id'):
        print(f"  Category ID: {product.category_id}")
    try:
        print(f"  Category: {product.category.display_name if product.category else 'None'}")
    except Exception as e:
        print(f"  Category Error: {e}")
    print(f"  Variants: {product.variants.count()}")

# Check for any products without categories
print("\n=== Products without Categories ===")
products_no_cat = Product.objects.filter(category__isnull=True)
print(f"Count: {products_no_cat.count()}")
for p in products_no_cat:
    print(f"  - {p.name} (ID: {p.id})")





