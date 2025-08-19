from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import StoreSettings, TermsAndConditions, PrivacyPolicy, PaymentMethod
from .serializers import SettingsSerializer, TermsAndConditionsSerializer, PrivacyPolicySerializer, PaymentMethodSerializer

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def settings_view(request):
    """Get or update store settings"""
    settings = StoreSettings.get_settings()
    
    if request.method == 'GET':
        serializer = SettingsSerializer(settings)
        return Response({
            'success': True,
            'message': 'Settings retrieved successfully',
            'data': serializer.data
        })
    
    elif request.method == 'PUT':
        serializer = SettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Settings updated successfully',
                'data': serializer.data
            })
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# Terms and Conditions Views
@api_view(['GET'])
def terms_and_conditions_view(request):
    """Get active terms and conditions (public)"""
    try:
        terms = TermsAndConditions.objects.filter(is_active=True).first()
        if not terms:
            return Response({
                'success': False,
                'message': 'No active terms and conditions found',
                'error': 'Terms and conditions not available'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TermsAndConditionsSerializer(terms)
        return Response({
            'success': True,
            'message': 'Terms and conditions retrieved successfully',
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to retrieve terms and conditions',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def terms_and_conditions_manage_view(request):
    """Create or update terms and conditions"""
    
    if request.method == 'POST':
        # Create new terms
        serializer = TermsAndConditionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Terms and conditions created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        # Update existing terms (get the active one)
        terms = TermsAndConditions.objects.filter(is_active=True).first()
        if not terms:
            return Response({
                'success': False,
                'message': 'No terms and conditions found to update',
                'error': 'Create terms first'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TermsAndConditionsSerializer(terms, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Terms and conditions updated successfully',
                'data': serializer.data
            })
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# Privacy Policy Views
@api_view(['GET'])
def privacy_policy_view(request):
    """Get active privacy policy (public)"""
    try:
        policy = PrivacyPolicy.objects.filter(is_active=True).first()
        if not policy:
            return Response({
                'success': False,
                'message': 'No active privacy policy found',
                'error': 'Privacy policy not available'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PrivacyPolicySerializer(policy)
        return Response({
            'success': True,
            'message': 'Privacy policy retrieved successfully',
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to retrieve privacy policy',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def privacy_policy_manage_view(request):
    """Create or update privacy policy"""
    
    if request.method == 'POST':
        # Create new policy
        serializer = PrivacyPolicySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Privacy policy created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        # Update existing policy (get the active one)
        policy = PrivacyPolicy.objects.filter(is_active=True).first()
        if not policy:
            return Response({
                'success': False,
                'message': 'No privacy policy found to update',
                'error': 'Create policy first'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PrivacyPolicySerializer(policy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Privacy policy updated successfully',
                'data': serializer.data
            })
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# Payment Method Views
@swagger_auto_schema(
    method='get',
    operation_description="List all payment methods",
    responses={
        200: openapi.Response('Success', PaymentMethodSerializer(many=True)),
        401: 'Unauthorized'
    }
)
@swagger_auto_schema(
    method='post',
    operation_description="Create a new payment method",
    request_body=PaymentMethodSerializer,
    responses={
        201: openapi.Response('Created', PaymentMethodSerializer),
        400: 'Bad Request',
        401: 'Unauthorized'
    }
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def payment_methods_list_create(request):
    """List all payment methods or create a new one"""
    
    if request.method == 'GET':
        payment_methods = PaymentMethod.objects.all()
        serializer = PaymentMethodSerializer(payment_methods, many=True)
        return Response({
            'success': True,
            'message': 'Payment methods retrieved successfully',
            'data': serializer.data
        })
    
    elif request.method == 'POST':
        serializer = PaymentMethodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Payment method created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Get a specific payment method",
    responses={
        200: openapi.Response('Success', PaymentMethodSerializer),
        401: 'Unauthorized',
        404: 'Not Found'
    }
)
@swagger_auto_schema(
    method='put',
    operation_description="Update a payment method",
    request_body=PaymentMethodSerializer,
    responses={
        200: openapi.Response('Updated', PaymentMethodSerializer),
        400: 'Bad Request',
        401: 'Unauthorized',
        404: 'Not Found'
    }
)
@swagger_auto_schema(
    method='delete',
    operation_description="Delete a payment method",
    responses={
        204: 'No Content',
        401: 'Unauthorized',
        404: 'Not Found'
    }
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def payment_method_detail(request, pk):
    """Retrieve, update or delete a payment method"""
    
    try:
        payment_method = PaymentMethod.objects.get(pk=pk)
    except PaymentMethod.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Payment method not found',
            'error': f'Payment method with id {pk} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = PaymentMethodSerializer(payment_method)
        return Response({
            'success': True,
            'message': 'Payment method retrieved successfully',
            'data': serializer.data
        })
    
    elif request.method == 'PUT':
        serializer = PaymentMethodSerializer(payment_method, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Payment method updated successfully',
                'data': serializer.data
            })
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        payment_method.delete()
        return Response({
            'success': True,
            'message': 'Payment method deleted successfully',
            'data': None
        }, status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='post',
    operation_description="Toggle payment method active status",
    responses={
        200: openapi.Response('Success', PaymentMethodSerializer),
        401: 'Unauthorized',
        404: 'Not Found'
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payment_method_toggle_status(request, pk):
    """Toggle the active status of a payment method"""
    
    try:
        payment_method = PaymentMethod.objects.get(pk=pk)
    except PaymentMethod.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Payment method not found',
            'error': f'Payment method with id {pk} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)
    
    payment_method.is_active = not payment_method.is_active
    payment_method.save()
    
    serializer = PaymentMethodSerializer(payment_method)
    return Response({
        'success': True,
        'message': f'Payment method {"activated" if payment_method.is_active else "deactivated"} successfully',
        'data': serializer.data
    })
