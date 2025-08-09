from django.urls import path
from . import views

urlpatterns = [
    # Orders
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/status/', views.OrderStatusUpdateView.as_view(), name='order-status-update'),
    
    # Customer orders
    path('customer/orders/', views.CustomerOrderListView.as_view(), name='customer-order-list'),
    path('customer/order-stats/', views.customer_order_stats, name='customer-order-stats'),
    
    # Admin orders
    path('admin/orders/', views.AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin/order-stats/', views.order_stats, name='order-stats'),
    path('admin/bulk-update-status/', views.bulk_update_order_status, name='bulk-update-order-status'),
    path('admin/recent-orders/', views.recent_orders, name='recent-orders'),
    
    # Shipping addresses
    path('shipping-addresses/', views.ShippingAddressListView.as_view(), name='shipping-address-list'),
    path('shipping-addresses/<int:pk>/', views.ShippingAddressDetailView.as_view(), name='shipping-address-detail'),
]
