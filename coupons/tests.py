from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from .models import Coupon, CouponUsageHistory
from orders.models import Cart, CartItem, Order

User = get_user_model()


class CouponModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.coupon = Coupon.objects.create(
            code='TEST20',
            description='Test coupon for 20% off',
            discount_type='percentage',
            discount_value=20,
            minimum_order_amount=50,
            valid_from=timezone.now() - timedelta(days=1),
            valid_to=timezone.now() + timedelta(days=30),
            usage_limit_per_customer=1,
            created_by=self.user
        )
    
    def test_coupon_creation(self):
        self.assertEqual(self.coupon.code, 'TEST20')
        self.assertEqual(self.coupon.discount_value, 20)
        self.assertTrue(self.coupon.is_active)
    
    def test_discount_display(self):
        self.assertEqual(self.coupon.get_discount_display(), '20% off')
        
        fixed_coupon = Coupon.objects.create(
            code='SAVE10',
            discount_type='fixed_amount',
            discount_value=10,
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30),
            created_by=self.user
        )
        self.assertEqual(fixed_coupon.get_discount_display(), '$10 off')
    
    def test_is_valid(self):
        self.assertTrue(self.coupon.is_valid())
        
        # Test expired coupon
        expired_coupon = Coupon.objects.create(
            code='EXPIRED',
            discount_type='percentage',
            discount_value=10,
            valid_from=timezone.now() - timedelta(days=30),
            valid_to=timezone.now() - timedelta(days=1),
            created_by=self.user
        )
        self.assertFalse(expired_coupon.is_valid())
        
        # Test inactive coupon
        self.coupon.is_active = False
        self.coupon.save()
        self.assertFalse(self.coupon.is_valid())
    
    def test_calculate_discount_percentage(self):
        discount = self.coupon.calculate_discount(100)
        self.assertEqual(discount, 20)  # 20% of 100
        
        # Test with max discount amount
        self.coupon.max_discount_amount = 15
        self.coupon.save()
        discount = self.coupon.calculate_discount(100)
        self.assertEqual(discount, 15)  # Capped at max discount
    
    def test_calculate_discount_fixed(self):
        fixed_coupon = Coupon.objects.create(
            code='FIXED25',
            discount_type='fixed_amount',
            discount_value=25,
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30),
            created_by=self.user
        )
        discount = fixed_coupon.calculate_discount(100)
        self.assertEqual(discount, 25)
        
        # Test when fixed discount exceeds order total
        discount = fixed_coupon.calculate_discount(20)
        self.assertEqual(discount, 20)  # Can't discount more than order total


class CouponAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123'
        )
        self.coupon_data = {
            'code': 'NEWCOUPON',
            'description': 'New coupon for testing',
            'discount_type': 'percentage',
            'discount_value': 15,
            'minimum_order_amount': 0,
            'valid_from': timezone.now().isoformat(),
            'valid_to': (timezone.now() + timedelta(days=30)).isoformat(),
            'usage_limit_per_customer': 1,
            'is_active': True
        }
    
    def test_create_coupon_admin_only(self):
        # Test regular user cannot create coupon
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post('/api/coupons/', self.coupon_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test admin can create coupon
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/coupons/', self.coupon_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['code'], 'NEWCOUPON')
    
    def test_list_coupons(self):
        # Create test coupons
        Coupon.objects.create(
            code='ACTIVE1',
            discount_type='percentage',
            discount_value=10,
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30),
            created_by=self.admin_user
        )
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/coupons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_validate_coupon(self):
        coupon = Coupon.objects.create(
            code='VALID20',
            discount_type='percentage',
            discount_value=20,
            minimum_order_amount=50,
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30),
            created_by=self.admin_user
        )
        
        self.client.force_authenticate(user=self.regular_user)
        
        # Test valid coupon
        response = self.client.post('/api/coupons/validate/', {
            'code': 'VALID20',
            'order_total': 100
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['discount_amount'], 20)
        
        # Test minimum order amount not met
        response = self.client.post('/api/coupons/validate/', {
            'code': 'VALID20',
            'order_total': 30
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])



