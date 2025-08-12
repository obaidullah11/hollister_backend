from django.contrib import admin
from .models import StoreSettings


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    """Admin configuration for StoreSettings"""
    list_display = ['currency', 'timezone', 'created_at', 'updated_at']
    list_display_links = ['currency', 'timezone']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        """Only allow one settings record"""
        return not StoreSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of settings"""
        return False
