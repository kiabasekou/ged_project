# dossiers/serializers.py
from rest_framework import serializers
from .models import Dossier
from apps.documents.models import Folder
from apps.users.serializers import UserMinimalSerializer
from apps.clients.serializers import ClientSerializer


class FolderSerializer(serializers.ModelSerializer):
    full_path = serializers.CharField(source="full_path", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True, allow_null=True)

    class Meta:
        model = Folder
        fields = ['id', 'name', 'full_path', 'parent', 'dossier', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['dossier', 'created_at']


class FolderTreeSerializer(FolderSerializer):
    """Pour afficher l'arborescence complète"""
    subfolders = serializers.SerializerMethodField()

    def get_subfolders(self, obj):
        return FolderTreeSerializer(obj.subfolders.all(), many=True).data

    class Meta(FolderSerializer.Meta):
        fields = FolderSerializer.Meta.fields + ['subfolders']


class DossierListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.display_name", read_only=True)
    responsible_name = serializers.CharField(source="responsible.get_full_name", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Dossier
        fields = [
            'id', 'reference_code', 'title', 'category', 'status',
            'client', 'client_name', 'responsible', 'responsible_name',
            'opening_date', 'closing_date', 'critical_deadline', 'is_overdue',
            'created_at'
        ]


class DossierDetailSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    responsible = UserMinimalSerializer(read_only=True)
    assigned_users = UserMinimalSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Dossier
        fields = '__all__'
        read_only_fields = ['id', 'reference_code', 'opening_date', 'created_at', 'updated_at', 'archived_date']