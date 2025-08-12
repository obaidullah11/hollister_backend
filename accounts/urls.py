from django.urls import path
from . import views

urlpatterns = [
    # Test endpoint
    path('test/', views.test_view, name='test'),
    
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password Reset
    path('forgot-password/', views.forgot_password_view, name='forgot-password'),
    path('reset-password/', views.reset_password_view, name='reset-password'),
    
    # Profile management
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserUpdateView.as_view(), name='profile-update'),
    
    # Comprehensive User Management
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/status/', views.update_user_status_view, name='user-status-update'),
    path('users/<int:pk>/delete/', views.delete_user_view, name='user-delete'),
    path('users/bulk-update-status/', views.bulk_update_status_view, name='bulk-update-status'),
    path('users/statistics/', views.user_statistics_view, name='user-statistics'),
    
    # Admin user management (legacy)
    path('admin/users/', views.AdminUserListView.as_view(), name='admin-users'),
    path('admin/users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin-user-detail'),
    
    # Dashboard stats
    path('admin/dashboard-stats/', views.dashboard_stats, name='dashboard-stats'),
]
