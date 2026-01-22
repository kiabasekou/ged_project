from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import User
from .serializers import (
    UserMinimalSerializer, 
    UserListSerializer, 
    UserDetailSerializer, 
    UserProfileUpdateSerializer
)
# Helper pour l'audit trail
from apps.audit.utils import log_action 


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Permission : l'utilisateur accède à son propre profil, 
    l'admin accède à tout le cabinet.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN or request.user.is_superuser:
            return True
        return obj == request.user


class IsAdminUser(permissions.BasePermission):
    """Accès réservé aux administrateurs système du cabinet."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == User.Role.ADMIN or request.user.is_superuser
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    Gestion des utilisateurs du cabinet.
    Optimisé pour différencier les vues liste, détail et mise à jour.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """
        Retourne le serializer adapté à l'action en cours.
        """
        if self.action == 'list':
            return UserListSerializer
        if self.action == 'update_profile':
            return UserProfileUpdateSerializer
        if self.action in ['retrieve', 'me']:
            return UserDetailSerializer
        return UserDetailSerializer

    def get_permissions(self):
        """Définit les permissions dynamiquement selon l'action."""
        if self.action in ['list', 'create', 'destroy']:
            return [IsAdminUser()]
        if self.action in ['retrieve', 'update', 'partial_update']:
            return [IsSelfOrAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        """
        Filtre les résultats selon les droits d'accès :
        - Admin : liste complète triée par date d'arrivée.
        - Utilisateur standard : restreint à son propre profil.
        """
        qs = User.objects.all()
        if self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser:
            return qs.order_by('-date_joined')
        return qs.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """Endpoint pour charger le profil complet de l'utilisateur connecté."""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], url_path='update-profile')
    def update_profile(self, request):
        """
        Mise à jour autonome. Le serializer UserProfileUpdateSerializer 
        gère la restriction des champs modifiables (email, téléphone, etc.).
        """
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        log_action(
            user=request.user,
            content_object=user,
            action_type='UPDATE',
            description="Mise à jour autonome du profil utilisateur",
            request=request
        )

        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='accept-privacy')
    def accept_privacy(self, request, pk=None):
        """Enregistre l'acceptation de la politique de confidentialité (Gabon)."""
        user = self.get_object()
        
        if user.has_accepted_privacy_policy:
            return Response(
                {"detail": "Consentement déjà enregistré."}, 
                status=status.HTTP_200_OK
            )

        user.accept_privacy_policy()

        log_action(
            user=request.user,
            content_object=user,
            action_type='UPDATE',
            description=f"Consentement RGPD validé par {request.user.username}",
            request=request
        )

        return Response({"detail": "Consentement enregistré avec succès."})

    def perform_create(self, serializer):
        user = serializer.save()
        log_action(
            user=self.request.user,
            content_object=user,
            action_type='CREATE',
            description=f"Création de l'utilisateur : {user.username}",
            request=self.request
        )

    def perform_update(self, serializer):
        user = serializer.save()
        log_action(
            user=self.request.user,
            content_object=user,
            action_type='UPDATE',
            description="Modification des données utilisateur par l'administrateur",
            request=self.request
        )

    def perform_destroy(self, instance):
        """Désactivation (Soft Delete) pour conserver l'historique des dossiers."""
        instance.is_active = False
        instance.save()
        log_action(
            user=self.request.user,
            content_object=instance,
            action_type='DELETE',
            description=f"Désactivation du compte : {instance.username}",
            request=self.request
        )