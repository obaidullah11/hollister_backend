from rest_framework import serializers
from .models import Product, ProductVariant, ProductSize, Review, Category
from django.contrib.auth import get_user_model

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active', 'product_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'product_count', 'created_at', 'updated_at']
    
    def get_product_count(self, obj):
        """Get count of products in this category"""
        return Product.objects.filter(category=obj.name, is_active=True).count()


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['id', 'size', 'stock']

class ProductVariantSerializer(serializers.ModelSerializer):
    sizes = ProductSizeSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'name', 'color', 'stock', 'variant_icon', 'variant_picture',
            'sizes', 'created_at', 'updated_at'
        ]

class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    profit_margin = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'description', 'gender', 'category',
            'selling_price', 'purchasing_price', 
            'material_and_care', 'is_active', 'show_on_homepage', 'variants', 
            'profit_margin', 'average_rating', 'review_count', 
            'created_at', 'updated_at'
        ]

class ProductCreateSerializer(serializers.ModelSerializer):
    variants_data = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
    
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'description', 'gender', 'category',
            'selling_price', 'purchasing_price', 'material_and_care',
            'is_active', 'show_on_homepage', 'variants_data'
        ]
    
    def validate_sku(self, value):
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        return value
    
    def validate_selling_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Selling price must be greater than 0.")
        return value
    
    def validate_purchasing_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Purchasing price must be greater than 0.")
        return value
    
    def create(self, validated_data):
        variants_data = validated_data.pop('variants_data', [])
        product = super().create(validated_data)
        
        # Create variants
        for variant_data in variants_data:
            sizes_data = variant_data.pop('sizes', [])
            
            variant = ProductVariant.objects.create(product=product, **variant_data)
            
            # Create sizes
            for size_data in sizes_data:
                ProductSize.objects.create(variant=variant, **size_data)
        
        return product

