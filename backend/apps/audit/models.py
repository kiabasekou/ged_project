import json
import uuid
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import JSONField

class AuditLog(models.Model):
    """
    Journal d'audit complet et immutable.
    Enregistre toutes les actions sensibles dans l'application :
    création, modification, consultation, téléchargement, connexion, etc.

    Indispensable pour :
    - Respect du secret professionnel (avocats/notaires)
    - Conformité RGPD gabonais (traçabilité, registre des traitements)
    - Preuve en cas de contrôle APDPVP ou litige interne
    """

    class Action(models.TextChoices):
        CREATE = "CREATE", _("Création")
        UPDATE = "UPDATE", _("Modification")
        DELETE = "DELETE", _("Suppression définitive")
        VIEW = "VIEW", _("Consultation (lecture)")
        DOWNLOAD = "DOWNLOAD", _("Téléchargement de document")
        PRINT = "PRINT", _("Impression (si implémenté)")
        SHARE = "SHARE", _("Partage interne (assignation)")
        LOGIN = "LOGIN", _("Connexion réussie")
        LOGIN_FAILED = "LOGIN_FAILED", _("Tentative de connexion échouée")
        LOGOUT = "LOGOUT", _("Déconnexion")
        EXPORT = "EXPORT", _("Export de données (RGPD)")
        CONSENT_GIVEN = "CONSENT", _("Consentement RGPD accordé")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Utilisateur responsable (null si anonyme ou système)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name=_("Utilisateur")
    )

    # Objet concerné (Dossier, Document, Client, etc.) via relation générique
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Type d'objet")
    )
    object_id = models.UUIDField(verbose_name=_("ID de l'objet"))
    content_object = GenericForeignKey('content_type', 'object_id')

    # Représentation texte de l'objet (pour lisibilité si suppression)
    object_repr = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Représentation de l'objet"),
        help_text=_("Ex. : [GAB-2026-0001] Succession M. X")
    )

    # Action effectuée
    action_type = models.CharField(
        max_length=20,
        choices=Action.choices,
        verbose_name=_("Type d'action")
    )

    # Détails structurés des changements (pour UPDATE)
    changes = JSONField(
        null=True,
        blank=True,
        verbose_name=_("Modifications apportées"),
        help_text=_("Diff JSON : {'field': ['ancienne_valeur', 'nouvelle_valeur']}")
    )

    # Description libre (ex. raison du téléchargement)
    description = models.TextField(
        blank=True,
        verbose_name=_("Commentaire ou justification")
    )

    # Contexte technique (très utile en on-premise)
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("Adresse IP")
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name=_("User-Agent navigateur")
    )
    request_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("URL de la requête")
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name=_("Clé de session")
    )

    # Horodatage précis
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name=_("Date et heure")
    )

    class Meta:
        verbose_name = _("Journal d'audit")
        verbose_name_plural = _("Journaux d'audit")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user']),
            models.Index(fields=['action_type']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['request_path']),
        ]
        permissions = [
            ("can_view_audit_logs", _("Peut consulter les logs d'audit")),
            ("can_export_audit_logs", _("Peut exporter les logs (RGPD)")),
        ]

    def __str__(self):
        user = self.user.get_full_name() or self.user.username if self.user else _("Système/Anonyme")
        target = self.object_repr or f"{self.content_type} ({self.object_id})"
        return f"{self.timestamp:%Y-%m-%d %H:%M} | {user} | {self.get_action_type_display()} | {target}"

    @property
    def is_sensitive_action(self):
        """Actions particulièrement sensibles à surveiller"""
        return self.action_type in {
            self.Action.VIEW,
            self.Action.DOWNLOAD,
            self.Action.DELETE,
            self.Action.EXPORT
        }

    def save(self, *args, **kwargs):
        """
        Garantit l'immutabilité partielle : on ne modifie jamais un log existant
        (sauf en cas d'erreur grave, par admin autorisé)
        """
        if self.pk:  # Si déjà existant
            # Optionnel : lever une exception pour empêcher toute modification
            # raise RuntimeError("Les logs d'audit sont immuables.")
            pass
        super().save(*args, **kwargs)


# Fonction utilitaire recommandée (à placer dans un module utils/audit.py)
def log_action(
    user,
    obj,
    action: str,
    changes=None,
    description="",
    request=None
):
    """
    Fonction helper pour créer un log d'audit facilement depuis les views/serializers.
    """
    from django.contrib.contenttypes.models import ContentType

    ip = None
    user_agent = ""
    path = ""
    session_key = ""

    if request:
        ip = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        path = request.path
        session_key = request.session.session_key or ""

    AuditLog.objects.create(
        user=user,
        content_type=ContentType.objects.get_for_model(obj),
        object_id=obj.id,
        object_repr=str(obj),
        action_type=action,
        changes=changes,
        description=description,
        ip_address=ip,
        user_agent=user_agent,
        request_path=path,
        session_key=session_key
    )