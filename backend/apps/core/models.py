"""
Modèles de base pour l'application GED Cabinet.
Tous les modèles métier héritent de BaseModel.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """
    Modèle abstrait de base pour tous les modèles de l'application.
    
    Fournit :
    - Identifiant UUID au lieu d'AutoField
    - Timestamps automatiques (created_at, updated_at)
    - Soft-delete (is_active)
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Identifiant"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le",
        help_text="Date et heure de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Modifié le",
        help_text="Date et heure de dernière modification"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Désactiver au lieu de supprimer (soft-delete)"
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def soft_delete(self):
        """Soft delete : marque comme inactif au lieu de supprimer"""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
    
    def restore(self):
        """Restaure un objet soft-deleted"""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])


class BaseModelQuerySet(models.QuerySet):
    """QuerySet personnalisé avec méthodes de filtrage utiles"""
    
    def active(self):
        """Retourne uniquement les objets actifs"""
        return self.filter(is_active=True)
    
    def inactive(self):
        """Retourne uniquement les objets inactifs (soft-deleted)"""
        return self.filter(is_active=False)
    
    def soft_delete(self):
        """Soft delete en masse"""
        return self.update(is_active=False)
    
    def restore(self):
        """Restauration en masse"""
        return self.update(is_active=True)


class BaseModelManager(models.Manager):
    """Manager personnalisé utilisant BaseModelQuerySet"""
    
    def get_queryset(self):
        return BaseModelQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def inactive(self):
        return self.get_queryset().inactive()


class TimestampedModel(models.Model):
    """
    Modèle abstrait simple avec uniquement timestamps.
    Pour les modèles qui n'ont pas besoin de UUID ni soft-delete.
    """
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Modifié le"
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']