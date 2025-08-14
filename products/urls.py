from django.urls import path
from . import views

urlpatterns = [
    # Products
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/create-with-variants/', views.EnhancedProductCreateView.as_view(), name='enhanced-product-create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # Product variants
    path('products/<int:product_id>/variants/', views.ProductVariantCreateView.as_view(), name='variant-create'),
    path('products/<int:product_id>/variants/<int:pk>/', views.ProductVariantDetailView.as_view(), name='variant-detail'),
    path('products/<int:product_id>/images/', views.ProductImageCreateView.as_view(), name='image-create'),
    
    # Debug endpoint
    path('debug-request/', views.debug_request_data, name='debug-request'),
    
    # Admin endpoints
    path('admin/products/', views.AdminProductListView.as_view(), name='admin-product-list'),
    path('admin/product-stats/', views.product_stats, name='product-stats'),
    path('admin/category-stats/', views.category_stats, name='category-stats'),
    path('admin/bulk-update-stock/', views.bulk_update_stock, name='bulk-update-stock'),
]
