from django.contrib import admin
from .models import StoreSettings, TermsAndConditions, PrivacyPolicy, PaymentMethod

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


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['provider', 'environment', 'is_active', 'created_at']
    list_filter = ['provider', 'environment', 'is_active']
    search_fields = ['provider']
    readonly_fields = ['created_at', 'updated_at', 'get_masked_api_key', 'get_masked_secret_key']
    fieldsets = (
        ('Provider Information', {
            'fields': ('provider', 'environment', 'is_active')
        }),
        ('API Credentials', {
            'fields': ('api_key', 'secret_key', 'get_masked_api_key', 'get_masked_secret_key'),
            'description': 'API keys are encrypted before storage. Masked keys show first and last 4 characters only.'
        }),
        ('Configuration', {
            'fields': ('config',),
            'description': 'Additional configuration in JSON format'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Make provider and environment read-only when editing
        if obj:
            return self.readonly_fields + ['provider', 'environment']
        return self.readonly_fields
    
    def get_masked_api_key(self, obj):
        return obj.get_masked_api_key()
    get_masked_api_key.short_description = "Masked API Key"
    
    def get_masked_secret_key(self, obj):
        return obj.get_masked_secret_key()
    get_masked_secret_key.short_description = "Masked Secret Key"
