from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Coupon, CouponUsageHistory


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'discount_display', 'minimum_order_amount', 
        'valid_from', 'valid_to', 'times_used', 'usage_limit_display',
        'status_display', 'is_active', 'created_at'
    ]
    list_filter = [
        'is_active', 'discount_type', 'applicable_to',
        'valid_from', 'valid_to', 'created_at'
    ]
    search_fields = ['code', 'description']
    readonly_fields = ['times_used', 'created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Discount Configuration', {
            'fields': (
                'discount_type', 'discount_value', 
                'max_discount_amount', 'minimum_order_amount'
            )
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_to')
        }),
        ('Usage Limits', {
            'fields': (
                'total_usage_limit', 'usage_limit_per_customer', 
                'times_used'
            )
        }),
        ('Product/Category Restrictions', {
            'fields': (
                'applicable_to', 'applicable_products', 
                'applicable_categories'
            )
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    filter_horizontal = ('applicable_products', 'applicable_categories')
    
    def discount_display(self, obj):
        return obj.get_discount_display()
    discount_display.short_description = 'Discount'
    
    def usage_limit_display(self, obj):
        if obj.total_usage_limit is None:
            return 'Unlimited'
        return f'{obj.times_used}/{obj.total_usage_limit}'
    usage_limit_display.short_description = 'Usage'
    
    def status_display(self, obj):
        if not obj.is_active:
            return format_html('<span style="color: red;">Inactive</span>')
        
        now = timezone.now()
        if now < obj.valid_from:
            return format_html('<span style="color: orange;">Not Yet Valid</span>')
        elif now > obj.valid_to:
            return format_html('<span style="color: red;">Expired</span>')
        elif obj.total_usage_limit and obj.times_used >= obj.total_usage_limit:
            return format_html('<span style="color: red;">Limit Reached</span>')
        else:
            return format_html('<span style="color: green;">Active</span>')
    status_display.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CouponUsageHistory)
class CouponUsageHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'coupon', 'used_by', 'order', 'discount_amount', 'used_at'
    ]
    list_filter = ['used_at', 'coupon']
    search_fields = [
        'coupon__code', 'used_by__email', 'order__order_number'
    ]
    readonly_fields = ['coupon', 'used_by', 'order', 'discount_amount', 'used_at']
    
    def has_add_permission(self, request):
        # Prevent manual creation of usage history
        return False
    
    def has_change_permission(self, request, obj=None):
        # Prevent editing of usage history
        return False
