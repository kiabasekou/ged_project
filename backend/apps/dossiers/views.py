# backend/apps/dossiers/views.py

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from django.db.models import Count, Prefetch, Q
from django.utils import timezone

from django_filters.rest_framework import DjangoFilterBackend

from .models import Dossier
from apps.documents.models import Folder
from .serializers import DossierListSerializer, DossierDetailSerializer, FolderSerializer
from apps.audit.utils import log_action
from apps.users.models import User  # Pour les annotations si besoin
from rest_framework_guardian.filters import ObjectPermissionsFilter
from guardian.shortcuts import assign_perm, remove_perm

class DossierViewSet(viewsets.ModelViewSet):
    """
    ViewSet complet pour la gestion des dossiers juridiques et notariaux.
    
    Fonctionnalités clés :
    - Recherche avancée (référence, titre, client, responsable, catégorie)
    - Filtrage par statut, catégorie, responsable, client, délais critiques
    - Annotation du nombre de documents et répertoires (performance + UX)
    - Actions sécurisées : clôturer, archiver, assigner utilisateurs
    - Audit complet de toutes les actions sensibles
    - Alerte automatique sur les dossiers en dépassement de délai
    - Préparé pour Django Guardian (permissions object-level par dossier)
    """
    permission_classes = [IsAuthenticated, DjangoObjectPermissions]
    filter_backends = [ObjectPermissionsFilter, DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Le reste de ton code (get_queryset, etc.) reste identique

    def perform_create(self, serializer):
        dossier = serializer.save(responsible=self.request.user)
        
        # Le responsable obtient toutes les permissions sur son dossier
        assign_perm('view_dossier', self.request.user, dossier)
        assign_perm('change_dossier', self.request.user, dossier)
        assign_perm('delete_dossier', self.request.user, dossier)
        assign_perm('assign_dossier', self.request.user, dossier)

        # Les assigned_users (si ajoutés au moment de la création) obtiennent view
        for user in dossier.assigned_users.all():
            assign_perm('view_dossier', user, dossier)
            assign_perm('view_document', user, dossier)  # Pour voir les docs du dossier

        log_action(
            user=self.request.user,
            obj=dossier,
            action='CREATE',
            description="Création d'un nouveau dossier avec permissions assignées",
            request=self.request
        )




    def get_serializer_class(self):
        """Liste légère pour l'affichage rapide, détail complet pour édition"""
        if self.action == 'list':
            return DossierListSerializer
        return DossierDetailSerializer

    # Backends de filtrage, recherche et tri
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # Filtres très utiles pour un cabinet
    filterset_fields = {
        'status': ['exact', 'in'],
        'category': ['exact', 'in'],
        'client': ['exact'],
        'responsible': ['exact'],
        'assigned_users': ['exact'],
        'critical_deadline': ['gte', 'lte', 'exact'],
        'opening_date': ['gte', 'lte', 'year', 'month'],
        #'is_active': ['exact'],  # Si tu ajoutes un champ is_active sur Dossier
    }

    # Recherche intelligente
    search_fields = [
        '=reference_code',           # Recherche exacte prioritaire sur référence
        '^title',                    # Commence par le titre
        'description',
        'client__display_name',
        'client__company_name',
        'client__nif',
        'client__rccm',
        'opponent',
        'jurisdiction',
    ]

    # Tri pertinent
    ordering_fields = [
        'reference_code',
        'title',
        'opening_date',
        'closing_date',
        'critical_deadline',
        'status',
        'category',
        'created_at',
        'document_count',
        'folder_count',
    ]
    ordering = ['-opening_date', '-critical_deadline']

    def get_queryset(self):
        """
        Optimisation massive :
        - select_related pour client et responsible
        - prefetch pour assigned_users et folders
        - annotations : nombre de documents et répertoires
        - indicateur de dépassement de délai
        """
        qs = Dossier.objects.select_related('client', 'responsible') \
                            .prefetch_related('assigned_users', 'folders')

        # Annotations utiles pour la liste
        qs = qs.annotate(
            document_count=Count('documents', distinct=True),
            folder_count=Count('folders', distinct=True),
        )

        # Optionnel : filtrer les dossiers archivés par défaut
        if 'status' not in self.request.query_params:
            qs = qs.exclude(status=Dossier.Status.ARCHIVED)

        return qs

    # === Actions avec audit ===

    def perform_create(self, serializer):
        dossier = serializer.save()
        log_action(
            user=self.request.user,
            obj=dossier,
            action='CREATE',
            description="Création d'un nouveau dossier juridique/notarial",
            request=self.request
        )

    def perform_update(self, serializer):
        dossier = serializer.save()
        log_action(
            user=self.request.user,
            obj=dossier,
            action='UPDATE',
            changes=serializer.validated_data,
            description="Modification d'un dossier",
            request=self.request
        )

    def perform_destroy(self, instance):
        """Soft delete ou archivage automatique"""
        instance.status = Dossier.Status.ARCHIVED
        instance.archived_date = timezone.now()
        instance.save(update_fields=['status', 'archived_date'])

        log_action(
            user=self.request.user,
            obj=instance,
            action='DELETE',
            description="Archivage du dossier",
            request=self.request
        )

    # === Actions personnalisées ===

    @action(detail=True, methods=['post'], url_path='cloturer')
    def cloturer(self, request, pk=None):
        """
        Clôture officielle du dossier.
        - Met le statut à CLOTURE
        - Remplit automatiquement closing_date si vide
        """
        dossier = self.get_object()

        if dossier.status == Dossier.Status.CLOSED:
            return Response(
                {"detail": "Ce dossier est déjà clôturé."},
                status=status.HTTP_400_BAD_REQUEST
            )

        dossier.status = Dossier.Status.CLOSED
        if not dossier.closing_date:
            dossier.closing_date = timezone.now().date()

        dossier.save()

        log_action(
            user=request.user,
            obj=dossier,
            action='UPDATE',
            description="Clôture officielle du dossier",
            request=request
        )

        return Response({"detail": "Dossier clôturé avec succès."})

    @action(detail=True, methods=['post'], url_path='archiver')
    def archiver(self, request, pk=None):
        """Archivage manuel (différent de la suppression)"""
        dossier = self.get_object()

        if dossier.status == Dossier.Status.ARCHIVED:
            return Response(
                {"detail": "Ce dossier est déjà archivé."},
                status=status.HTTP_400_BAD_REQUEST
            )

        dossier.status = Dossier.Status.ARCHIVED
        dossier.archived_date = timezone.now()
        dossier.save()

        log_action(
            user=request.user,
            obj=dossier,
            action='UPDATE',
            description="Archivage manuel du dossier",
            request=request
        )

        return Response({"detail": "Dossier archivé avec succès."})

    @action(detail=True, methods=['get'], url_path='folders')
    def list_folders(self, request, pk=None):
        """Liste l'arborescence des répertoires du dossier"""
        dossier = self.get_object()
        folders = dossier.folders.all()
        serializer = FolderSerializer(folders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Statistiques globales pour le dashboard (Optimisées)"""
        # On récupère le queryset filtré selon les droits de l'utilisateur
        qs = self.filter_queryset(self.get_queryset())
        
        # Récupération de la date du jour (Libreville) pour le calcul du retard
        today = timezone.now().date()

        stats = {
            "total": qs.count(),
            "ouverts": qs.filter(status=Dossier.Status.OPEN).count(),
            "en_attente": qs.filter(status=Dossier.Status.PENDING).count(),
            "clotures": qs.filter(status=Dossier.Status.CLOSED).count(),
            # CORRECTION : Filtrage par date réelle au lieu de la propriété Python
            "en_retard": qs.filter(
                status=Dossier.Status.OPEN, 
                critical_deadline__lt=today
            ).count(),
            "par_categorie": dict(
                qs.values('category')
                  .annotate(count=Count('category'))
                  .values_list('category', 'count')
            ),
        }

        return Response(stats)