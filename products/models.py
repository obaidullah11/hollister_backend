from django.db import models
from django.utils.translation import gettext_lazy as _

class Product(models.Model):
    class Gender(models.TextChoices):
        MEN = 'men', _('Men')
        WOMEN = 'women', _('Women')
        UNISEX = 'unisex', _('Unisex')
        KIDS = 'kids', _('Kids')
    
    # Product Fields
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.UNISEX)
    category = models.CharField(max_length=100)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchasing_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    material_and_care = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def profit_margin(self):
        if self.purchasing_price and self.purchasing_price > 0:
            return ((self.selling_price - self.purchasing_price) / self.purchasing_price) * 100
        return 0

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    stock = models.PositiveIntegerField(default=0)
    variant_icon = models.ImageField(upload_to='variant_icons/', blank=True, null=True)
    variant_picture = models.ImageField(upload_to='variant_pictures/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Product Variant')
        verbose_name_plural = _('Product Variants')
        unique_together = ['product', 'name']
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"

class ProductSize(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=20)
    stock = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = _('Product Size')
        verbose_name_plural = _('Product Sizes')
        unique_together = ['variant', 'size']
    
    def __str__(self):
        return f"{self.variant.name} - {self.size}"
