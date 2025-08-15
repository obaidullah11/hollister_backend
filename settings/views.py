from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import StoreSettings, TermsAndConditions, PrivacyPolicy
from .serializers import SettingsSerializer, TermsAndConditionsSerializer, PrivacyPolicySerializer

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
