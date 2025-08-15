from django.urls import path
from . import views

app_name = 'banners'

urlpatterns = [
    # Test endpoint
    path('test/', views.test_view, name='test'),
    
    # Banner management endpoints
    path('', views.BannerListView.as_view(), name='banner-list'),
    path('<int:pk>/', views.BannerDetailView.as_view(), name='banner-detail'),
    path('<int:pk>/status/', views.BannerStatusUpdateView.as_view(), name='banner-status-update'),
    
    # Public endpoints
    path('active/', views.ActiveBannerListView.as_view(), name='active-banners'),
]
