from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory, ShippingAddress
from accounts.serializers import UserProfileSerializer
from products.serializers import ProductSerializer, ProductVariantSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'variant', 'size', 'quantity', 'unit_price', 'total_price']

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'notes', 'created_at', 'created_by']

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['id', 'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country', 'phone_number', 'is_default', 'created_at']

class OrderSerializer(serializers.ModelSerializer):
    customer = UserProfileSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    item_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'status', 'total_amount', 
            'shipping_address', 'billing_address', 'phone_number', 'email', 
            'notes', 'items', 'status_history', 'item_count', 'created_at', 'updated_at'
        ]

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
            from products.models import Product, ProductVariant, ProductSize
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
