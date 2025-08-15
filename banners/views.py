from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from .models import Banner
from .serializers import (
    BannerSerializer, 
    BannerCreateSerializer, 
    BannerUpdateSerializer
)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def test_view(request):
    """
    Simple test view to verify the banner app is working
    """
    return Response({
        'success': True,
        'message': 'Banner app is working!',
    })

class BannerListView(generics.ListCreateAPIView):
    """
    GET: List all banners with pagination and filtering
    POST: Create new banner
    """
    serializer_class = BannerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Banner.objects.none()
        
        queryset = Banner.objects.all()
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
            )
        
        # Status filtering
        status_filter = self.request.query_params.get('status', None)
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BannerCreateSerializer
        return BannerSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            banner = serializer.save()
            return Response({
                'success': True,
                'message': 'Banner created successfully',
                'data': BannerSerializer(banner).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Failed to create banner',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'success': True,
                'message': 'Banners retrieved successfully',
                'data': {
                    'count': self.paginator.page.paginator.count,
                    'next': self.paginator.get_next_link(),
                    'previous': self.paginator.get_previous_link(),
                    'results': serializer.data
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Banners retrieved successfully',
            'data': serializer.data
        })

class BannerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Get detailed banner information
    PUT/PATCH: Update banner information
    DELETE: Delete banner
    """
    serializer_class = BannerSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Banner.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BannerUpdateSerializer
        return BannerSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Banner retrieved successfully',
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            banner = serializer.save()
            return Response({
                'success': True,
                'message': 'Banner updated successfully',
                'data': BannerSerializer(banner).data
            })
        return Response({
            'success': False,
            'message': 'Failed to update banner',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            'success': True,
            'message': 'Banner deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)

class ActiveBannerListView(generics.ListAPIView):
    """
    GET: List only active banners (public endpoint)
    """
    serializer_class = BannerSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Banner.objects.filter(is_active=True).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Active banners retrieved successfully',
            'data': serializer.data
        })

class BannerStatusUpdateView(generics.UpdateAPIView):
    """
    PATCH: Update banner status (active/inactive)
    """
    serializer_class = BannerSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Banner.objects.all()
    
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        is_active = request.data.get('is_active')
        
        if is_active is None:
            return Response({
                'success': False,
                'message': 'is_active field is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        instance.is_active = is_active
        instance.save()
        
        return Response({
            'success': True,
            'message': f'Banner status updated to {"active" if is_active else "inactive"}',
            'data': BannerSerializer(instance).data
        })
