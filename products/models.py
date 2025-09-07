from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    """Independent Category model for product categorization"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True, help_text="Category image")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_categories'
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name


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
    is_active = models.BooleanField(default=True, help_text="Whether the product is active and visible to customers")
    show_on_homepage = models.BooleanField(default=False, help_text="Whether to show product on homepage")
    
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
    
    @property
    def average_rating(self):
        """Calculate the average rating for this product"""
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    @property
    def review_count(self):
        """Get the total number of reviews for this product"""
        return self.reviews.count()

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


class Review(models.Model):
    """Product review model for customer feedback"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(help_text="Review comment")
    is_verified_purchase = models.BooleanField(
        default=False, 
        help_text="Whether this review is from a verified purchase"
    )
    helpful_votes = models.PositiveIntegerField(
        default=0,
        help_text="Number of users who found this review helpful"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Product Review')
        verbose_name_plural = _('Product Reviews')
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # One review per user per product
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name} - {self.rating} stars"
