from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
import os


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


class PaymentMethod(models.Model):
    """Model to store payment gateway configurations"""
    
    PROVIDER_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('google_pay', 'Google Pay'),
        ('apple_pay', 'Apple Pay'),
    ]
    
    ENVIRONMENT_CHOICES = [
        ('sandbox', 'Sandbox/Test'),
        ('production', 'Production'),
    ]
    
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        unique=True,
        verbose_name=_('Payment Provider')
    )
    
    environment = models.CharField(
        max_length=20,
        choices=ENVIRONMENT_CHOICES,
        default='sandbox',
        verbose_name=_('Environment')
    )
    
    is_active = models.BooleanField(
        default=False,
        verbose_name=_('Is Active')
    )
    
    # Encrypted fields for sensitive data
    api_key = models.TextField(
        blank=True,
        verbose_name=_('API Key')
    )
    
    secret_key = models.TextField(
        blank=True,
        verbose_name=_('Secret Key')
    )
    
    # Additional configuration as JSON
    config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Additional Configuration')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        ordering = ['provider']
    
    def __str__(self):
        return f"{self.get_provider_display()} - {self.get_environment_display()}"
    
    def _get_cipher_suite(self):
        """Get or create encryption key"""
        key = getattr(settings, 'PAYMENT_ENCRYPTION_KEY', None)
        if not key:
            key = Fernet.generate_key()
        return Fernet(key)
    
    def encrypt_field(self, value):
        """Encrypt a field value"""
        if not value:
            return ""
        cipher_suite = self._get_cipher_suite()
        return cipher_suite.encrypt(value.encode()).decode()
    
    def decrypt_field(self, value):
        """Decrypt a field value"""
        if not value:
            return ""
        try:
            cipher_suite = self._get_cipher_suite()
            return cipher_suite.decrypt(value.encode()).decode()
        except:
            return value  # Return as-is if decryption fails
    
    def save(self, *args, **kwargs):
        """Encrypt sensitive fields before saving"""
        if self.api_key and not self.api_key.startswith('gAAAAA'):  # Check if already encrypted
            self.api_key = self.encrypt_field(self.api_key)
        if self.secret_key and not self.secret_key.startswith('gAAAAA'):
            self.secret_key = self.encrypt_field(self.secret_key)
        super().save(*args, **kwargs)
    
    def get_decrypted_api_key(self):
        """Get decrypted API key"""
        return self.decrypt_field(self.api_key)
    
    def get_decrypted_secret_key(self):
        """Get decrypted secret key"""
        return self.decrypt_field(self.secret_key)
    
    def get_masked_api_key(self):
        """Get masked API key for display"""
        decrypted = self.get_decrypted_api_key()
        if len(decrypted) > 8:
            return f"{decrypted[:4]}{'*' * (len(decrypted) - 8)}{decrypted[-4:]}"
        return "*" * len(decrypted)
    
    def get_masked_secret_key(self):
        """Get masked secret key for display"""
        decrypted = self.get_decrypted_secret_key()
        if len(decrypted) > 8:
            return f"{decrypted[:4]}{'*' * (len(decrypted) - 8)}{decrypted[-4:]}"
        return "*" * len(decrypted)
