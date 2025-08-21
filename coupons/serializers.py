from rest_framework import serializers
from django.utils import timezone
from .models import Coupon, CouponUsageHistory


class CouponSerializer(serializers.ModelSerializer):
    discount_display = serializers.CharField(source='get_discount_display', read_only=True)
    is_valid = serializers.SerializerMethodField()
    times_available = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'discount_type', 'discount_value',
            'max_discount_amount', 'minimum_order_amount', 'valid_from', 'valid_to',
            'total_usage_limit', 'usage_limit_per_customer', 'is_active', 'times_used', 
            'discount_display', 'is_valid', 'times_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['times_used', 'created_at', 'updated_at']
    
    def get_is_valid(self, obj):
        return obj.is_valid()
    
    def get_times_available(self, obj):
        if obj.total_usage_limit is None:
            return None
        return max(0, obj.total_usage_limit - obj.times_used)
    
    def validate_code(self, value):
        """Ensure coupon code is uppercase and unique"""
        value = value.upper().strip()
        if self.instance and self.instance.code == value:
            return value
        if Coupon.objects.filter(code=value).exists():
            raise serializers.ValidationError("A coupon with this code already exists.")
        return value
    
    def validate_discount_value(self, value):
        """Validate discount value based on discount type"""
        discount_type = self.initial_data.get('discount_type', 
                                             self.instance.discount_type if self.instance else 'percentage')
        
        if discount_type == 'percentage' and value > 100:
            raise serializers.ValidationError("Percentage discount cannot exceed 100%")
        
        if value <= 0:
            raise serializers.ValidationError("Discount value must be greater than 0")
        
        return value
    
    def validate(self, data):
        """Validate coupon data"""
        # Validate date range
        valid_from = data.get('valid_from', self.instance.valid_from if self.instance else None)
        valid_to = data.get('valid_to', self.instance.valid_to if self.instance else None)
        
        if valid_from and valid_to and valid_from >= valid_to:
            raise serializers.ValidationError({
                'valid_to': 'Valid to date must be after valid from date'
            })
        
        # Validate usage limits
        total_limit = data.get('total_usage_limit')
        per_customer_limit = data.get('usage_limit_per_customer', 1)
        
        if total_limit is not None and per_customer_limit > total_limit:
            raise serializers.ValidationError({
                'usage_limit_per_customer': 'Per customer limit cannot exceed total usage limit'
            })
        

        
        return data


class CouponApplySerializer(serializers.Serializer):
    """Serializer for applying a coupon to cart/order"""
    code = serializers.CharField(required=True)
    
    def validate_code(self, value):
        """Validate and retrieve coupon"""
        value = value.upper().strip()
        try:
            coupon = Coupon.objects.get(code=value)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code")
        
        if not coupon.is_valid():
            if not coupon.is_active:
                raise serializers.ValidationError("This coupon is no longer active")
            
            now = timezone.now()
            if now < coupon.valid_from:
                raise serializers.ValidationError("This coupon is not yet valid")
            elif now > coupon.valid_to:
                raise serializers.ValidationError("This coupon has expired")
            elif coupon.total_usage_limit and coupon.times_used >= coupon.total_usage_limit:
                raise serializers.ValidationError("This coupon has reached its usage limit")
        
        return value


class CouponValidateSerializer(CouponApplySerializer):
    """Serializer for validating a coupon with order details"""
    order_total = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of product IDs in the order"
    )


class CouponUsageHistorySerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    user_email = serializers.EmailField(source='used_by.email', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = CouponUsageHistory
        fields = [
            'id', 'coupon', 'coupon_code', 'used_by', 'user_email',
            'order', 'order_number', 'discount_amount', 'used_at'
        ]
        read_only_fields = ['used_at']



