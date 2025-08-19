from django.contrib import admin
from .models import Product, ProductVariant, ProductSize, Review, Category

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'gender', 'selling_price', 'purchasing_price', 'is_active', 'created_at')
    list_filter = ('category', 'gender', 'is_active', 'created_at')
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
        ('Status', {
            'fields': ('is_active',)
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


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_verified_purchase', 'helpful_votes', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'created_at')
    search_fields = ('product__name', 'user__username', 'user__email', 'comment')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'user', 'rating', 'comment')
        }),
        ('Status', {
            'fields': ('is_verified_purchase', 'helpful_votes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'product_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    def product_count(self, obj):
        from .models import Product
        return Product.objects.filter(category=obj.name).count()
    product_count.short_description = 'Products'
