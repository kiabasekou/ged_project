# backend/apps/users/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    """Pour les relations : responsible, assigned_users, uploaded_by, etc."""
    full_name = serializers.CharField(source="get_full_name", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'role', 'role_display', 'professional_id']


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    is_legal_professional = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'email', 'role', 'role_display',
            'professional_id', 'phone_number', 'is_legal_professional',
            'is_staff', 'is_active', 'date_joined'
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    is_legal_professional = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name',
            'email', 'role', 'role_display', 'professional_id',
            'phone_number', 'is_legal_professional', 'is_staff', 'is_active',
            'has_accepted_privacy_policy', 'privacy_policy_accepted_at',
            'date_joined', 'last_login'
        ]
        read_only_fields = [
            'id', 'is_staff', 'is_active', 'has_accepted_privacy_policy',
            'privacy_policy_accepted_at', 'date_joined', 'last_login'
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Pour la mise à jour du profil personnel uniquement"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']