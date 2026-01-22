# backend/apps/clients/views.py

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone

from django_filters.rest_framework import DjangoFilterBackend

from .models import Client
from .serializers import ClientSerializer, ClientListSerializer
from apps.audit.utils import log_action  # Fonction helper pour audit (à créer si pas déjà fait)


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet complet pour la gestion des clients (Personnes Physiques et Morales).
    Adapté aux cabinets d'avocats et notaires au Gabon et zone OHADA.

    Fonctionnalités :
    - Recherche puissante (nom, raison sociale, NIF, RCCM, téléphone, email)
    - Filtrage par type, ville, quartier, activité
    - Tri intelligent
    - Audit complet des actions sensibles
    - Soft delete (désactivation)
    """
    queryset = Client.objects.select_related().all()
    permission_classes = [IsAuthenticated]

    # Serializers dynamiques : liste légère, détail complet
    def get_serializer_class(self):
        if self.action == 'list':
            return ClientListSerializer
        return ClientSerializer

    # Filtrage, recherche et tri
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # Filtres utiles pour un cabinet à Libreville ou ailleurs au Gabon
    filterset_fields = {
        'client_type': ['exact'],
        'city': ['exact', 'icontains'],
        'neighborhood': ['exact', 'icontains'],
        'is_active': ['exact'],
        'consent_given': ['exact'],
        'created_at': ['gte', 'lte', 'exact'],
    }

    # Recherche plein texte performante sur les champs clés
    search_fields = [
        'first_name',
        'last_name',
        'company_name',
        'rccm',
        'nif',
        'ni_number',
        'email',
        'phone_primary',
        'phone_secondary',
        'representative_name',
    ]

    # Tri par défaut et autorisé
    ordering_fields = [
        'created_at',
        'last_name',
        'first_name',
        'company_name',
        'city',
        'nif',
        'rccm',
        'is_active',
    ]
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Optimisation + annotations utiles pour la liste
        - Compte le nombre de dossiers par client (très utile dans l'interface)
        - Filtre les clients inactifs en option
        """
        qs = Client.objects.all()

        # Annotation : nombre de dossiers liés
        qs = qs.annotate(dossier_count=Count('dossiers'))

        # Optionnel : cacher les clients inactifs par défaut (toggle via filtre)
        if not self.request.query_params.get('is_active') in ['false', '0']:
            qs = qs.filter(is_active=True)

        return qs.order_by(*self.ordering)

    def perform_create(self, serializer):
        """Création avec audit"""
        client = serializer.save()
        log_action(
            user=self.request.user,
            obj=client,
            action='CREATE',
            description="Création d'un nouveau client",
            request=self.request
        )

    def perform_update(self, serializer):
        """Modification avec audit des changements"""
        old_client = self.get_object()
        client = serializer.save()
        log_action(
            user=self.request.user,
            obj=client,
            action='UPDATE',
            changes=serializer.validated_data,
            description="Modification des informations client",
            request=self.request
        )

    def perform_destroy(self, instance):
        """Soft delete : désactivation + audit"""
        if not instance.is_active:
            return  # Déjà inactif

        instance.is_active = False
        instance.save(update_fields=['is_active'])

        log_action(
            user=self.request.user,
            obj=instance,
            action='DELETE',
            description="Désactivation du client (soft delete)",
            request=self.request
        )

    @action(detail=True, methods=['post'], url_path='grant-consent')
    def grant_consent(self, request, pk=None):
        """
        Action sécurisée pour enregistrer le consentement RGPD du client.
        Utile lors de la signature physique de la convention ou de l'acte.
        """
        client = self.get_object()

        if client.consent_given:
            return Response(
                {"detail": "Le consentement a déjà été enregistré pour ce client."},
                status=status.HTTP_200_OK
            )

        client.grant_consent()  # Méthode du modèle

        log_action(
            user=request.user,
            obj=client,
            action='CONSENT',
            description="Consentement RGPD accordé pour le client",
            request=request
        )

        return Response(
            {"detail": "Consentement RGPD enregistré avec succès."},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        Statistiques rapides pour le dashboard cabinet
        Ex. : Nombre de clients actifs, par type, par ville
        """
        qs = self.get_queryset()

        stats = {
            "total_clients": qs.count(),
            "clients_physiques": qs.filter(client_type=Client.ClientType.INDIVIDUAL).count(),
            "clients_moraux": qs.filter(client_type=Client.ClientType.COMPANY).count(),
            "clients_libreville": qs.filter(city__icontains="Libreville").count(),
            "clients_actifs": qs.filter(is_active=True).count(),
            "avec_dossiers": qs.filter(dossier_count__gt=0).count(),
        }

        return Response(stats)