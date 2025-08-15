from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class StoreSettings(models.Model):
    """Global store settings including currency and timezone"""
    
    CURRENCY_CHOICES = [
        ('USD', 'USD ($)'),
        ('EUR', 'EUR (€)'),
        ('GBP', 'GBP (£)'),
        ('CAD', 'CAD (C$)'),
        ('AUD', 'AUD (A$)'),
        ('JPY', 'JPY (¥)'),
    ]
    
    TIMEZONE_CHOICES = [
        ('UTC', 'UTC'),
        ('EST', 'Eastern Standard Time'),
        ('PST', 'Pacific Standard Time'),
        ('CST', 'Central Standard Time'),
        ('MST', 'Mountain Standard Time'),
        ('GMT', 'Greenwich Mean Time'),
        ('CET', 'Central European Time'),
        ('IST', 'Indian Standard Time'),
        ('JST', 'Japan Standard Time'),
        ('AEST', 'Australian Eastern Standard Time'),
    ]
    
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD',
        verbose_name=_('Currency')
    )
    
    timezone = models.CharField(
        max_length=10,
        choices=TIMEZONE_CHOICES,
        default='UTC',
        verbose_name=_('Timezone')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Store Settings')
        verbose_name_plural = _('Store Settings')
    
    def __str__(self):
        return f"Store Settings - {self.currency} / {self.timezone}"
    
    @classmethod
    def get_settings(cls):
        """Get the current store settings, create if doesn't exist"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

class TermsAndConditions(models.Model):
    title = models.CharField(max_length=200, default="Terms and Conditions")
    content = models.TextField()
    version = models.CharField(max_length=20, default="1.0")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Terms and Conditions"
        verbose_name_plural = "Terms and Conditions"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} v{self.version}"

class PrivacyPolicy(models.Model):
    title = models.CharField(max_length=200, default="Privacy Policy")
    content = models.TextField()
    version = models.CharField(max_length=20, default="1.0")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Privacy Policy"
        verbose_name_plural = "Privacy Policies"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} v{self.version}"
