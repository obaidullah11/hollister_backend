from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from coupons.models import Coupon

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates test coupons for development'

    def handle(self, *args, **options):
        # Get or create an admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )

        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created admin user: {admin_user.email}"))

        # Create test coupons
        coupons_data = [
            {
                'code': 'WELCOME20',
                'description': 'Welcome discount - 20% off your first order',
                'discount_type': 'percentage',
                'discount_value': 20,
                'minimum_order_amount': 50,
                'max_discount_amount': 50,
                'valid_from': timezone.now(),
                'valid_to': timezone.now() + timedelta(days=90),
                'usage_limit_per_customer': 1,
                'total_usage_limit': 100,
                'is_active': True,
            },
            {
                'code': 'SAVE10',
                'description': 'Save $10 on orders over $100',
                'discount_type': 'fixed_amount',
                'discount_value': 10,
                'minimum_order_amount': 100,
                'valid_from': timezone.now(),
                'valid_to': timezone.now() + timedelta(days=30),
                'usage_limit_per_customer': 3,
                'total_usage_limit': None,  # Unlimited total uses
                'is_active': True,
            },
            {
                'code': 'SUMMER50',
                'description': '50% off summer collection - max $100 discount',
                'discount_type': 'percentage',
                'discount_value': 50,
                'minimum_order_amount': 0,
                'max_discount_amount': 100,
                'valid_from': timezone.now(),
                'valid_to': timezone.now() + timedelta(days=60),
                'usage_limit_per_customer': 2,
                'total_usage_limit': 50,
                'is_active': True,
            },
        ]

        for coupon_data in coupons_data:
            coupon, created = Coupon.objects.get_or_create(
                code=coupon_data['code'],
                defaults={**coupon_data, 'created_by': admin_user}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created coupon: {coupon.code} - {coupon.description}"))
            else:
                self.stdout.write(self.style.WARNING(f"Coupon already exists: {coupon.code}"))

        self.stdout.write(self.style.SUCCESS(f"\nTotal coupons in database: {Coupon.objects.count()}"))
        self.stdout.write(self.style.SUCCESS("\nActive coupons:"))
        for coupon in Coupon.objects.filter(is_active=True):
            self.stdout.write(f"- {coupon.code}: {coupon.get_discount_display()} (Min order: ${coupon.minimum_order_amount})")



