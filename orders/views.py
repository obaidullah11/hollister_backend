from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Sum, Count
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order, OrderItem, OrderStatusHistory, ShippingAddress
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderUpdateSerializer, 
    OrderStatusUpdateSerializer, OrderItemCreateSerializer, 
    AdminOrderSerializer, CustomerOrderSerializer, ShippingAddressSerializer
)

class OrderListView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'customer']
    search_fields = ['order_number', 'customer__email', 'customer__first_name', 'customer__last_name']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
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
        if self.request.user.is_admin:
            return Order.objects.select_related('customer').prefetch_related('items', 'status_history')
        else:
            return Order.objects.filter(customer=self.request.user).select_related('customer').prefetch_related('items', 'status_history')

class OrderStatusUpdateView(generics.UpdateAPIView):
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
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
        if not self.request.user.is_admin:
            return Order.objects.none()
        return Order.objects.select_related('customer').prefetch_related('items', 'status_history')

class ShippingAddressListView(generics.ListCreateAPIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ShippingAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
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
