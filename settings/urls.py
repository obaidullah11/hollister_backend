from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('store-settings/', views.get_store_settings, name='get_store_settings'),
    path('store-settings/update/', views.update_store_settings, name='update_store_settings'),
]