class EnhancedProductCreateSerializer(serializers.ModelSerializer):
    """
    Enhanced serializer that handles multiple variants with images in one call.
    Expects multipart/form-data with array-style field names.
    """
    variants = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
    
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'description', 'gender', 'category',
            'selling_price', 'purchasing_price', 'material_and_care',
            'is_active', 'show_on_homepage', 'variants'
        ]
    
    def validate_sku(self, value):
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        return value
    
    def validate_selling_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Selling price must be greater than 0.")
        return value
    
    def validate_purchasing_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Purchasing price must be greater than 0.")
        return value
    
    def validate_variants(self, value):
        """Validate variants data structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Variants must be a list")
        
        for i, variant in enumerate(value):
            if not isinstance(variant, dict):
                raise serializers.ValidationError(f"Variant {i} must be a dictionary")
            
            required_fields = ['name', 'color']
            for field in required_fields:
                if field not in variant:
                    raise serializers.ValidationError(f"Variant {i} missing required field: {field}")
            
            if not variant['name']:
                raise serializers.ValidationError(f"Variant {i} name cannot be empty")
            
            if not variant['color']:
                raise serializers.ValidationError(f"Variant {i} color cannot be empty")
            
            # Validate stock/stock_quantity
            stock_value = variant.get('stock', variant.get('stock_quantity', 0))
            try:
                stock = int(stock_value)
                if stock < 0:
                    raise serializers.ValidationError(f"Variant {i} stock cannot be negative")
            except (ValueError, TypeError):
                raise serializers.ValidationError(f"Variant {i} stock must be a valid number")
        
        return value
    
    def create(self, validated_data):
        variants_data = validated_data.pop('variants', [])
        product = super().create(validated_data)
        
        # Create variants with images
        for variant_data in variants_data:
            sizes_data = variant_data.pop('sizes', [])
            
            # Handle sizes - convert string to list if needed
            if isinstance(sizes_data, str):
                sizes_data = [size.strip() for size in sizes_data.split(',')]
            elif not isinstance(sizes_data, list):
                sizes_data = []
            
            # Create variant
            variant = ProductVariant.objects.create(product=product, **variant_data)
            
            # Create sizes
            for size in sizes_data:
                ProductSize.objects.create(variant=variant, size=size, stock=variant.stock)
        
        return product

class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'description', 'gender', 'category',
            'selling_price', 'purchasing_price', 'material_and_care',
            'is_active', 'show_on_homepage'
        ]
    
    def validate_sku(self, value):
        if self.instance and Product.objects.filter(sku=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        elif not self.instance and Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        return value

class ProductVariantCreateSerializer(serializers.ModelSerializer):
    sizes = serializers.CharField(write_only=True, required=False)  # Changed to CharField to handle comma-separated values
    size_stocks = serializers.CharField(write_only=True, required=False)  # Changed to CharField to handle JSON string from FormData
    variant_icon = serializers.CharField(required=False, allow_blank=True)
    variant_picture = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = ProductVariant
        fields = [
            'name', 'color', 'stock', 'variant_icon', 'variant_picture', 'sizes', 'size_stocks'
        ]
    
    def create(self, validated_data):
        sizes_data = validated_data.pop('sizes', '')
        size_stocks_raw = validated_data.pop('size_stocks', '')
        variant_icon_data = validated_data.pop('variant_icon', None)
        variant_picture_data = validated_data.pop('variant_picture', None)
        
        # Parse size_stocks if it's a JSON string
        size_stocks_data = []
        if size_stocks_raw:
            try:
                import json
                if isinstance(size_stocks_raw, str):
                    size_stocks_data = json.loads(size_stocks_raw)
                else:
                    size_stocks_data = size_stocks_raw
            except (json.JSONDecodeError, TypeError):
                size_stocks_data = []
        
        # Create variant without images first
        variant = super().create(validated_data)
        
        # Handle variant_icon
        if variant_icon_data and variant_icon_data.startswith('data:image'):
            # Convert base64 to file and save
            import base64
            from django.core.files.base import ContentFile
            
            try:
                # Extract the base64 data
                format, imgstr = variant_icon_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Create file name
                filename = f"variant_icon_{variant.id}_{variant.name}.{ext}"
                
                # Convert to file and save
                data = ContentFile(base64.b64decode(imgstr))
                variant.variant_icon.save(filename, data, save=False)
            except Exception as e:
                # If base64 conversion fails, ignore the image
                pass
        
        # Handle variant_picture
        if variant_picture_data and variant_picture_data.startswith('data:image'):
            # Convert base64 to file and save
            import base64
            from django.core.files.base import ContentFile
            
            try:
                # Extract the base64 data
                format, imgstr = variant_picture_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Create file name
                filename = f"variant_picture_{variant.id}_{variant.name}.{ext}"
                
                # Convert to file and save
                data = ContentFile(base64.b64decode(imgstr))
                variant.variant_picture.save(filename, data, save=False)
            except Exception as e:
                # If base64 conversion fails, ignore the image
                pass
        
        # Create sizes with individual stock values
        if size_stocks_data:
            # Use individual size stock data if provided
            for size_stock in size_stocks_data:
                if 'size' in size_stock and 'stock' in size_stock:
                    ProductSize.objects.create(
                        variant=variant, 
                        size=size_stock['size'], 
                        stock=int(size_stock['stock'])
                    )
        elif sizes_data:
            # Fallback to comma-separated sizes with variant stock
            sizes_list = [size.strip() for size in sizes_data.split(',') if size.strip()]
            for size in sizes_list:
                ProductSize.objects.create(variant=variant, size=size, stock=variant.stock)
        
        variant.save()
        return variant

class ProductVariantUpdateSerializer(serializers.ModelSerializer):
    variant_icon = serializers.CharField(required=False, allow_blank=True)
    variant_picture = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = ProductVariant
        fields = [
            'name', 'color', 'stock', 'variant_icon', 'variant_picture'
        ]
    
    def update(self, instance, validated_data):
        # Handle base64 image data
        variant_icon_data = validated_data.pop('variant_icon', None)
        variant_picture_data = validated_data.pop('variant_picture', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Handle variant_icon
        if variant_icon_data and variant_icon_data.startswith('data:image'):
            # Convert base64 to file and save
            import base64
            from django.core.files.base import ContentFile
            
            try:
                # Extract the base64 data
                format, imgstr = variant_icon_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Create file name
                filename = f"variant_icon_{instance.id}_{instance.name}.{ext}"
                
                # Convert to file and save
                data = ContentFile(base64.b64decode(imgstr))
                instance.variant_icon.save(filename, data, save=False)
            except Exception as e:
                # If base64 conversion fails, ignore the image
                pass
        
        # Handle variant_picture
        if variant_picture_data and variant_picture_data.startswith('data:image'):
            # Convert base64 to file and save
            import base64
            from django.core.files.base import ContentFile
            
            try:
                # Extract the base64 data
                format, imgstr = variant_picture_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Create file name
                filename = f"variant_picture_{instance.id}_{instance.name}.{ext}"
                
                # Convert to file and save
                data = ContentFile(base64.b64decode(imgstr))
                instance.variant_picture.save(filename, data, save=False)
            except Exception as e:
                # If base64 conversion fails, ignore the image
                pass
        
        instance.save()
        return instance

class ProductImageSerializer(serializers.Serializer):
    """
    Simple serializer for product image uploads
    """
    image = serializers.ImageField()
    caption = serializers.CharField(required=False, allow_blank=True)


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reading reviews with user information"""
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'product', 'user', 'user_id', 'username', 'rating', 
            'comment', 'is_verified_purchase', 'helpful_votes', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'user_id', 'username', 'is_verified_purchase', 'helpful_votes']


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating reviews"""
    
    class Meta:
        model = Review
        fields = ['product', 'rating', 'comment']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def validate(self, data):
        # Check if user already has a review for this product
        user = self.context['request'].user
        product = data['product']
        
        if self.instance is None:  # Creating new review
            if Review.objects.filter(user=user, product=product).exists():
                raise serializers.ValidationError("You have already reviewed this product.")
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # Check if user has purchased this product to set is_verified_purchase
        # This logic would check the orders model
        return super().create(validated_data)


class ProductDetailSerializer(ProductSerializer):
    """Extended product serializer that includes reviews"""
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['reviews']
