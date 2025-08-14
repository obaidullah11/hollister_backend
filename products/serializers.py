from rest_framework import serializers
from .models import Product, ProductVariant, ProductSize

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
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'description', 'gender', 'category',
            'selling_price', 'purchasing_price', 'material_and_care',
            'variants', 'profit_margin', 'created_at', 'updated_at'
        ]

class ProductCreateSerializer(serializers.ModelSerializer):
    variants_data = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
    
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'description', 'gender', 'category',
            'selling_price', 'purchasing_price', 'material_and_care',
            'variants_data'
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
            'variants'
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
            'selling_price', 'purchasing_price', 'material_and_care'
        ]
    
    def validate_sku(self, value):
        if self.instance and Product.objects.filter(sku=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        elif not self.instance and Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        return value

class ProductVariantCreateSerializer(serializers.ModelSerializer):
    sizes = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    variant_icon = serializers.CharField(required=False, allow_blank=True)
    variant_picture = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = ProductVariant
        fields = [
            'name', 'color', 'stock', 'variant_icon', 'variant_picture', 'sizes'
        ]
    
    def create(self, validated_data):
        sizes_data = validated_data.pop('sizes', [])
        variant_icon_data = validated_data.pop('variant_icon', None)
        variant_picture_data = validated_data.pop('variant_picture', None)
        
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
        
        # Create sizes
        for size in sizes_data:
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
