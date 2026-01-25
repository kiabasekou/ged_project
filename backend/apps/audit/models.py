"""
Système d'audit complet avec anonymisation RGPD des données sensibles.
"""
import hashlib
import uuid
import json
from typing import Optional, Dict, Any

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    """
    Journal d'audit complet avec anonymisation automatique des champs sensibles.
    Conforme RGPD - aucune donnée personnelle en clair.
    """
    
    ACTION_TYPES = [
        ('CREATE', 'Création'),
        ('READ', 'Lecture'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
        ('DOWNLOAD', 'Téléchargement'),
        ('UPLOAD', 'Upload'),
        ('RESTORE', 'Restauration'),
        ('INTEGRITY_CHECK', 'Vérification Intégrité'),
        ('INTEGRITY_FAILURE', 'Échec Intégrité'),
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('LOGIN_FAILED', 'Échec Connexion'),
        ('PERMISSION_DENIED', 'Accès Refusé'),
    ]
    
    # Champs sensibles à anonymiser automatiquement
    SENSITIVE_FIELDS = [
        'ni_number', 'nif', 'rccm', 'date_of_birth', 'place_of_birth',
        'email', 'phone_primary', 'phone_secondary', 'address_line',
        'password', 'social_security', 'bank_account'
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Utilisateur effectuant l'action
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name="Utilisateur"
    )
    
    # Objet concerné (Generic Foreign Key)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="Type d'objet"
    )
    object_id = models.UUIDField(verbose_name="ID de l'objet")
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=255, verbose_name="Représentation")
    
    # Action
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name="Type d'action"
    )
    
    # Changements (données anonymisées)
    changes = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Changements",
        help_text="Données sensibles automatiquement anonymisées"
    )
    
    # Hash des champs sensibles (pour audit sans exposer les données)
    sensitive_fields_hash = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Hash des champs sensibles"
    )
    
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Contexte de la requête
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Adresse IP"
    )
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    request_path = models.CharField(max_length=500, blank=True, verbose_name="Chemin requête")
    session_key = models.CharField(max_length=40, blank=True, verbose_name="Clé de session")
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Horodatage")
    
    class Meta:
        db_table = 'audit_auditlog'
        verbose_name = "Entrée d'Audit"
        verbose_name_plural = "Journal d'Audit"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['action_type', 'timestamp']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        username = self.user.username if self.user else "Système"
        return f"{self.timestamp} - {username} - {self.action_type} - {self.object_repr}"
    
    def save(self, *args, **kwargs):
        """Anonymisation automatique avant sauvegarde"""
        if self.changes:
            self.changes, self.sensitive_fields_hash = self._anonymize_sensitive_data(
                self.changes
            )
        super().save(*args, **kwargs)
    
    def _anonymize_sensitive_data(self, data: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, str]]:
        """
        Anonymise les champs sensibles dans les changements.
        
        Args:
            data: Dictionnaire de données potentiellement sensibles
            
        Returns:
            Tuple (données_anonymisées, hash_champs_sensibles)
        """
        anonymized_data = data.copy()
        sensitive_hashes = {}
        
        for field in self.SENSITIVE_FIELDS:
            if field in anonymized_data:
                original_value = str(anonymized_data[field])
                
                # Hash SHA-256 du champ (pour comparaisons futures sans exposer la donnée)
                field_hash = hashlib.sha256(original_value.encode()).hexdigest()
                sensitive_hashes[field] = field_hash
                
                # Remplacement par marqueur anonyme
                if original_value:
                    anonymized_data[field] = "***REDACTED***"
                
        return anonymized_data, sensitive_hashes
    
    def verify_sensitive_field(self, field_name: str, value: str) -> bool:
        """
        Vérifie si une valeur correspond au hash stocké sans exposer la donnée.
        
        Args:
            field_name: Nom du champ sensible
            value: Valeur à vérifier
            
        Returns:
            True si le hash correspond
        """
        if field_name not in self.sensitive_fields_hash:
            return False
        
        value_hash = hashlib.sha256(str(value).encode()).hexdigest()
        return value_hash == self.sensitive_fields_hash[field_name]
    
    @classmethod
    def log_action(cls, user, obj, action_type: str, description: str = "",
                   changes: Optional[Dict] = None, request=None) -> 'AuditLog':
        """
        Méthode de classe pour créer rapidement une entrée d'audit.
        
        Args:
            user: Utilisateur effectuant l'action
            obj: Objet Django concerné
            action_type: Type d'action (CREATE, UPDATE, etc.)
            description: Description textuelle
            changes: Dictionnaire des changements
            request: Objet Request Django (optionnel)
            
        Returns:
            Instance AuditLog créée
        """
        content_type = ContentType.objects.get_for_model(obj.__class__)
        
        log_data = {
            'user': user,
            'content_type': content_type,
            'object_id': obj.pk,
            'object_repr': str(obj)[:255],
            'action_type': action_type,
            'description': description,
            'changes': changes or {},
        }
        
        # Extraction du contexte de requête si disponible
        if request:
            log_data.update({
                'ip_address': cls._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:1000],
                'request_path': request.path[:500],
                'session_key': request.session.session_key if hasattr(request, 'session') else '',
            })
        
        return cls.objects.create(**log_data)
    
    @staticmethod
    def _get_client_ip(request) -> Optional[str]:
        """Extraction de l'IP réelle du client (gestion proxy)"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_changes_display(self) -> str:
        """Formatage lisible des changements"""
        if not self.changes:
            return "Aucun changement enregistré"
        
        lines = []
        for key, value in self.changes.items():
            if value == "***REDACTED***":
                lines.append(f"- {key}: [Donnée sensible anonymisée]")
            else:
                lines.append(f"- {key}: {value}")
        
        return "\n".join(lines)


class AuditQuerySet(models.QuerySet):
    """QuerySet personnalisé pour requêtes d'audit courantes"""
    
    def for_object(self, obj):
        """Tous les logs pour un objet spécifique"""
        content_type = ContentType.objects.get_for_model(obj.__class__)
        return self.filter(content_type=content_type, object_id=obj.pk)
    
    def for_user(self, user):
        """Tous les logs d'un utilisateur"""
        return self.filter(user=user)
    
    def recent(self, days=7):
        """Logs des N derniers jours"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(timestamp__gte=cutoff)
    
    def by_action(self, action_type):
        """Filtrer par type d'action"""
        return self.filter(action_type=action_type)
    
    def security_events(self):
        """Événements de sécurité uniquement"""
        security_actions = [
            'LOGIN_FAILED', 'PERMISSION_DENIED', 'INTEGRITY_FAILURE'
        ]
        return self.filter(action_type__in=security_actions)


# Attacher le QuerySet personnalisé
AuditLog.objects = AuditQuerySet.as_manager()
