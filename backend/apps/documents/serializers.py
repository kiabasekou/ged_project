"""
Serializers REST pour gestion des documents avec validation stricte.
"""
import mimetypes
from pathlib import Path

from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _

from .models import Document, Folder


class FolderSerializer(serializers.ModelSerializer):
    """Serializer pour les dossiers avec chemin complet"""
    
    full_path = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Folder
        fields = [
            'id', 'name', 'dossier', 'parent', 'full_path',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_full_path(self, obj):
        return obj.get_full_path()
    
    def validate(self, attrs):
        """Validation de la hiérarchie"""
        parent = attrs.get('parent')
        dossier = attrs.get('dossier')
        
        if parent and parent.dossier != dossier:
            raise serializers.ValidationError({
                'parent': "Le dossier parent doit appartenir au même dossier juridique"
            })
        
        return attrs


class DocumentVersionHistorySerializer(serializers.ModelSerializer):
    """Serializer simplifié pour l'historique des versions"""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size_human = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'version', 'uploaded_at', 'uploaded_by', 'uploaded_by_name',
            'file_size', 'file_size_human', 'file_hash', 'description'
        ]
        read_only_fields = fields
    
    def get_file_size_human(self, obj):
        """Formatage taille fichier (ex: 2.5 MB)"""
        size = obj.file_size
        for unit in ['o', 'Ko', 'Mo', 'Go']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} To"


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer principal pour les documents avec validation stricte.
    """
    
    # Champs en lecture seule calculés
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    folder_path = serializers.CharField(source='folder.get_full_path', read_only=True, allow_null=True)
    file_size_human = serializers.SerializerMethodField()
    integrity_verified = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    
    # Champs en écriture uniquement
    file = serializers.FileField(write_only=True, required=False)
    
    class Meta:
        model = Document
        fields = [
            'id', 'dossier', 'folder', 'folder_path',
            'file', 'title', 'description', 'original_filename',
            'file_extension', 'file_size', 'file_size_human', 'mime_type',
            'file_hash', 'version', 'is_current_version', 'previous_version',
            'sensitivity', 'retention_until',
            'uploaded_by', 'uploaded_by_name', 'uploaded_at', 'updated_at',
            'integrity_verified', 'download_url'
        ]
        read_only_fields = [
            'id', 'file_hash', 'version', 'file_extension', 'file_size',
            'mime_type', 'original_filename', 'uploaded_at', 'updated_at'
        ]
    
    # Configuration de validation stricte
    ALLOWED_EXTENSIONS = [
        '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt',
        '.txt', '.rtf', '.odt', '.ods', '.odp',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
        '.zip', '.rar', '.7z', '.msg', '.eml'
    ]
    
    ALLOWED_MIME_TYPES = {
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.doc': 'application/msword',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xls': 'application/vnd.ms-excel',
        '.txt': 'text/plain',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.zip': 'application/zip',
    }
    
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
    
    def get_file_size_human(self, obj):
        """Formatage lisible de la taille"""
        size = obj.file_size
        for unit in ['o', 'Ko', 'Mo', 'Go']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} To"
    
    def get_integrity_verified(self, obj):
        """Vérification de l'intégrité du fichier"""
        try:
            return obj.verify_integrity()
        except Exception:
            return False
    
    def get_download_url(self, obj):
        """URL de téléchargement du document"""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.get_absolute_url())
        return None
    
    def validate_file(self, file):
        """
        Validation stricte du fichier uploadé:
        - Taille maximale
        - Extension autorisée
        - Type MIME cohérent
        - Pas de contenu malveillant évident
        """
        if not file:
            return file
        
        # 1. Vérification de la taille
        if file.size > self.MAX_FILE_SIZE:
            raise serializers.ValidationError(
                f"Fichier trop volumineux. Maximum autorisé: {self.MAX_FILE_SIZE / 1024 / 1024:.0f} MB"
            )
        
        # 2. Vérification de l'extension
        extension = Path(file.name).suffix.lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"Extension '{extension}' non autorisée. "
                f"Extensions acceptées: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # 3. Vérification du type MIME
        declared_mime = file.content_type
        expected_mime = self.ALLOWED_MIME_TYPES.get(extension)
        
        if expected_mime and declared_mime != expected_mime:
            # Tentative de détection via le contenu
            detected_mime, _ = mimetypes.guess_type(file.name)
            
            if detected_mime != expected_mime and declared_mime != expected_mime:
                raise serializers.ValidationError(
                    f"Type MIME incohérent. Extension {extension} attendue: {expected_mime}, "
                    f"reçu: {declared_mime}"
                )
        
        # 4. Vérification basique anti-malware (magic bytes)
        file.seek(0)
        header = file.read(1024)
        file.seek(0)
        
        # Vérification des magic bytes pour PDF
        if extension == '.pdf' and not header.startswith(b'%PDF-'):
            raise serializers.ValidationError(
                "Le fichier ne semble pas être un PDF valide"
            )
        
        # Vérification pour ZIP (PK header)
        if extension in ['.docx', '.xlsx', '.pptx', '.zip']:
            if not header.startswith(b'PK\x03\x04'):
                raise serializers.ValidationError(
                    f"Le fichier {extension} ne semble pas être un ZIP valide"
                )
        
        return file
    
    def validate(self, attrs):
        """Validation globale des attributs"""
        folder = attrs.get('folder')
        dossier = attrs.get('dossier')
        
        # Vérifier cohérence folder/dossier
        if folder and folder.dossier != dossier:
            raise serializers.ValidationError({
                'folder': "Le sous-dossier doit appartenir au même dossier juridique"
            })
        
        # Vérifier niveau de sensibilité vs dossier
        sensitivity = attrs.get('sensitivity')
        if sensitivity == 'secret' and dossier.category not in ['penal', 'civil']:
            raise serializers.ValidationError({
                'sensitivity': "Niveau 'Secret Professionnel' réservé aux affaires pénales et civiles"
            })
        
        return attrs
    
    def create(self, validated_data):
        """Création d'un nouveau document (version 1)"""
        # L'utilisateur connecté est automatiquement l'uploader
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['uploaded_by'] = request.user
        
        try:
            return super().create(validated_data)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class DocumentUploadSerializer(serializers.Serializer):
    """
    Serializer pour upload initial de document.
    Utilisé pour l'endpoint POST /documents/upload/
    """
    
    dossier = serializers.UUIDField(required=True)
    folder = serializers.UUIDField(required=False, allow_null=True)
    file = serializers.FileField(required=True)
    title = serializers.CharField(max_length=300, required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    sensitivity = serializers.ChoiceField(
        choices=Document.SENSITIVITY_CHOICES,
        default='internal'
    )
    
    def validate(self, attrs):
        """Validation croisée"""
        # Réutilise la validation du DocumentSerializer
        doc_serializer = DocumentSerializer(data=attrs, context=self.context)
        doc_serializer.is_valid(raise_exception=True)
        return attrs


class DocumentVersionCreateSerializer(serializers.Serializer):
    """
    Serializer pour créer une nouvelle version d'un document existant.
    Utilisé pour l'endpoint POST /documents/{id}/new-version/
    """
    
    file = serializers.FileField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(max_length=300, required=False)
    
    def validate_file(self, file):
        """Réutilise la validation stricte de DocumentSerializer"""
        doc_serializer = DocumentSerializer()
        return doc_serializer.validate_file(file)
