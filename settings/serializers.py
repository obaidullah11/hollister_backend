from rest_framework import serializers
from .models import StoreSettings


class StoreSettingsSerializer(serializers.ModelSerializer):
    """Serializer for store settings"""
    
    class Meta:
        model = StoreSettings
        fields = ['currency', 'timezone', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class StoreSettingsUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating store settings"""
    
    class Meta:
        model = StoreSettings
        fields = ['currency', 'timezone']
