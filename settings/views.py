from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.response import Response
from .models import StoreSettings
from .serializers import StoreSettingsSerializer, StoreSettingsUpdateSerializer


class IsAdminUser(BasePermission):
    """
    Custom permission class to check if user has admin role
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


@api_view(['GET'])
@permission_classes([AllowAny])
def get_store_settings(request):
    """Get current store settings"""
    try:
        settings = StoreSettings.get_settings()
        serializer = StoreSettingsSerializer(settings)
        return Response({
            'success': True,
            'message': 'Store settings retrieved successfully',
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error retrieving store settings: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_store_settings(request):
    """Update store settings"""
    try:
        settings = StoreSettings.get_settings()
        serializer = StoreSettingsUpdateSerializer(settings, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Store settings updated successfully',
                'data': StoreSettingsSerializer(settings).data
            })
        else:
            return Response({
                'success': False,
                'message': 'Invalid data provided',
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error updating store settings: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
