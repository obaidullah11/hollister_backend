from django.urls import path
from . import views

urlpatterns = [
    # Settings endpoints
    path('', views.settings_view, name='settings'),

    # Terms and Conditions endpoints
    path('terms/', views.terms_and_conditions_view, name='terms_and_conditions'),
    path('terms/manage/', views.terms_and_conditions_manage_view, name='terms_manage'),

    # Privacy Policy endpoints
    path('privacy/', views.privacy_policy_view, name='privacy_policy'),
    path('privacy/manage/', views.privacy_policy_manage_view, name='privacy_manage'),
]
