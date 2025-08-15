from rest_framework import serializers
from .models import StoreSettings, TermsAndConditions, PrivacyPolicy

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
