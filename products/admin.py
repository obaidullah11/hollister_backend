from django.contrib import admin
from .models import Product, ProductVariant, ProductSize

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'gender', 'selling_price', 'purchasing_price', 'created_at')
    list_filter = ('category', 'gender', 'created_at')
    search_fields = ('name', 'sku', 'description')
    ordering = ('-created_at',)
    inlines = [ProductVariantInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'description', 'gender', 'category')
        }),
        ('Pricing', {
            'fields': ('selling_price', 'purchasing_price')
        }),
        ('Additional Information', {
            'fields': ('material_and_care',)
        }),
    )

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'color', 'stock', 'created_at')
    list_filter = ('product', 'created_at')
    search_fields = ('name', 'product__name', 'color')
    inlines = [ProductSizeInline]

@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('variant', 'size', 'stock')
    list_filter = ('variant__product',)
    search_fields = ('variant__name', 'size')
