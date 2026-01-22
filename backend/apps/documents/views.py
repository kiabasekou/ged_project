import os
from django.http import FileResponse, Http404
from django.utils import timezone
from django.db.models import Count
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_guardian.filters import ObjectPermissionsFilter

# Correction Import : Guardian est nécessaire pour assign_perm
try:
    from guardian.shortcuts import assign_perm
except ImportError:
    assign_perm = None

from .models import Folder, Document
from .serializers import (
    FolderSerializer, 
    FolderTreeSerializer,
    DocumentListSerializer, 
    DocumentDetailSerializer
)
from apps.audit.utils import log_action

# ======================
# FOLDER VIEWSET
# ======================
class FolderViewSet(viewsets.ModelViewSet):
    """
    Gestion de l'arborescence virtuelle.
    Optimisé pour un rendu rapide des dossiers du cabinet.
    """
    permission_classes = [IsAuthenticated]
    queryset = Folder.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dossier', 'parent']

    def get_queryset(self):
        # Utilisation de select_related pour éviter les requêtes N+1 sur l'auteur
        return Folder.objects.select_related('dossier', 'created_by') \
                             .annotate(
                                 document_count=Count('documents', distinct=True),
                                 subfolder_count=Count('subfolders', distinct=True)
                             )

    def get_serializer_class(self):
        # Utilise l'arbre pour la liste, le plat pour la création/édition
        if self.action == 'list':
            return FolderTreeSerializer
        return FolderSerializer

    def perform_create(self, serializer):
        folder = serializer.save(created_by=self.request.user)
        log_action(
            user=self.request.user,
            obj=folder,
            action='CREATE',
            description=f"Création du répertoire : {folder.name}",
            request=self.request
        )

    def perform_destroy(self, instance):
        log_action(
            user=self.request.user, obj=instance, action='DELETE',
            description=f"Suppression du répertoire : {instance.name}",
            request=self.request
        )
        instance.delete()

# ======================
# DOCUMENT VIEWSET
# ======================
class DocumentViewSet(viewsets.ModelViewSet):
    """
    Gestion documentaire avancée : Versioning, Audit et Sécurité.
    """
    permission_classes = [IsAuthenticated, DjangoObjectPermissions]
    # Consolidation des backends de filtrage (suppression du doublon)
    filter_backends = [
        ObjectPermissionsFilter, 
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]

    filterset_fields = {
        'dossier': ['exact'],
        'folder': ['exact', 'isnull'],
        'is_current_version': ['exact'],
        'sensitivity': ['exact'],
        'file_extension': ['exact', 'in'],
        'uploaded_by': ['exact'],
        'uploaded_at': ['gte', 'lte'],
    }

    search_fields = ['^title', 'description', 'original_filename']
    ordering_fields = ['uploaded_at', 'title', 'version', 'file_size']
    ordering = ['-uploaded_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentListSerializer
        return DocumentDetailSerializer

    def get_queryset(self):
        # Prefetch_related sur next_versions pour éviter les lenteurs lors du listing des versions
        return Document.objects.select_related(
            'dossier', 'uploaded_by', 'folder'
        ).prefetch_related('next_versions')
    
    def perform_create(self, serializer):
        # CORRECTION : Une seule sauvegarde pour éviter les doublons de création
        document = serializer.save(uploaded_by=self.request.user)
        
        # Gestion automatique des permissions (Guardian)
        if assign_perm:
            assign_perm('view_document', self.request.user, document)
            assign_perm('download_document', self.request.user, document)

        log_action(
            user=self.request.user,
            obj=document,
            action='CREATE',
            description=f"Upload du document : {document.title} (v{document.version})",
            request=self.request
        )

    def perform_destroy(self, instance):
        # Suppression sécurisée du fichier physique avant suppression en base
        log_action(
            user=self.request.user, obj=instance, action='DELETE',
            description=f"Suppression définitive du document : {instance.title}",
            request=self.request
        )
        if instance.file and os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
        instance.delete()

    # === ACTIONS MÉTIER ===

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        """Streaming sécurisé pour gros fichiers (Pleadings, Actes)"""
        document = self.get_object()

        if not document.file or not os.path.exists(document.file.path):
            raise Http404("Le fichier physique est introuvable sur le stockage.")

        log_action(
            user=request.user, obj=document, action='DOWNLOAD',
            description=f"Téléchargement du document : {document.title}",
            request=request
        )

        response = FileResponse(
            document.file.open('rb'),
            content_type=document.mime_type or 'application/octet-stream'
        )
        # Nettoyage du nom de fichier pour éviter les erreurs d'encodage header
        safe_name = document.title.replace('"', '')
        response['Content-Disposition'] = f'attachment; filename="{safe_name}{document.file_extension}"'
        response['Content-Length'] = document.file_size
        return response

    @action(detail=True, methods=['post'], url_path='nouvelle-version')
    def new_version(self, request, pk=None):
        """Incrémente la version et désactive l'ancienne (Atomic)"""
        old_doc = self.get_object()

        if not old_doc.is_current_version:
            return Response(
                {"detail": "Action impossible sur une archive."},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_file = request.FILES.get('file')
        if not new_file:
            return Response({"detail": "Fichier manquant."}, status=status.HTTP_400_BAD_REQUEST)

        new_doc = old_doc.create_new_version(new_file=new_file, user=request.user)

        log_action(
            user=request.user, obj=new_doc, action='CREATE',
            description=f"Nouvelle version v{new_doc.version} créée",
            request=request
        )

        return Response(DocumentDetailSerializer(new_doc, context={'request': request}).data)

    @action(detail=True, methods=['get'], url_path='versions')
    def versions(self, request, pk=None):
        """Récupère l'historique complet par remontée de chaîne"""
        document = self.get_object()
        history = []
        curr = document
        while curr:
            history.append(curr)
            curr = curr.previous_version
        
        # On retourne l'historique du plus ancien au plus récent
        serializer = DocumentListSerializer(reversed(history), many=True, context={'request': request})
        return Response(serializer.data)