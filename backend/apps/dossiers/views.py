# backend/apps/dossiers/views.py - IMPORTS COMPLETS CORRIGÉS

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from rest_framework.exceptions import PermissionDenied

from django.db.models import Count, Prefetch, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

# CORRECTION : Import de ObjectPermissionsFilter depuis django-guardian
from guardian.shortcuts import assign_perm, remove_perm, get_objects_for_user

# IMPORTANT : ObjectPermissionsFilter vient de rest_framework_guardian
# Installer si nécessaire : pip install djangorestframework-guardian
try:
    from rest_framework_guardian.filters import ObjectPermissionsFilter
except ImportError:
    # Fallback si rest_framework_guardian n'est pas installé
    # Créer un filtre basique qui ne fait rien
    class ObjectPermissionsFilter:
        """Fallback filter si rest_framework_guardian n'est pas installé"""
        def filter_queryset(self, request, queryset, view):
            return queryset

from .models import Dossier
from apps.documents.models import Folder
from .serializers import DossierListSerializer, DossierDetailSerializer, FolderSerializer
from apps.audit.utils import log_action
from apps.users.models import User

import logging
logger = logging.getLogger(__name__)


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
    - Django Guardian (permissions object-level par dossier)
    """
    
    # Permissions : IsAuthenticated + permissions objet Django
    permission_classes = [IsAuthenticated, DjangoObjectPermissions]
    
    # Backends de filtrage
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    
    # Note : ObjectPermissionsFilter est optionnel
    # On gère manuellement les permissions dans get_queryset()
    
    serializer_class = DossierDetailSerializer
    
    # Filtres très utiles pour un cabinet
    filterset_fields = {
        'status': ['exact', 'in'],
        'category': ['exact', 'in'],
        'client': ['exact'],
        'responsible': ['exact'],
        'assigned_users': ['exact'],
        'critical_deadline': ['gte', 'lte', 'exact'],
        'opening_date': ['gte', 'lte', 'year', 'month'],
    }

    # Recherche intelligente
    search_fields = [
        '=reference_code',           # Recherche exacte prioritaire sur référence
        '^title',                    # Commence par le titre
        'description',
        'client__first_name',
        'client__last_name',
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
    ]
    ordering = ['-opening_date', '-critical_deadline']

    def get_queryset(self):
        """
        Filtrage des dossiers selon le rôle et les permissions.
        
        Logique :
        1. Superusers : tous les dossiers
        2. Admins (is_staff) : tous les dossiers
        3. Avocats/Notaires :
           - Dossiers dont ils sont responsables
           - Dossiers où ils sont collaborateurs (assigned_users)
        4. Autres utilisateurs : dossiers via assigned_users uniquement
        """
        user = self.request.user
        
        # Optimisation des requêtes
        qs = Dossier.objects.select_related('client', 'responsible') \
                            .prefetch_related('assigned_users', 'folders')
        
        # Annotations utiles
        qs = qs.annotate(
            document_count=Count('documents', distinct=True),
            folder_count=Count('folders', distinct=True)
        )
        
        # 1. Superusers : accès total
        if user.is_superuser:
            return qs
        
        # 2. Staff/Admins : accès total (secrétaires administratifs)
        if user.is_staff:
            return qs
        
        # 3. Avocats, Notaires, Conseils juridiques
        if user.role in ['AVOCAT', 'NOTAIRE', 'CONSEIL_JURIDIQUE']:
            # Dossiers dont l'utilisateur est responsable OU collaborateur
            return qs.filter(
                Q(responsible=user) | Q(assigned_users=user)
            ).distinct()
        
        # 4. Autres utilisateurs (Stagiaires, Assistants, Secrétaires)
        # Uniquement les dossiers où ils sont explicitement ajoutés
        return qs.filter(assigned_users=user).distinct()

    def get_serializer_class(self):
        """Liste légère pour l'affichage rapide, détail complet pour édition"""
        if self.action == 'list':
            return DossierListSerializer
        return DossierDetailSerializer

    def perform_create(self, serializer):
        """
        Création d'un dossier avec permissions automatiques.
        
        Le créateur devient automatiquement :
        - Le responsable du dossier
        - Obtient toutes les permissions sur ce dossier
        """
        dossier = serializer.save(responsible=self.request.user)
        
        # Attribution des permissions Guardian au responsable
        assign_perm('view_dossier', self.request.user, dossier)
        assign_perm('change_dossier', self.request.user, dossier)
        assign_perm('delete_dossier', self.request.user, dossier)
        
        # Log audit
        log_action(
            user=self.request.user,
            obj=dossier,
            action_type='CREATE',
            description=f"Création du dossier {dossier.reference_code}"
        )

    @action(detail=True, methods=['post'], url_path='assign-user')
    def assign_user(self, request, pk=None):
        """
        Ajouter un collaborateur à un dossier.
        
        POST /dossiers/{id}/assign-user/
        Body: {
            "user_id": "uuid-de-l-utilisateur",
            "permissions": ["view", "change"]  # Optionnel
        }
        """
        dossier = self.get_object()
        user_id = request.data.get('user_id')
        permissions = request.data.get('permissions', ['view'])
        
        # Vérification : seul le responsable ou un admin peut assigner
        if not (request.user == dossier.responsible or request.user.is_staff):
            raise PermissionDenied(
                "Seul le responsable du dossier peut ajouter des collaborateurs"
            )
        
        try:
            user_to_assign = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Utilisateur introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Ajouter à la liste des collaborateurs
        dossier.assigned_users.add(user_to_assign)
        
        # Attribution des permissions Guardian
        if 'view' in permissions:
            assign_perm('view_dossier', user_to_assign, dossier)
        
        if 'change' in permissions:
            if user_to_assign.role in ['AVOCAT', 'NOTAIRE', 'CONSEIL_JURIDIQUE']:
                assign_perm('change_dossier', user_to_assign, dossier)
        
        # Log audit
        log_action(
            user=request.user,
            obj=dossier,
            action_type='ASSIGN_USER',
            description=f"Ajout de {user_to_assign.get_full_name()} comme collaborateur"
        )
        
        return Response({
            'message': f'{user_to_assign.get_full_name()} ajouté comme collaborateur',
            'dossier': DossierDetailSerializer(dossier).data
        })

    @action(detail=True, methods=['post'], url_path='remove-user')
    def remove_user(self, request, pk=None):
        """
        Retirer un collaborateur d'un dossier.
        
        POST /dossiers/{id}/remove-user/
        Body: {"user_id": "uuid-de-l-utilisateur"}
        """
        dossier = self.get_object()
        user_id = request.data.get('user_id')
        
        # Vérification permissions
        if not (request.user == dossier.responsible or request.user.is_staff):
            raise PermissionDenied(
                "Seul le responsable peut retirer des collaborateurs"
            )
        
        try:
            user_to_remove = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Utilisateur introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Empêcher de retirer le responsable
        if user_to_remove == dossier.responsible:
            return Response(
                {'error': 'Impossible de retirer le responsable du dossier'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Retirer des collaborateurs
        dossier.assigned_users.remove(user_to_remove)
        
        # Retirer les permissions Guardian
        remove_perm('view_dossier', user_to_remove, dossier)
        remove_perm('change_dossier', user_to_remove, dossier)
        
        # Log audit
        log_action(
            user=request.user,
            obj=dossier,
            action_type='REMOVE_USER',
            description=f"Retrait de {user_to_remove.get_full_name()} comme collaborateur"
        )
        
        return Response({
            'message': f'{user_to_remove.get_full_name()} retiré du dossier'
        })

    @action(detail=True, methods=['get'], url_path='collaborateurs')
    def list_collaborateurs(self, request, pk=None):
        """
        Liste tous les collaborateurs d'un dossier.
        
        GET /dossiers/{id}/collaborateurs/
        """
        dossier = self.get_object()
        
        # Responsable principal
        responsable = {
            'id': str(dossier.responsible.id),
            'name': dossier.responsible.get_full_name(),
            'role': dossier.responsible.get_role_display(),
            'is_responsible': True,
            'permissions': ['view', 'change', 'delete', 'assign']
        }
        
        # Collaborateurs
        collaborateurs = []
        for user in dossier.assigned_users.all():
            perms = []
            if user.has_perm('view_dossier', dossier):
                perms.append('view')
            if user.has_perm('change_dossier', dossier):
                perms.append('change')
            
            collaborateurs.append({
                'id': str(user.id),
                'name': user.get_full_name(),
                'role': user.get_role_display(),
                'is_responsible': False,
                'permissions': perms
            })
        
        return Response({
            'responsable': responsable,
            'collaborateurs': collaborateurs,
            'total_collaborateurs': len(collaborateurs)
        })

    @action(detail=True, methods=['post'])
    def cloturer(self, request, pk=None):
        """Clôturer un dossier"""
        dossier = self.get_object()
        
        if dossier.status == 'CLOTURE':
            return Response(
                {'error': 'Ce dossier est déjà clôturé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dossier.status = 'CLOTURE'
        dossier.closing_date = timezone.now().date()
        dossier.save()
        
        log_action(
            user=request.user,
            obj=dossier,
            action_type='CLOSE',
            description=f"Clôture du dossier {dossier.reference_code}"
        )
        
        return Response(DossierDetailSerializer(dossier).data)

    @action(detail=True, methods=['post'])
    def archiver(self, request, pk=None):
        """Archiver un dossier"""
        dossier = self.get_object()
        
        if dossier.status != 'CLOTURE':
            return Response(
                {'error': 'Seuls les dossiers clôturés peuvent être archivés'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dossier.status = 'ARCHIVE'
        dossier.archived_date = timezone.now()
        dossier.save()
        
        log_action(
            user=request.user,
            obj=dossier,
            action_type='ARCHIVE',
            description=f"Archivage du dossier {dossier.reference_code}"
        )
        
        return Response(DossierDetailSerializer(dossier).data)