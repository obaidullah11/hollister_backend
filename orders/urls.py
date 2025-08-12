from django.urls import path
from . import views

urlpatterns = [
    # Cart endpoints
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.AddToCartView.as_view(), name='add-to-cart'),
    path('cart/update/<int:pk>/', views.UpdateCartItemView.as_view(), name='update-cart-item'),
    path('cart/remove/<int:pk>/', views.RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('cart/clear/', views.ClearCartView.as_view(), name='clear-cart'),
    
    # Checkout endpoint
    path('checkout/', views.checkout_view, name='checkout'),
    
    # Order endpoints
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    
    # Admin order endpoints
    path('admin/orders/', views.AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin/orders/<int:pk>/', views.AdminOrderDetailView.as_view(), name='admin-order-detail'),
    
    # Shipping address endpoints
    path('shipping-addresses/', views.ShippingAddressListView.as_view(), name='shipping-address-list'),
    path('shipping-addresses/<int:pk>/', views.ShippingAddressDetailView.as_view(), name='shipping-address-detail'),
]
