from rest_framework import serializers
from .models import StoreSettings, TermsAndConditions, PrivacyPolicy, PaymentMethod

class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreSettings
        fields = ['id', 'currency', 'timezone', 'created_at', 'updated_at']

class TermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndConditions
        fields = ['id', 'title', 'content', 'version', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = ['id', 'title', 'content', 'version', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class PaymentMethodSerializer(serializers.ModelSerializer):
    masked_api_key = serializers.SerializerMethodField()
    masked_secret_key = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'provider', 'environment', 'is_active',
            'api_key', 'secret_key', 'masked_api_key', 'masked_secret_key',
            'config', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'masked_api_key', 'masked_secret_key']
        extra_kwargs = {
            'api_key': {'write_only': True},
            'secret_key': {'write_only': True}
        }
    
    def get_masked_api_key(self, obj):
        return obj.get_masked_api_key()
    
    def get_masked_secret_key(self, obj):
        return obj.get_masked_secret_key()
    
    def validate_provider(self, value):
        """Ensure unique provider per environment"""
        instance = self.instance
        environment = self.initial_data.get('environment', 'sandbox')
        
        if instance:
            # Update case
            qs = PaymentMethod.objects.filter(
                provider=value,
                environment=environment
            ).exclude(pk=instance.pk)
        else:
            # Create case
            qs = PaymentMethod.objects.filter(
                provider=value,
                environment=environment
            )
        
        if qs.exists():
            raise serializers.ValidationError(
                f"A payment method for {value} in {environment} environment already exists."
            )
        return value
    
    def validate_config(self, value):
        """Validate configuration based on provider"""
        provider = self.initial_data.get('provider')
        
        # Define required config fields per provider
        required_fields = {
            'stripe': [],
            'paypal': ['client_id', 'webhook_id'],
            'google_pay': ['merchant_id', 'merchant_name'],
            'apple_pay': ['merchant_identifier', 'domain_name']
        }
        
        if provider and provider in required_fields:
            missing_fields = [
                field for field in required_fields[provider]
                if field not in value
            ]
            if missing_fields:
                raise serializers.ValidationError(
                    f"Missing required config fields for {provider}: {', '.join(missing_fields)}"
                )
        
        return value
