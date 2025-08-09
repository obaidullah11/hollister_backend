import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'holister_backend.settings')
django.setup()

from products.models import Product, ProductVariant, ProductSize
from orders.models import Order, OrderItem

def check_data():
    print("=== PRODUCTS ===")
    products = Product.objects.all()
    for product in products:
        print(f"Product: {product.id} - {product.name} - {product.sku}")
        variants = ProductVariant.objects.filter(product=product)
        print(f"  Variants count: {variants.count()}")
        for variant in variants:
            print(f"    Variant: {variant.id} - {variant.name} - {variant.color}")
            sizes = ProductSize.objects.filter(variant=variant)
            print(f"      Sizes count: {sizes.count()}")
            for size in sizes:
                print(f"        Size: {size.size} - Stock: {size.stock}")
        print()
    
    print("=== ORDERS ===")
    orders = Order.objects.all()
    for order in orders:
        print(f"Order: {order.order_number} - Status: {order.status}")
        items = OrderItem.objects.filter(order=order)
        print(f"  Items count: {items.count()}")
        for item in items:
            print(f"    Item: {item.product.name} - {item.variant.name} - {item.size.size}")
        print()

if __name__ == "__main__":
    check_data()
