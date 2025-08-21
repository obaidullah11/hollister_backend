from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count, Sum
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Coupon, CouponUsageHistory
from .serializers import (
    CouponSerializer, 
    CouponApplySerializer, 
    CouponValidateSerializer,
    CouponUsageHistorySerializer
)



class CouponListCreateView(generics.ListCreateAPIView):
    """List all coupons or create a new coupon"""
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Coupon.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        elif status_filter == 'valid':
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True,
                valid_from__lte=now,
                valid_to__gte=now
            )
        elif status_filter == 'expired':
            queryset = queryset.filter(valid_to__lt=timezone.now())
        
        # Search by code or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'message': 'Coupon created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return Response({
                'success': True,
                'message': 'Coupons retrieved successfully',
                'data': response.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Coupons retrieved successfully',
            'data': serializer.data
        })


class CouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a coupon"""
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Add usage statistics
        usage_stats = CouponUsageHistory.objects.filter(coupon=instance).aggregate(
            total_uses=Count('id'),
            total_discount=Sum('discount_amount'),
            unique_users=Count('used_by', distinct=True)
        )
        
        data = serializer.data
        data['usage_statistics'] = usage_stats
        
        return Response({
            'success': True,
            'message': 'Coupon retrieved successfully',
            'data': data
        })
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'message': 'Coupon updated successfully',
            'data': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Coupon deleted successfully',
            'data': None
        }, status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='post',
    request_body=CouponValidateSerializer,
    responses={
        200: openapi.Response(
            description="Coupon is valid",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'code': openapi.Schema(type=openapi.TYPE_STRING),
                            'discount_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                            'final_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                        }
                    )
                }
            )
        ),
        400: 'Invalid coupon or requirements not met'
    },
    operation_description="Validate a coupon code and calculate discount for given order total",
    tags=['Coupons']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_coupon(request):
    """Validate a coupon code for the current user"""
    serializer = CouponValidateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    code = serializer.validated_data['code'].upper()
    order_total = serializer.validated_data['order_total']
    product_ids = serializer.validated_data.get('product_ids', [])
    
    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Invalid coupon code',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user can use this coupon
    if not coupon.can_be_used_by(request.user):
        return Response({
            'success': False,
            'message': 'You have already used this coupon the maximum number of times',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check minimum order amount
    if order_total < coupon.minimum_order_amount:
        return Response({
            'success': False,
            'message': f'Minimum order amount of ${coupon.minimum_order_amount} required',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate discount for the entire order
    discount_amount = coupon.calculate_discount(order_total)
    
    return Response({
        'success': True,
        'message': 'Coupon is valid',
        'data': {
            'code': coupon.code,
            'description': coupon.description,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'discount_display': coupon.get_discount_display(),
            'discount_amount': discount_amount,
            'final_amount': order_total - discount_amount
        }
    })


@swagger_auto_schema(
    method='post',
    request_body=CouponApplySerializer,
    responses={
        200: openapi.Response(
            description="Coupon applied successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                }
            )
        ),
        400: 'Invalid coupon or requirements not met'
    },
    operation_description="Apply a coupon to the user's cart",
    tags=['Coupons']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_coupon_to_cart(request):
    """Apply a coupon to the user's cart"""
    from orders.models import Cart
    
    serializer = CouponApplySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    code = serializer.validated_data['code'].upper()
    
    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Invalid coupon code',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get user's cart
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return Response({
            'success': False,
            'message': 'No cart found',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate coupon for this cart
    cart_total = cart.total_amount
    
    if not coupon.can_be_used_by(request.user):
        return Response({
            'success': False,
            'message': 'You have already used this coupon the maximum number of times',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if cart_total < coupon.minimum_order_amount:
        return Response({
            'success': False,
            'message': f'Minimum order amount of ${coupon.minimum_order_amount} required',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate discount for the entire cart
    discount_amount = coupon.calculate_discount(cart_total)
    
    # Store coupon in session or cart (you might want to add a field to Cart model)
    request.session['applied_coupon'] = {
        'code': coupon.code,
        'discount_amount': float(discount_amount)
    }
    
    return Response({
        'success': True,
        'message': 'Coupon applied successfully',
        'data': {
            'code': coupon.code,
            'discount_display': coupon.get_discount_display(),
            'discount_amount': discount_amount,
            'cart_total': cart_total,
            'final_amount': cart_total - discount_amount
        }
    })


@swagger_auto_schema(
    method='delete',
    responses={
        200: openapi.Response(
            description="Coupon removed successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(type=openapi.TYPE_OBJECT, nullable=True)
                }
            )
        )
    },
    operation_description="Remove applied coupon from cart",
    tags=['Coupons']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_coupon_from_cart(request):
    """Remove applied coupon from cart"""
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
    
    return Response({
        'success': True,
        'message': 'Coupon removed successfully',
        'data': None
    })


class CouponUsageHistoryView(generics.ListAPIView):
    """View coupon usage history"""
    serializer_class = CouponUsageHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CouponUsageHistory.objects.all()
        
        # Filter by coupon
        coupon_id = self.request.query_params.get('coupon_id')
        if coupon_id:
            queryset = queryset.filter(coupon_id=coupon_id)
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(used_by_id=user_id)
        
        return queryset.order_by('-used_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return Response({
                'success': True,
                'message': 'Usage history retrieved successfully',
                'data': response.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Usage history retrieved successfully',
            'data': serializer.data
        })
