"""
ViewSets pour gestion des documents avec sécurité renforcée.
"""
from django.http import FileResponse, Http404
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import PermissionDenied, ValidationError

from guardian.shortcuts import get_objects_for_user, assign_perm

from .models import Document, Folder
from .serializers import (
    DocumentSerializer,
    DocumentUploadSerializer,
    DocumentVersionCreateSerializer,
    DocumentVersionHistorySerializer,
    FolderSerializer
)
from apps.audit.utils import log_action


class UploadRateThrottle(UserRateThrottle):
    """Rate limiting spécifique pour les uploads (50/heure par utilisateur)"""
    scope = 'upload'
    rate = '50/hour'


class DocumentRateThrottle(UserRateThrottle):
    """Rate limiting pour consultation documents (1000/jour)"""
    scope = 'documents'
    rate = '1000/day'


class FolderViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gestion de l'arborescence de dossiers.
    """
    
    queryset = Folder.objects.select_related('dossier', 'parent', 'created_by')
    serializer_class = FolderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['dossier', 'parent']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Filtrage par permissions utilisateur"""
        user = self.request.user
        
        if user.is_superuser:
            return self.queryset
        
        # Récupère les dossiers auxquels l'utilisateur a accès
        accessible_dossiers = get_objects_for_user(
            user,
            'dossiers.view_dossier',
            klass='dossiers.Dossier'
        )
        
        return self.queryset.filter(dossier__in=accessible_dossiers)
    
    def perform_create(self, serializer):
        """Attribution automatique du créateur et des permissions"""
        folder = serializer.save(created_by=self.request.user)
        
        # Log audit
        log_action(
            user=self.request.user,
            obj=folder,
            action_type='CREATE',
            description=f"Création du dossier '{folder.name}'"
        )
    
    @action(detail=True, methods=['get'])
    def tree(self, request, pk=None):
        """
        Retourne l'arborescence complète sous ce dossier.
        GET /folders/{id}/tree/
        """
        folder = self.get_object()
        
        def build_tree(folder_obj):
            """Construction récursive de l'arbre"""
            return {
                'id': str(folder_obj.id),
                'name': folder_obj.name,
                'created_at': folder_obj.created_at,
                'subfolders': [
                    build_tree(sub) for sub in folder_obj.subfolders.all()
                ],
                'documents_count': folder_obj.documents.filter(is_current_version=True).count()
            }
        
        tree_data = build_tree(folder)
        return Response(tree_data)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal pour gestion des documents avec versionnage.
    """
    
    queryset = Document.objects.select_related(
        'dossier', 'folder', 'uploaded_by', 'previous_version'
    ).prefetch_related('next_versions')
    
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [DocumentRateThrottle]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['dossier', 'folder', 'sensitivity', 'is_current_version']
    search_fields = ['title', 'description', 'original_filename']
    ordering_fields = ['uploaded_at', 'title', 'file_size', 'version']
    ordering = ['-uploaded_at']
    
    def get_queryset(self):
        """
        Filtrage par permissions + optimisation requêtes.
        Par défaut, ne retourne que les versions courantes.
        """
        user = self.request.user
        queryset = self.queryset
        
        # Filtrer par versions courantes sauf si explicitement demandé
        show_all_versions = self.request.query_params.get('all_versions', 'false').lower() == 'true'
        if not show_all_versions:
            queryset = queryset.filter(is_current_version=True)
        
        if user.is_superuser:
            return queryset
        
        # Permissions via Guardian
        accessible_dossiers = get_objects_for_user(
            user,
            'dossiers.view_dossier',
            klass='dossiers.Dossier'
        )
        
        return queryset.filter(dossier__in=accessible_dossiers)
    
    def get_throttles(self):
        """Rate limiting différencié selon l'action"""
        if self.action in ['upload', 'create_version']:
            return [UploadRateThrottle()]
        return super().get_throttles()
    
    @transaction.atomic
    def perform_create(self, serializer):
        """Création document avec log audit"""
        document = serializer.save(uploaded_by=self.request.user)
        
        log_action(
            user=self.request.user,
            obj=document,
            action_type='CREATE',
            description=f"Upload document '{document.title}' (v{document.version})"
        )
    
    @action(detail=False, methods=['post'], throttle_classes=[UploadRateThrottle])
    def upload(self, request):
        """
        Upload initial d'un document.
        POST /documents/upload/
        
        Body:
        - dossier (UUID)
        - folder (UUID, optionnel)
        - file (File)
        - title (str)
        - description (str, optionnel)
        - sensitivity (str)
        """
        serializer = DocumentUploadSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        # Création via le serializer principal
        doc_serializer = DocumentSerializer(
            data=validated_data,
            context={'request': request}
        )
        doc_serializer.is_valid(raise_exception=True)
        
        document = doc_serializer.save(uploaded_by=request.user)
        
        log_action(
            user=request.user,
            obj=document,
            action_type='CREATE',
            description=f"Upload document '{document.title}'"
        )
        
        return Response(
            DocumentSerializer(document, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'], throttle_classes=[UploadRateThrottle])
    @transaction.atomic
    def new_version(self, request, pk=None):
        """
        Crée une nouvelle version du document.
        POST /documents/{id}/new-version/
        
        Body:
        - file (File)
        - description (str, optionnel)
        - title (str, optionnel)
        """
        document = self.get_object()
        
        # Vérification: seule la version courante peut être versionnée
        if not document.is_current_version:
            raise ValidationError({
                'detail': "Impossible de créer une version depuis une version non-courante"
            })
        
        serializer = DocumentVersionCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        # Création de la nouvelle version
        new_document = document.create_new_version(
            new_file=validated_data['file'],
            uploaded_by=request.user,
            title=validated_data.get('title', document.title),
            description=validated_data.get('description', document.description)
        )
        
        log_action(
            user=request.user,
            obj=new_document,
            action_type='UPDATE',
            description=f"Nouvelle version du document '{new_document.title}' (v{new_document.version})",
            changes={'previous_version': str(document.id), 'new_version': str(new_document.id)}
        )
        
        return Response(
            DocumentSerializer(new_document, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        Retourne l'historique complet des versions.
        GET /documents/{id}/history/
        """
        document = self.get_object()
        history = document.get_version_history()
        
        serializer = DocumentVersionHistorySerializer(history, many=True)
        
        return Response({
            'current_version': document.version,
            'total_versions': len(history),
            'history': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    @method_decorator(cache_page(60 * 5))  # Cache 5 minutes
    def download(self, request, pk=None):
        """
        Téléchargement du fichier avec déchiffrement transparent.
        GET /documents/{id}/download/
        """
        document = self.get_object()
        
        # Vérification de l'intégrité
        if not document.verify_integrity():
            log_action(
                user=request.user,
                obj=document,
                action_type='INTEGRITY_FAILURE',
                description=f"Échec vérification intégrité: {document.title}"
            )
            raise ValidationError({
                'detail': "Intégrité du fichier compromise. Contactez l'administrateur."
            })
        
        # Log de l'accès
        log_action(
            user=request.user,
            obj=document,
            action_type='DOWNLOAD',
            description=f"Téléchargement: {document.title} (v{document.version})"
        )
        
        # Ouverture du fichier (déchiffrement transparent via storage)
        try:
            file_obj = document.file.open('rb')
            response = FileResponse(
                file_obj,
                content_type=document.mime_type,
                as_attachment=True,
                filename=document.original_filename
            )
            
            # Headers de sécurité
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            
            return response
            
        except Exception as e:
            raise Http404(f"Fichier introuvable: {str(e)}")
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def restore_version(self, request, pk=None):
        """
        Restaure une ancienne version comme version courante.
        POST /documents/{id}/restore-version/
        """
        old_document = self.get_object()
        
        if old_document.is_current_version:
            raise ValidationError({'detail': "Ce document est déjà la version courante"})
        
        # Trouver la version courante actuelle
        current = Document.objects.get(
            dossier=old_document.dossier,
            original_filename=old_document.original_filename,
            is_current_version=True
        )
        
        # Archiver l'actuelle
        current.is_current_version = False
        current.save(update_fields=['is_current_version'])
        
        # Restaurer l'ancienne comme nouvelle version
        restored = Document.objects.create(
            dossier=old_document.dossier,
            folder=old_document.folder,
            file=old_document.file,
            title=old_document.title,
            description=f"[RESTAURÉE] {old_document.description}",
            original_filename=old_document.original_filename,
            sensitivity=old_document.sensitivity,
            retention_until=old_document.retention_until,
            uploaded_by=request.user,
            version=current.version + 1,
            is_current_version=True,
            previous_version=current
        )
        
        log_action(
            user=request.user,
            obj=restored,
            action_type='RESTORE',
            description=f"Restauration version {old_document.version} → {restored.version}",
            changes={'restored_from': str(old_document.id)}
        )
        
        return Response(
            DocumentSerializer(restored, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def verify_integrity(self, request, pk=None):
        """
        Vérifie l'intégrité cryptographique du fichier.
        POST /documents/{id}/verify-integrity/
        """
        document = self.get_object()
        is_valid = document.verify_integrity()
        
        log_action(
            user=request.user,
            obj=document,
            action_type='INTEGRITY_CHECK',
            description=f"Vérification intégrité: {'OK' if is_valid else 'ÉCHEC'}",
            changes={'integrity_valid': is_valid}
        )
        
        return Response({
            'id': str(document.id),
            'title': document.title,
            'file_hash': document.file_hash,
            'integrity_valid': is_valid,
            'message': 'Intégrité vérifiée avec succès' if is_valid else 'ALERTE: Fichier corrompu ou modifié'
        })
