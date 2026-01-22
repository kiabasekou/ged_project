from rest_framework import serializers
from .models import Document, Folder
from apps.users.serializers import UserMinimalSerializer

# --- MODULE DOSSIERS/FOLDERS ---

class FolderSerializer(serializers.ModelSerializer):
    full_path = serializers.ReadOnlyField() 

    class Meta:
        model = Folder
        fields = ['id', 'name', 'full_path', 'parent', 'dossier']

class FolderTreeSerializer(serializers.ModelSerializer):
    full_path = serializers.ReadOnlyField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = ['id', 'name', 'full_path', 'parent', 'children']

    def get_children(self, obj):
        subfolders = obj.subfolders.all()
        return FolderTreeSerializer(subfolders, many=True, context=self.context).data

# --- MODULE DOCUMENTS ---

class DocumentListSerializer(serializers.ModelSerializer):
    folder_path = serializers.ReadOnlyField()
    uploaded_by_name = serializers.ReadOnlyField(source="uploaded_by.get_full_name")
    file_url = serializers.SerializerMethodField()
    file_size_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'folder', 'folder_path', 'file_extension',
            'file_size', 'file_size_formatted', 'file_url',
            'version', 'is_current_version', 'sensitivity',
            'uploaded_by', 'uploaded_by_name', 'uploaded_at'
        ]

    def get_file_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.file.url) if obj.file and request else None

    def get_file_size_formatted(self, obj):
        if not obj.file_size: return "0 octets"
        size = float(obj.file_size)
        for unit in ['octets', 'Ko', 'Mo', 'Go']:
            if size < 1024.0: return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} To"

class DocumentDetailSerializer(serializers.ModelSerializer):
    dossier_reference = serializers.ReadOnlyField(source="dossier.reference_code")
    folder = FolderSerializer(read_only=True)
    uploaded_by = UserMinimalSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        # CORRECTION : 'uploaded_by' a été ajouté dans la liste des champs
        fields = [
            'id', 'title', 'description', 'dossier', 'dossier_reference', 'folder', 
            'file', 'file_url', 'file_hash', 'file_extension', 'file_size',
            'original_filename', 'version', 'is_current_version', 
            'sensitivity', 'retention_until', 'uploaded_by', 'uploaded_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_hash', 'original_filename', 'uploaded_at', 
            'updated_at', 'is_current_version'
        ]

    def get_file_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.file.url) if obj.file and request else None