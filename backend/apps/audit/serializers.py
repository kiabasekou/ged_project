# audit/serializers.py
from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.get_full_name", read_only=True, allow_null=True, default="Système"
    )
    user_username = serializers.CharField(source="user.username", read_only=True, allow_null=True)
    action_display = serializers.CharField(source="get_action_type_display", read_only=True)
    object_repr = serializers.CharField(read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'user_username',
            'action_type', 'action_display', 'object_repr',
            'content_type', 'object_id', 'changes', 'description',
            'ip_address', 'request_path', 'timestamp'
        ]
        read_only_fields = '__all__'  # Jamais modifiable via API