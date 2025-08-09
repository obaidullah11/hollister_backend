from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import User
from products.models import Product, ProductVariant, ProductSize
from orders.models import Order, OrderItem, ShippingAddress, OrderStatusHistory
from decimal import Decimal
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up initial data for the Holister Admin Panel'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create sample admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@holister.com',
            defaults={
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user: admin@holister.com (password: admin123)')
        else:
            self.stdout.write('Admin user already exists')
        
        # Create sample customer users
        customers = [
            {
                'email': 'john@example.com',
                'username': 'john_doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': User.Role.CUSTOMER,
                'phone_number': '+1234567890',
                'address': '123 Main St, New York, NY 10001'
            },
            {
                'email': 'sarah@example.com',
                'username': 'sarah_johnson',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': User.Role.CUSTOMER,
                'phone_number': '+1234567891',
                'address': '456 Oak Ave, Los Angeles, CA 90210'
            },
            {
                'email': 'mike@example.com',
                'username': 'mike_wilson',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'role': User.Role.CUSTOMER,
                'phone_number': '+1234567892',
                'address': '789 Pine Rd, Chicago, IL 60601'
            }
        ]
        
        created_customers = []
        for customer_data in customers:
            customer, created = User.objects.get_or_create(
                email=customer_data['email'],
                defaults=customer_data
            )
            if created:
                customer.set_password('customer123')
                customer.save()
                created_customers.append(customer)
                self.stdout.write(f'Created customer: {customer_data["email"]} (password: customer123)')
            else:
                created_customers.append(customer)
                self.stdout.write(f'Customer already exists: {customer_data["email"]}')
        
        # Create sample products
        products_data = [
            {
                'name': 'Classic Denim Jeans',
                'sku': 'JEAN-001',
                'description': 'Comfortable classic denim jeans with perfect fit',
                'gender': Product.Gender.UNISEX,
                'category': 'Jeans',
                'selling_price': Decimal('89.99'),
                'purchasing_price': Decimal('45.00'),
                'material_and_care': '100% Cotton denim. Machine wash cold, tumble dry low.'
            },
            {
                'name': 'Cotton T-Shirt',
                'sku': 'TSHIRT-001',
                'description': 'Soft cotton t-shirt for everyday wear',
                'gender': Product.Gender.UNISEX,
                'category': 'T-Shirts',
                'selling_price': Decimal('29.99'),
                'purchasing_price': Decimal('12.00'),
                'material_and_care': '100% Cotton. Machine wash cold, tumble dry low.'
            },
            {
                'name': 'Casual Shirt',
                'sku': 'SHIRT-001',
                'description': 'Elegant casual shirt for any occasion',
                'gender': Product.Gender.MEN,
                'category': 'Shirts',
                'selling_price': Decimal('59.99'),
                'purchasing_price': Decimal('25.00'),
                'material_and_care': 'Cotton blend. Dry clean recommended.'
            },
            {
                'name': 'Summer Dress',
                'sku': 'DRESS-001',
                'description': 'Beautiful summer dress with floral pattern',
                'gender': Product.Gender.WOMEN,
                'category': 'Dresses',
                'selling_price': Decimal('79.99'),
                'purchasing_price': Decimal('35.00'),
                'material_and_care': 'Polyester blend. Hand wash cold, line dry.'
            }
        ]
        
        created_products = []
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults=product_data
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')
            else:
                self.stdout.write(f'Product already exists: {product.name}')
            created_products.append(product)
        
        # Create sample variants for products
        variants_data = [
            # Jeans variants
            {
                'product': created_products[0],  # Classic Denim Jeans
                'name': 'Blue Denim',
                'color': 'Blue',
                'stock': 50
            },
            {
                'product': created_products[0],
                'name': 'Black Denim',
                'color': 'Black',
                'stock': 30
            },
            # T-Shirt variants
            {
                'product': created_products[1],  # Cotton T-Shirt
                'name': 'White',
                'color': 'White',
                'stock': 100
            },
            {
                'product': created_products[1],
                'name': 'Black',
                'color': 'Black',
                'stock': 80
            },
            {
                'product': created_products[1],
                'name': 'Gray',
                'color': 'Gray',
                'stock': 60
            },
            # Shirt variants
            {
                'product': created_products[2],  # Casual Shirt
                'name': 'White',
                'color': 'White',
                'stock': 40
            },
            {
                'product': created_products[2],
                'name': 'Blue',
                'color': 'Blue',
                'stock': 35
            },
            # Dress variants
            {
                'product': created_products[3],  # Summer Dress
                'name': 'Floral Blue',
                'color': 'Blue Floral',
                'stock': 25
            },
            {
                'product': created_products[3],
                'name': 'Floral Pink',
                'color': 'Pink Floral',
                'stock': 20
            }
        ]
        
        created_variants = []
        for variant_data in variants_data:
            variant, created = ProductVariant.objects.get_or_create(
                product=variant_data['product'],
                name=variant_data['name'],
                defaults={
                    'color': variant_data['color'],
                    'stock': variant_data['stock']
                }
            )
            if created:
                self.stdout.write(f'Created variant: {variant.product.name} - {variant.name}')
            else:
                self.stdout.write(f'Variant already exists: {variant.product.name} - {variant.name}')
            created_variants.append(variant)
        
        # Create sample sizes for variants
        sizes_data = [
            # Jeans sizes
            {'variant': created_variants[0], 'size': '30', 'stock': 10},
            {'variant': created_variants[0], 'size': '32', 'stock': 15},
            {'variant': created_variants[0], 'size': '34', 'stock': 12},
            {'variant': created_variants[0], 'size': '36', 'stock': 8},
            {'variant': created_variants[1], 'size': '30', 'stock': 8},
            {'variant': created_variants[1], 'size': '32', 'stock': 12},
            {'variant': created_variants[1], 'size': '34', 'stock': 10},
            # T-Shirt sizes
            {'variant': created_variants[2], 'size': 'S', 'stock': 25},
            {'variant': created_variants[2], 'size': 'M', 'stock': 30},
            {'variant': created_variants[2], 'size': 'L', 'stock': 25},
            {'variant': created_variants[2], 'size': 'XL', 'stock': 20},
            {'variant': created_variants[3], 'size': 'S', 'stock': 20},
            {'variant': created_variants[3], 'size': 'M', 'stock': 25},
            {'variant': created_variants[3], 'size': 'L', 'stock': 20},
            {'variant': created_variants[3], 'size': 'XL', 'stock': 15},
            {'variant': created_variants[4], 'size': 'S', 'stock': 15},
            {'variant': created_variants[4], 'size': 'M', 'stock': 20},
            {'variant': created_variants[4], 'size': 'L', 'stock': 15},
            {'variant': created_variants[4], 'size': 'XL', 'stock': 10},
            # Shirt sizes
            {'variant': created_variants[5], 'size': 'S', 'stock': 10},
            {'variant': created_variants[5], 'size': 'M', 'stock': 15},
            {'variant': created_variants[5], 'size': 'L', 'stock': 10},
            {'variant': created_variants[5], 'size': 'XL', 'stock': 5},
            {'variant': created_variants[6], 'size': 'S', 'stock': 8},
            {'variant': created_variants[6], 'size': 'M', 'stock': 12},
            {'variant': created_variants[6], 'size': 'L', 'stock': 10},
            {'variant': created_variants[6], 'size': 'XL', 'stock': 5},
            # Dress sizes
            {'variant': created_variants[7], 'size': 'XS', 'stock': 5},
            {'variant': created_variants[7], 'size': 'S', 'stock': 8},
            {'variant': created_variants[7], 'size': 'M', 'stock': 7},
            {'variant': created_variants[7], 'size': 'L', 'stock': 5},
            {'variant': created_variants[8], 'size': 'XS', 'stock': 4},
            {'variant': created_variants[8], 'size': 'S', 'stock': 6},
            {'variant': created_variants[8], 'size': 'M', 'stock': 5},
            {'variant': created_variants[8], 'size': 'L', 'stock': 5}
        ]
        
        for size_data in sizes_data:
            size, created = ProductSize.objects.get_or_create(
                variant=size_data['variant'],
                size=size_data['size'],
                defaults={'stock': size_data['stock']}
            )
            if created:
                self.stdout.write(f'Created size: {size.variant.product.name} - {size.variant.name} - {size.size}')
            else:
                self.stdout.write(f'Size already exists: {size.variant.product.name} - {size.variant.name} - {size.size}')
        
        # Create sample shipping addresses
        shipping_addresses = []
        for i, customer in enumerate(created_customers):
            address_data = [
                {
                    'user': customer,
                    'address_line_1': f'{100 + i} Main Street',
                    'address_line_2': f'Apt {i + 1}',
                    'city': 'New York',
                    'state': 'NY',
                    'postal_code': f'1000{i + 1}',
                    'country': 'United States',
                    'is_default': True
                },
                {
                    'user': customer,
                    'address_line_1': f'{200 + i} Oak Avenue',
                    'address_line_2': '',
                    'city': 'Los Angeles',
                    'state': 'CA',
                    'postal_code': f'9021{i}',
                    'country': 'United States',
                    'is_default': False
                }
            ]
            
            for addr_data in address_data:
                address, created = ShippingAddress.objects.get_or_create(
                    user=addr_data['user'],
                    address_line_1=addr_data['address_line_1'],
                    city=addr_data['city'],
                    defaults=addr_data
                )
                if created:
                    self.stdout.write(f'Created shipping address for {customer.email}')
                else:
                    self.stdout.write(f'Shipping address already exists for {customer.email}')
                shipping_addresses.append(address)
        
        # Create sample orders
        orders_data = [
            {
                'customer': created_customers[0],
                'order_number': f'ORD-{uuid.uuid4().hex[:8].upper()}',
                'status': Order.Status.PENDING,
                'total_amount': Decimal('119.98'),
                'email': created_customers[0].email,
                'phone_number': created_customers[0].phone_number,
                'shipping_address': shipping_addresses[0],
                'billing_address': shipping_addresses[0],
                'notes': 'Please deliver in the morning'
            },
            {
                'customer': created_customers[1],
                'order_number': f'ORD-{uuid.uuid4().hex[:8].upper()}',
                'status': Order.Status.CONFIRMED,
                'total_amount': Decimal('89.99'),
                'email': created_customers[1].email,
                'phone_number': created_customers[1].phone_number,
                'shipping_address': shipping_addresses[2],
                'billing_address': shipping_addresses[2],
                'notes': 'Gift wrapping requested'
            },
            {
                'customer': created_customers[2],
                'order_number': f'ORD-{uuid.uuid4().hex[:8].upper()}',
                'status': Order.Status.SHIPPED,
                'total_amount': Decimal('159.98'),
                'email': created_customers[2].email,
                'phone_number': created_customers[2].phone_number,
                'shipping_address': shipping_addresses[4],
                'billing_address': shipping_addresses[4],
                'notes': 'Express shipping preferred'
            }
        ]
        
        created_orders = []
        for order_data in orders_data:
            order, created = Order.objects.get_or_create(
                order_number=order_data['order_number'],
                defaults=order_data
            )
            if created:
                self.stdout.write(f'Created order: {order.order_number}')
            else:
                self.stdout.write(f'Order already exists: {order.order_number}')
            created_orders.append(order)
        
        # Create sample order items
        order_items_data = [
            # Order 1 items
            {
                'order': created_orders[0],
                'product': created_products[0],  # Jeans
                'variant': created_variants[0],  # Blue Denim
                'size': ProductSize.objects.get(variant=created_variants[0], size='32'),
                'quantity': 1,
                'unit_price': Decimal('89.99'),
                'total_price': Decimal('89.99')
            },
            {
                'order': created_orders[0],
                'product': created_products[1],  # T-Shirt
                'variant': created_variants[2],  # White
                'size': ProductSize.objects.get(variant=created_variants[2], size='M'),
                'quantity': 1,
                'unit_price': Decimal('29.99'),
                'total_price': Decimal('29.99')
            },
            # Order 2 items
            {
                'order': created_orders[1],
                'product': created_products[0],  # Jeans
                'variant': created_variants[1],  # Black Denim
                'size': ProductSize.objects.get(variant=created_variants[1], size='34'),
                'quantity': 1,
                'unit_price': Decimal('89.99'),
                'total_price': Decimal('89.99')
            },
            # Order 3 items
            {
                'order': created_orders[2],
                'product': created_products[2],  # Shirt
                'variant': created_variants[5],  # White
                'size': ProductSize.objects.get(variant=created_variants[5], size='L'),
                'quantity': 1,
                'unit_price': Decimal('59.99'),
                'total_price': Decimal('59.99')
            },
            {
                'order': created_orders[2],
                'product': created_products[3],  # Dress
                'variant': created_variants[7],  # Floral Blue
                'size': ProductSize.objects.get(variant=created_variants[7], size='M'),
                'quantity': 1,
                'unit_price': Decimal('79.99'),
                'total_price': Decimal('79.99')
            },
            {
                'order': created_orders[2],
                'product': created_products[1],  # T-Shirt
                'variant': created_variants[3],  # Black
                'size': ProductSize.objects.get(variant=created_variants[3], size='S'),
                'quantity': 1,
                'unit_price': Decimal('29.99'),
                'total_price': Decimal('29.99')
            }
        ]
        
        for item_data in order_items_data:
            item, created = OrderItem.objects.get_or_create(
                order=item_data['order'],
                product=item_data['product'],
                variant=item_data['variant'],
                size=item_data['size'],
                defaults={
                    'quantity': item_data['quantity'],
                    'unit_price': item_data['unit_price'],
                    'total_price': item_data['total_price']
                }
            )
            if created:
                self.stdout.write(f'Created order item: {item.product.name} - {item.variant.name} - {item.size.size}')
            else:
                self.stdout.write(f'Order item already exists: {item.product.name} - {item.variant.name} - {item.size.size}')
        
        # Create sample order status history
        status_history_data = [
            {
                'order': created_orders[0],
                'status': Order.Status.PENDING,
                'notes': 'Order placed successfully',
                'created_by': admin_user
            },
            {
                'order': created_orders[1],
                'status': Order.Status.PENDING,
                'notes': 'Order placed successfully',
                'created_by': admin_user
            },
            {
                'order': created_orders[1],
                'status': Order.Status.CONFIRMED,
                'notes': 'Payment confirmed, preparing for processing',
                'created_by': admin_user
            },
            {
                'order': created_orders[2],
                'status': Order.Status.PENDING,
                'notes': 'Order placed successfully',
                'created_by': admin_user
            },
            {
                'order': created_orders[2],
                'status': Order.Status.CONFIRMED,
                'notes': 'Payment confirmed, preparing for processing',
                'created_by': admin_user
            },
            {
                'order': created_orders[2],
                'status': Order.Status.PROCESSING,
                'notes': 'Order is being processed and packed',
                'created_by': admin_user
            },
            {
                'order': created_orders[2],
                'status': Order.Status.SHIPPED,
                'notes': 'Order has been shipped via express delivery',
                'created_by': admin_user
            }
        ]
        
        for history_data in status_history_data:
            history, created = OrderStatusHistory.objects.get_or_create(
                order=history_data['order'],
                status=history_data['status'],
                created_by=history_data['created_by'],
                defaults={'notes': history_data['notes']}
            )
            if created:
                self.stdout.write(f'Created status history: {history.order.order_number} - {history.status}')
            else:
                self.stdout.write(f'Status history already exists: {history.order.order_number} - {history.status}')
        
        self.stdout.write(self.style.SUCCESS('Initial data setup completed successfully!'))
        self.stdout.write('\nSample Data Summary:')
        self.stdout.write(f'- {User.objects.count()} users (1 admin, {User.objects.filter(role=User.Role.CUSTOMER).count()} customers)')
        self.stdout.write(f'- {Product.objects.count()} products')
        self.stdout.write(f'- {ProductVariant.objects.count()} product variants')
        self.stdout.write(f'- {ProductSize.objects.count()} product sizes')
        self.stdout.write(f'- {ShippingAddress.objects.count()} shipping addresses')
        self.stdout.write(f'- {Order.objects.count()} orders')
        self.stdout.write(f'- {OrderItem.objects.count()} order items')
        self.stdout.write(f'- {OrderStatusHistory.objects.count()} status history entries')
