from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory, ShippingAddress, Cart, CartItem
from products.models import Product, ProductVariant, ProductSize
from accounts.serializers import UserProfileSerializer

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'selling_price', 'category']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'color']

class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['id', 'size', 'stock']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    size = ProductSizeSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    variant_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    size_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'variant', 'size', 'quantity', 'unit_price', 'total_price',
            'product_id', 'variant_id', 'size_id', 'created_at'
        ]
        read_only_fields = ['unit_price', 'total_price', 'created_at']
    
    def validate(self, attrs):
        product_id = attrs.get('product_id')
        variant_id = attrs.get('variant_id')
        size_id = attrs.get('size_id')
        quantity = attrs.get('quantity', 1)
        
        # Validate product exists
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        
        # Set unit price from product
        attrs['unit_price'] = product.selling_price
        
        # Validate variant if provided
        if variant_id:
            try:
                variant = ProductVariant.objects.get(id=variant_id, product=product)
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError("Product variant not found")
        
        # Validate size if provided
        if size_id:
            if not variant_id:
                raise serializers.ValidationError("Size requires a variant")
            try:
                size = ProductSize.objects.get(id=size_id, variant_id=variant_id)
                # Check stock availability
                if size.stock < quantity:
                    raise serializers.ValidationError(f"Only {size.stock} units available in stock")
            except ProductSize.DoesNotExist:
                raise serializers.ValidationError("Product size not found")
        
        return attrs
    
    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        variant_id = validated_data.pop('variant_id', None)
        size_id = validated_data.pop('size_id', None)
        
        product = Product.objects.get(id=product_id)
        variant = ProductVariant.objects.get(id=variant_id) if variant_id else None
        size = ProductSize.objects.get(id=size_id) if size_id else None
        
        cart = self.context['cart']
        
        # Check if item already exists in cart
        existing_item = CartItem.objects.filter(
            cart=cart,
            product=product,
            variant=variant,
            size=size
        ).first()
        
        if existing_item:
            # Update quantity
            existing_item.quantity += validated_data.get('quantity', 1)
            existing_item.save()
            return existing_item
        else:
            # Create new item
            return CartItem.objects.create(
                cart=cart,
                product=product,
                variant=variant,
                size=size,
                **validated_data
            )

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_amount', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    size_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)

class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)

class CheckoutSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20)
    shipping_address = serializers.DictField()
    billing_address = serializers.DictField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_shipping_address(self, value):
        required_fields = ['address_line_1', 'city', 'state', 'postal_code', 'country']
        for field in required_fields:
            if field not in value or not value[field]:
                raise serializers.ValidationError(f"Shipping address {field} is required")
        return value
    
    def validate(self, attrs):
        # If billing address not provided, use shipping address
        if 'billing_address' not in attrs or not attrs['billing_address']:
            attrs['billing_address'] = attrs['shipping_address']
        return attrs

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['id', 'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country', 'is_default', 'created_at']
        read_only_fields = ['created_at']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    size = ProductSizeSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'variant', 'size', 'quantity', 'unit_price', 'total_price']

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    
    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'notes', 'created_by', 'created_at']
        read_only_fields = ['created_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = ShippingAddressSerializer(read_only=True)
    billing_address = ShippingAddressSerializer(read_only=True)
    item_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status', 'total_amount', 'email', 
            'phone_number', 'shipping_address', 'billing_address', 'notes', 
            'items', 'item_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'created_at', 'updated_at']

class OrderCreateSerializer(serializers.ModelSerializer):
    items_data = serializers.ListField(child=serializers.DictField(), write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'customer', 'shipping_address', 'billing_address', 'phone_number', 
            'email', 'notes', 'items_data'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items_data', [])
        order = Order.objects.create(**validated_data)
        
        total_amount = 0
        for item_data in items_data:
            product_id = item_data.get('product_id')
            variant_id = item_data.get('variant_id')
            size_id = item_data.get('size_id')
            quantity = item_data.get('quantity', 1)
            
            # Get product and calculate price
            product = Product.objects.get(id=product_id)
            unit_price = product.selling_price
            
            # Create order item
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                variant_id=variant_id if variant_id else None,
                size_id=size_id if size_id else None,
                quantity=quantity,
                unit_price=unit_price,
                total_price=unit_price * quantity
            )
            
            total_amount += order_item.total_price
        
        order.total_amount = total_amount
        order.save()
        
        # Create initial status history
        OrderStatusHistory.objects.create(
            order=order,
            status=Order.Status.PENDING,
            notes='Order created',
            created_by=self.context['request'].user
        )
        
        return order

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status', 'notes']

class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get('status')
        notes = validated_data.get('notes', '')
        
        instance.status = new_status
        if notes:
            instance.notes = notes
        instance.save()
        
        # Create status history entry
        OrderStatusHistory.objects.create(
            order=instance,
            status=new_status,
            notes=notes or f'Status changed from {old_status} to {new_status}',
            created_by=self.context['request'].user
        )
        
        return instance

class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'variant', 'size', 'quantity', 'unit_price']

class AdminOrderSerializer(OrderSerializer):
    customer = UserProfileSerializer(read_only=True)
    
    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + ['customer']

class CustomerOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    item_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'total_amount', 
            'shipping_address', 'phone_number', 'email', 
            'items', 'item_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'status', 'total_amount', 'created_at', 'updated_at']
