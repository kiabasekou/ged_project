# backend/apps/agenda/serializers.py

from rest_framework import serializers
from .models import Event
from apps.dossiers.serializers import DossierListSerializer
from apps.users.serializers import UserMinimalSerializer
from apps.dossiers.models import Dossier

class EventSerializer(serializers.ModelSerializer):
    created_by = UserMinimalSerializer(read_only=True)
    dossier = DossierListSerializer(read_only=True)
    dossier_id = serializers.PrimaryKeyRelatedField(
        queryset=Dossier.objects.all(),
        source='dossier',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'type', 'start_date', 'start_time', 'all_day',
            'end_date', 'end_time', 'location', 'description',
            'dossier', 'dossier_id', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)