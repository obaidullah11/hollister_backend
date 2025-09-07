from django.urls import path
from . import views

app_name = 'coupons'

urlpatterns = [
    # Admin endpoints
    path('', views.CouponListCreateView.as_view(), name='coupon-list-create'),
    path('<int:pk>/', views.CouponDetailView.as_view(), name='coupon-detail'),
    path('usage-history/', views.CouponUsageHistoryView.as_view(), name='usage-history'),
    
    # Customer endpoints
    path('validate/', views.validate_coupon, name='validate-coupon'),
    path('apply/', views.apply_coupon_to_cart, name='apply-coupon'),
    path('remove/', views.remove_coupon_from_cart, name='remove-coupon'),
]




