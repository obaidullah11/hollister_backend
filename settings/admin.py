from django.contrib import admin
from .models import StoreSettings, TermsAndConditions, PrivacyPolicy

@admin.register(StoreSettings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ['currency', 'timezone', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Store Configuration', {
            'fields': ('currency', 'timezone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TermsAndConditions)
class TermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ['title', 'version', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'version')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['activate_terms', 'deactivate_terms']

    def activate_terms(self, request, queryset):
        # Deactivate all other terms first
        TermsAndConditions.objects.all().update(is_active=False)
        # Activate selected terms
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} terms and conditions activated successfully.')
    activate_terms.short_description = "Activate selected terms and conditions"

    def deactivate_terms(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} terms and conditions deactivated successfully.')
    deactivate_terms.short_description = "Deactivate selected terms and conditions"

@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ['title', 'version', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'version')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['activate_policy', 'deactivate_policy']

    def activate_policy(self, request, queryset):
        # Deactivate all other policies first
        PrivacyPolicy.objects.all().update(is_active=False)
        # Activate selected policy
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} privacy policy activated successfully.')
    activate_policy.short_description = "Activate selected privacy policy"

    def deactivate_policy(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} privacy policy deactivated successfully.')
    deactivate_policy.short_description = "Deactivate selected privacy policy"
