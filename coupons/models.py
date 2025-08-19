from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from products.models import Product, Category

User = get_user_model()


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', _('Percentage')
        FIXED_AMOUNT = 'fixed_amount', _('Fixed Amount')
    
    class ApplicableType(models.TextChoices):
        ALL = 'all', _('All Products')
        SPECIFIC_PRODUCTS = 'specific_products', _('Specific Products')
        SPECIFIC_CATEGORIES = 'specific_categories', _('Specific Categories')
    
    # Basic Information
    code = models.CharField(
        max_length=50, 
        unique=True, 
        help_text="Unique coupon code that customers will use"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Description of the coupon offer"
    )
    
    # Discount Configuration
    discount_type = models.CharField(
        max_length=20, 
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE
    )
    discount_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Discount value (percentage or fixed amount)"
    )
    max_discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Maximum discount amount for percentage discounts"
    )
    
    # Order Constraints
    minimum_order_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Minimum order amount required to use this coupon"
    )
    
    # Validity Period
    valid_from = models.DateTimeField(help_text="Coupon validity start date and time")
    valid_to = models.DateTimeField(help_text="Coupon validity end date and time")
    
    # Usage Limits
    total_usage_limit = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Total number of times this coupon can be used (null for unlimited)"
    )
    usage_limit_per_customer = models.PositiveIntegerField(
        default=1,
        help_text="Number of times a single customer can use this coupon"
    )
    
    # Product/Category Restrictions
    applicable_to = models.CharField(
        max_length=30,
        choices=ApplicableType.choices,
        default=ApplicableType.ALL
    )
    applicable_products = models.ManyToManyField(
        Product,
        blank=True,
        related_name='applicable_coupons',
        help_text="Products this coupon applies to (if applicable_to is SPECIFIC_PRODUCTS)"
    )
    applicable_categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='applicable_coupons',
        help_text="Categories this coupon applies to (if applicable_to is SPECIFIC_CATEGORIES)"
    )
    
    # Status and Tracking
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the coupon is currently active"
    )
    times_used = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this coupon has been used"
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='created_coupons'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'coupons'
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['valid_from', 'valid_to']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.get_discount_display()}"
    
    def get_discount_display(self):
        """Return human-readable discount description"""
        if self.discount_type == self.DiscountType.PERCENTAGE:
            return f"{self.discount_value}% off"
        else:
            return f"${self.discount_value} off"
    
    def is_valid(self):
        """Check if coupon is currently valid"""
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_to and
            (self.total_usage_limit is None or self.times_used < self.total_usage_limit)
        )
    
    def can_be_used_by(self, user):
        """Check if a specific user can use this coupon"""
        if not self.is_valid():
            return False
        
        user_usage_count = self.usage_history.filter(used_by=user).count()
        return user_usage_count < self.usage_limit_per_customer
    
    def calculate_discount(self, order_total, applicable_items_total=None):
        """Calculate the discount amount for a given order total"""
        if not self.is_valid():
            return 0
        
        if order_total < self.minimum_order_amount:
            return 0
        
        # Use applicable_items_total if provided (for category/product specific coupons)
        base_amount = applicable_items_total if applicable_items_total is not None else order_total
        
        if self.discount_type == self.DiscountType.PERCENTAGE:
            discount = base_amount * (self.discount_value / 100)
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return discount
        else:
            # Fixed amount discount
            return min(self.discount_value, base_amount)


class CouponUsageHistory(models.Model):
    """Track coupon usage history"""
    coupon = models.ForeignKey(
        Coupon, 
        on_delete=models.CASCADE, 
        related_name='usage_history'
    )
    used_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='coupon_usage_history'
    )
    order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.CASCADE,
        related_name='coupon_usage'
    )
    discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Actual discount amount applied"
    )
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'coupon_usage_history'
        verbose_name = _('Coupon Usage History')
        verbose_name_plural = _('Coupon Usage History')
        ordering = ['-used_at']
    
    def __str__(self):
        return f"{self.coupon.code} used by {self.used_by.email} on {self.used_at}"
