# clients/serializers.py
from rest_framework import serializers
from .models import Client


class ClientListSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'display_name', 'client_type', 'phone_primary', 'email', 'city', 'is_active']


class ClientSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    full_address = serializers.CharField(read_only=True)

    class Meta:
        model = Client
        fields = [
            'id', 'client_type', 'display_name',
            'first_name', 'last_name', 'date_of_birth', 'place_of_birth',
            'ni_number', 'ni_type',
            'company_name', 'rccm', 'nif',
            'representative_name', 'representative_role',
            'email', 'phone_primary', 'phone_secondary',
            'address_line', 'neighborhood', 'city', 'country', 'full_address',
            'data_source', 'consent_given', 'consent_date',
            'retention_period_years', 'notes', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']