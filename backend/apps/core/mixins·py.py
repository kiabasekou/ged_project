"""
Mixins réutilisables pour l'application GED Cabinet.
"""
from django.db import models
from django.utils import timezone
from rest_framework import serializers
from rest_framework.permissions import BasePermission


class SoftDeleteMixin:
    """
    Mixin pour gérer le soft-delete sur les ViewSets DRF.
    À utiliser avec des modèles ayant un champ is_active.
    """
    
    def perform_destroy(self, instance):
        """Override destroy pour faire un soft-delete au lieu de supprimer"""
        instance.soft_delete()
        
        # Log audit si disponible
        if hasattr(self, '_log_audit'):
            self._log_audit(instance, 'SOFT_DELETE', 'Désactivation (soft-delete)')


class AuditTrailMixin:
    """
    Mixin pour ajouter automatiquement l'audit trail aux ViewSets.
    Requiert apps.audit installée.
    """
    
    def _log_audit(self, instance, action_type: str, description: str = "", changes: dict = None):
        """Helper pour créer une entrée d'audit"""
        from apps.audit.utils import log_action
        
        log_action(
            user=self.request.user,
            obj=instance,
            action_type=action_type,
            description=description,
            changes=changes,
            request=self.request
        )
    
    def perform_create(self, serializer):
        """Override create pour ajouter audit"""
        instance = serializer.save()
        self._log_audit(instance, 'CREATE', f"Création de {instance}")
        return instance
    
    def perform_update(self, serializer):
        """Override update pour ajouter audit avec changements"""
        old_instance = self.get_object()
        
        # Capturer les changements
        changes = {}
        for field in serializer.validated_data.keys():
            old_value = getattr(old_instance, field, None)
            new_value = serializer.validated_data[field]
            if old_value != new_value:
                changes[field] = {'old': str(old_value), 'new': str(new_value)}
        
        instance = serializer.save()
        self._log_audit(instance, 'UPDATE', f"Modification de {instance}", changes)
        return instance


class TimestampMixin(models.Model):
    """
    Mixin pour ajouter created_at et updated_at à un modèle.
    Alternative légère à BaseModel.
    """
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        abstract = True


class UserTrackingMixin(models.Model):
    """
    Mixin pour tracker created_by et updated_by.
    """
    
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        abstract = True


class RGPDMixin(models.Model):
    """
    Mixin pour conformité RGPD.
    Ajoute les champs de consentement et rétention.
    """
    
    data_source = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Source des données",
        help_text="Origine des données personnelles"
    )
    
    consent_given = models.BooleanField(
        default=False,
        verbose_name="Consentement donné",
        help_text="La personne a consenti au traitement de ses données"
    )
    
    consent_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de consentement"
    )
    
    retention_period_years = models.PositiveIntegerField(
        default=10,
        verbose_name="Période de rétention (années)",
        help_text="Durée de conservation des données"
    )
    
    class Meta:
        abstract = True
    
    def calculate_retention_date(self):
        """Calcule la date limite de rétention"""
        from apps.core.utils import calculate_retention_date
        return calculate_retention_date(self.retention_period_years, self.created_at)
    
    def is_retention_expired(self):
        """Vérifie si la période de rétention est expirée"""
        retention_date = self.calculate_retention_date()
        return timezone.now() > retention_date


class SerializerValidationMixin:
    """
    Mixin pour ajouter des validations communes aux serializers.
    """
    
    def validate_not_empty(self, value, field_name: str):
        """Valide qu'un champ n'est pas vide"""
        if not value or (isinstance(value, str) and not value.strip()):
            raise serializers.ValidationError(
                f"Le champ {field_name} ne peut pas être vide."
            )
        return value
    
    def validate_positive_number(self, value, field_name: str):
        """Valide qu'un nombre est positif"""
        if value is not None and value < 0:
            raise serializers.ValidationError(
                f"Le champ {field_name} doit être positif."
            )
        return value
    
    def validate_future_date(self, value, field_name: str):
        """Valide qu'une date est dans le futur"""
        if value and value <= timezone.now().date():
            raise serializers.ValidationError(
                f"Le champ {field_name} doit être une date future."
            )
        return value


class OwnerPermissionMixin(BasePermission):
    """
    Permission mixin : l'utilisateur doit être propriétaire de l'objet.
    """
    
    owner_field = 'created_by'  # Nom du champ contenant le propriétaire
    
    def has_object_permission(self, request, view, obj):
        """Vérifie que l'utilisateur est le propriétaire"""
        if request.user.is_superuser:
            return True
        
        owner = getattr(obj, self.owner_field, None)
        return owner == request.user


class ReadOnlyForInactiveMixin:
    """
    Mixin pour rendre les objets inactifs (soft-deleted) en lecture seule.
    """
    
    def get_queryset(self):
        """Override pour exclure les objets inactifs par défaut"""
        queryset = super().get_queryset()
        
        # Montrer uniquement les objets actifs sauf si explicitement demandé
        if self.action in ['list', 'retrieve']:
            show_inactive = self.request.query_params.get('show_inactive', 'false')
            if show_inactive.lower() != 'true':
                queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def perform_update(self, serializer):
        """Empêche la modification d'objets inactifs"""
        instance = self.get_object()
        
        if hasattr(instance, 'is_active') and not instance.is_active:
            from apps.core.exceptions import ValidationError
            raise ValidationError("Impossible de modifier un objet désactivé.")
        
        return super().perform_update(serializer)


class BulkActionMixin:
    """
    Mixin pour ajouter des actions en masse aux ViewSets.
    """
    
    def bulk_update_field(self, queryset, field: str, value):
        """Update en masse d'un champ"""
        count = queryset.update(**{field: value})
        return {
            'updated': count,
            'field': field,
            'value': value
        }
    
    def bulk_soft_delete(self, queryset):
        """Soft delete en masse"""
        count = queryset.update(is_active=False)
        return {
            'soft_deleted': count
        }
    
    def bulk_restore(self, queryset):
        """Restauration en masse"""
        count = queryset.update(is_active=True)
        return {
            'restored': count
        }


class CacheInvalidationMixin:
    """
    Mixin pour invalider automatiquement le cache lors de modifications.
    """
    
    cache_key_prefix = None  # À définir dans la classe enfant
    
    def _get_cache_key(self, obj):
        """Génère la clé de cache pour un objet"""
        if not self.cache_key_prefix:
            return None
        return f"{self.cache_key_prefix}:{obj.pk}"
    
    def _invalidate_cache(self, obj):
        """Invalide le cache pour un objet"""
        from django.core.cache import cache
        
        cache_key = self._get_cache_key(obj)
        if cache_key:
            cache.delete(cache_key)
    
    def perform_update(self, serializer):
        """Invalide le cache après update"""
        instance = super().perform_update(serializer)
        self._invalidate_cache(instance)
        return instance
    
    def perform_destroy(self, instance):
        """Invalide le cache après delete"""
        self._invalidate_cache(instance)
        super().perform_destroy(instance)


class SearchableMixin:
    """
    Mixin pour ajouter la recherche full-text aux ViewSets.
    """
    
    search_fields = []  # À définir dans la classe enfant
    
    def get_queryset(self):
        """Ajoute le filtrage par recherche"""
        queryset = super().get_queryset()
        
        search_query = self.request.query_params.get('search', None)
        
        if search_query and self.search_fields:
            from django.db.models import Q
            
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f"{field}__icontains": search_query})
            
            queryset = queryset.filter(query)
        
        return queryset