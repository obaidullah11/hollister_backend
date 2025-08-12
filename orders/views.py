from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction
from django.db.models import Q, Sum, Count
from django_filters.rest_framework import DjangoFilterBackend
import uuid
from .models import Order, OrderItem, OrderStatusHistory, ShippingAddress, Cart, CartItem
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderUpdateSerializer, 
    OrderStatusUpdateSerializer, OrderItemCreateSerializer, 
    AdminOrderSerializer, CustomerOrderSerializer, ShippingAddressSerializer,
    CartSerializer, CartItemSerializer, AddToCartSerializer, UpdateCartItemSerializer, CheckoutSerializer
)

# Cart Views
class CartView(generics.RetrieveAPIView):
    """
    Get user's cart
    
    Retrieve the current user's shopping cart with all items.
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    @swagger_auto_schema(
        tags=['Shopping Flow'],
        operation_description="Retrieve the current user's shopping cart with all items",
        responses={
            200: openapi.Response(
                description="Cart retrieved successfully",
                schema=CartSerializer
            ),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class AddToCartView(generics.CreateAPIView):
    """
    Add item to cart
    
    Add a product to the user's shopping cart. If the item already exists,
    the quantity will be increased.
    """
    serializer_class = AddToCartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        tags=['Shopping Flow'],
        operation_description="Add a product to the user's shopping cart",
        request_body=AddToCartSerializer,
        responses={
            201: openapi.Response(
                description="Item added to cart successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: "Invalid data or validation error",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Create cart item serializer with cart context
            cart_item_serializer = CartItemSerializer(
                data=serializer.validated_data,
                context={'cart': cart}
            )
            
            if cart_item_serializer.is_valid():
                cart_item = cart_item_serializer.save()
                cart_serializer = CartSerializer(cart)
                
                return Response({
                    'success': True,
                    'message': 'Item added to cart successfully',
                    'data': cart_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to add item to cart',
                    'errors': cart_item_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UpdateCartItemView(generics.UpdateAPIView):
    """
    Update cart item quantity
    
    Update the quantity of a specific item in the user's cart.
    """
    serializer_class = UpdateCartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CartItem.objects.all()
    
    @swagger_auto_schema(
        tags=['Shopping Flow'],
        operation_description="Update the quantity of a specific item in the user's cart",
        request_body=UpdateCartItemSerializer,
        responses={
            200: openapi.Response(
                description="Cart item updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: "Invalid data or validation error",
            401: "Authentication required",
            404: "Cart item not found"
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=['Shopping Flow'],
        operation_description="Update the quantity of a specific item in the user's cart (partial update)",
        request_body=UpdateCartItemSerializer,
        responses={
            200: openapi.Response(
                description="Cart item updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: "Invalid data or validation error",
            401: "Authentication required",
            404: "Cart item not found"
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        cart_item = self.get_object()
        serializer = self.get_serializer(cart_item, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Check stock availability if size is specified
            if cart_item.size:
                if cart_item.size.stock < serializer.validated_data.get('quantity', 1):
                    return Response({
                        'success': False,
                        'message': f'Only {cart_item.size.stock} units available in stock'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            cart_item = serializer.save()
            cart_serializer = CartSerializer(cart_item.cart)
            
            return Response({
                'success': True,
                'message': 'Cart item updated successfully',
                'data': cart_serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Failed to update cart item',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class RemoveFromCartView(generics.DestroyAPIView):
    """
    Remove item from cart
    
    Remove a specific item from the user's shopping cart.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = CartItem.objects.all()
    
    @swagger_auto_schema(
        tags=['Shopping Flow'],
        operation_description="Remove a specific item from the user's shopping cart",
        responses={
            200: openapi.Response(
                description="Item removed from cart successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            401: "Authentication required",
            404: "Cart item not found"
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        cart_item = self.get_object()
        cart = cart_item.cart
        cart_item.delete()
        
        cart_serializer = CartSerializer(cart)
        
        return Response({
            'success': True,
            'message': 'Item removed from cart successfully',
            'data': cart_serializer.data
        })

class ClearCartView(generics.DestroyAPIView):
    """
    Clear all items from cart
    
    Remove all items from the user's shopping cart.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        tags=['Shopping Flow'],
        operation_description="Remove all items from the user's shopping cart",
        responses={
            200: openapi.Response(
                description="Cart cleared successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            401: "Authentication required"
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    def destroy(self, request, *args, **kwargs):
        cart = self.get_object()
        cart.items.all().delete()
        
        cart_serializer = CartSerializer(cart)
        
        return Response({
            'success': True,
            'message': 'Cart cleared successfully',
            'data': cart_serializer.data
        })

# Checkout View
@swagger_auto_schema(
    method='post',
    tags=['Shopping Flow'],
    operation_description="Process the checkout by creating an order from the user's cart items",
    request_body=CheckoutSerializer,
    responses={
        201: openapi.Response(
            description="Order placed successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'order': openapi.Schema(type=openapi.TYPE_OBJECT),
                            'order_number': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                }
            )
        ),
        400: "Invalid checkout data or cart is empty",
        401: "Authentication required"
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def checkout_view(request):
    """
    Checkout cart and create order
    
    Process the checkout by creating an order from the user's cart items.
    This will create shipping/billing addresses, generate an order number,
    and clear the cart after successful order creation.
    """
    serializer = CheckoutSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                # Get user's cart
                cart = Cart.objects.filter(user=request.user).first()
                if not cart or cart.items.count() == 0:
                    return Response({
                        'success': False,
                        'message': 'Cart is empty'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                checkout_data = serializer.validated_data
                
                # Create shipping address
                shipping_address_data = checkout_data['shipping_address']
                shipping_address = ShippingAddress.objects.create(
                    user=request.user,
                    **shipping_address_data
                )
                
                # Create billing address (same as shipping if not provided)
                billing_address_data = checkout_data.get('billing_address', shipping_address_data)
                billing_address = ShippingAddress.objects.create(
                    user=request.user,
                    **billing_address_data
                )
                
                # Generate order number
                order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
                
                # Create order
                order = Order.objects.create(
                    order_number=order_number,
                    customer=request.user,
                    status=Order.Status.PENDING,
                    payment_status=Order.PaymentStatus.COMPLETED,  # Default to completed for now
                    total_amount=cart.total_amount,
                    email=checkout_data['email'],
                    phone_number=checkout_data['phone_number'],
                    shipping_address=shipping_address,
                    billing_address=billing_address,
                    notes=checkout_data.get('notes', '')
                )
                
                # Create order items from cart items
                for cart_item in cart.items.all():
                    # Check stock availability
                    if cart_item.size:
                        if cart_item.size.stock < cart_item.quantity:
                            raise Exception(f"Insufficient stock for {cart_item.product.name}")
                        # Update stock
                        cart_item.size.stock -= cart_item.quantity
                        cart_item.size.save()
                    
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        variant=cart_item.variant,
                        size=cart_item.size,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.unit_price,
                        total_price=cart_item.total_price
                    )
                
                # Create initial status history
                OrderStatusHistory.objects.create(
                    order=order,
                    status=Order.Status.PENDING,
                    notes='Order placed successfully',
                    created_by=request.user
                )
                
                # Clear cart
                cart.items.all().delete()
                
                # Serialize order for response
                order_serializer = OrderSerializer(order)
                
                return Response({
                    'success': True,
                    'message': 'Order placed successfully',
                    'data': {
                        'order': order_serializer.data,
                        'order_number': order_number
                    }
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': False,
        'message': 'Invalid checkout data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

# Existing Order Views (keep these)
class OrderListView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'customer']
    search_fields = ['order_number', 'customer__email', 'customer__first_name', 'customer__last_name']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        if self.request.user.is_admin:
            return Order.objects.select_related('customer').prefetch_related('items', 'status_history')
        else:
            return Order.objects.filter(customer=self.request.user).select_related('customer').prefetch_related('items', 'status_history')

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        if self.request.user.is_admin:
            return Order.objects.select_related('customer').prefetch_related('items', 'status_history')
        else:
            return Order.objects.filter(customer=self.request.user).select_related('customer').prefetch_related('items', 'status_history')

class OrderStatusUpdateView(generics.UpdateAPIView):
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        if self.request.user.is_admin:
            return Order.objects.all()
        else:
            return Order.objects.filter(customer=self.request.user)

class CustomerOrderListView(generics.ListAPIView):
    serializer_class = CustomerOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(customer=self.request.user).select_related('customer').prefetch_related('items')

class AdminOrderListView(generics.ListAPIView):
    serializer_class = AdminOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'customer']
    search_fields = ['order_number', 'customer__email', 'customer__first_name', 'customer__last_name']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        if not self.request.user.is_admin:
            return Order.objects.none()
        return Order.objects.select_related('customer').prefetch_related('items', 'status_history')

class AdminOrderDetailView(generics.RetrieveUpdateAPIView):
    """
    Admin: Get and update order details
    """
    serializer_class = AdminOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        if not self.request.user.is_admin:
            return Order.objects.none()
        return Order.objects.select_related('customer').prefetch_related('items', 'status_history')
    
    def update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        
        if serializer.is_valid():
            old_status = order.status
            order = serializer.save()
            
            # Create status history if status changed
            if old_status != order.status:
                OrderStatusHistory.objects.create(
                    order=order,
                    status=order.status,
                    notes=f'Status updated to {order.status}',
                    created_by=request.user
                )
            
            return Response({
                'success': True,
                'message': 'Order updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Failed to update order',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ShippingAddressListView(generics.ListCreateAPIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ShippingAddress.objects.none()
        return ShippingAddress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ShippingAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ShippingAddress.objects.none()
        return ShippingAddress.objects.filter(user=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def order_stats(request):
    if not request.user.is_admin:
        return Response({"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)
    
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status=Order.Status.PENDING).count()
    processing_orders = Order.objects.filter(status=Order.Status.PROCESSING).count()
    completed_orders = Order.objects.filter(status__in=[Order.Status.DELIVERED, Order.Status.REFUNDED]).count()
    cancelled_orders = Order.objects.filter(status=Order.Status.CANCELLED).count()
    
    # Calculate total revenue
    total_revenue = Order.objects.filter(
        status__in=[Order.Status.DELIVERED, Order.Status.REFUNDED]
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Calculate average order value
    avg_order_value = Order.objects.filter(
        status__in=[Order.Status.DELIVERED, Order.Status.REFUNDED]
    ).aggregate(avg=Sum('total_amount') / Count('id'))['avg'] or 0
    
    return Response({
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'total_revenue': total_revenue,
        'average_order_value': avg_order_value,
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def customer_order_stats(request):
    user = request.user
    
    total_orders = Order.objects.filter(customer=user).count()
    completed_orders = Order.objects.filter(
        customer=user, 
        status__in=[Order.Status.DELIVERED, Order.Status.REFUNDED]
    ).count()
    total_spent = Order.objects.filter(
        customer=user,
        status__in=[Order.Status.DELIVERED, Order.Status.REFUNDED]
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    return Response({
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'total_spent': total_spent,
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_update_order_status(request):
    if not request.user.is_admin:
        return Response({"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)
    
    updates = request.data.get('updates', [])
    updated_count = 0
    
    for update in updates:
        order_id = update.get('order_id')
        new_status = update.get('status')
        notes = update.get('notes', '')
        
        try:
            order = Order.objects.get(id=order_id)
            old_status = order.status
            order.status = new_status
            order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                notes=notes or f'Status changed from {old_status} to {new_status}',
                created_by=request.user
            )
            updated_count += 1
        except Order.DoesNotExist:
            continue
    
    return Response({
        'message': f'Successfully updated {updated_count} orders',
        'updated_count': updated_count
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recent_orders(request):
    if not request.user.is_admin:
        return Response({"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)
    
    recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:10]
    serializer = AdminOrderSerializer(recent_orders, many=True)
    
    return Response(serializer.data)

class ShippingAddressListView(generics.ListCreateAPIView):
    """
    List and create shipping addresses
    """
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @swagger_auto_schema(
        tags=['Shopping Flow'],
        operation_description="List all shipping addresses for the current user",
        responses={
            200: openapi.Response(
                description="Shipping addresses retrieved successfully",
                schema=ShippingAddressSerializer(many=True)
            ),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=['Shopping Flow'],
        operation_description="Create a new shipping address for the current user",
        request_body=ShippingAddressSerializer,
        responses={
            201: openapi.Response(
                description="Shipping address created successfully",
                schema=ShippingAddressSerializer
            ),
            400: "Invalid data",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ShippingAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, and delete shipping address
    """
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ShippingAddress.objects.all()
    
    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)
    
    @swagger_auto_schema(
        tags=['Shopping Flow'],
        operation_description="Get a specific shipping address",
        responses={
            200: openapi.Response(
                description="Shipping address retrieved successfully",
                schema=ShippingAddressSerializer
            ),
            401: "Authentication required",
            404: "Shipping address not found"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=['Shopping Flow'],
        operation_description="Update a shipping address",
        request_body=ShippingAddressSerializer,
        responses={
            200: openapi.Response(
                description="Shipping address updated successfully",
                schema=ShippingAddressSerializer
            ),
            400: "Invalid data",
            401: "Authentication required",
            404: "Shipping address not found"
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=['Shopping Flow'],
        operation_description="Partially update a shipping address",
        request_body=ShippingAddressSerializer,
        responses={
            200: openapi.Response(
                description="Shipping address updated successfully",
                schema=ShippingAddressSerializer
            ),
            400: "Invalid data",
            401: "Authentication required",
            404: "Shipping address not found"
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=['Shopping Flow'],
        operation_description="Delete a shipping address",
        responses={
            204: "Shipping address deleted successfully",
            401: "Authentication required",
            404: "Shipping address not found"
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
