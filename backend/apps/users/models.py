import uuid
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé pour les cabinets d'avocats et de notaires au Gabon
    et dans la zone OHADA.

    Points forts :
    - Utilisation d'UUID comme PK pour plus de sécurité (empêche l'énumération)
    - Rôles adaptés aux professions réglementées gabonaises
    - Champs professionnels obligatoires pour les rôles assermentés
    - Audit trail intégré (création/modification)
    - Préparation à la traçabilité RGPD et secret professionnel
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", _("Administrateur système")
        AVOCAT = "AVOCAT", _("Avocat")
        NOTAIRE = "NOTAIRE", _("Notaire")
        CONSEIL_JURIDIQUE = "CONSEIL_JURIDIQUE", _("Conseil juridique")
        STAGIAIRE = "STAGIAIRE", _("Stagiaire / Collaborateur")
        SECRETAIRE = "SECRETAIRE", _("Secrétaire / Clerc")
        ASSISTANT = "ASSISTANT", _("Assistant juridique")

    # Identifiant unique sécurisé
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("Identifiant unique")
    )

    # Rôle dans le cabinet
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STAGIAIRE,
        verbose_name=_("Rôle dans le cabinet"),
        help_text=_("Détermine les permissions par défaut dans l'application")
    )

    # Numéro professionnel (carte Barreau, Chambre des Notaires, etc.)
    professional_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,  # Un numéro professionnel doit être unique dans le cabinet
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9/-]+$',
                message=_("Le numéro professionnel ne doit contenir que des lettres majuscules, chiffres, tirets ou slashes.")
            )
        ],
        verbose_name=_("Numéro de carte professionnelle"),
        help_text=_("Ex. : BAR/GAB/2023/001 pour un avocat ou NOT/GAB/001 pour un notaire")
    )

    # Téléphone avec validation basique
    phone_regex = RegexValidator(
        regex=r'^\+?\d{8,15}$',
        message=_("Le numéro de téléphone doit être au format international ou local valide (8 à 15 chiffres).")
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Téléphone professionnel")
    )

    # Consentement RGPD (traçabilité de l'acceptation des conditions)
    has_accepted_privacy_policy = models.BooleanField(
        default=False,
        verbose_name=_("A accepté la politique de confidentialité"),
        help_text=_("Requis pour la conformité Loi 001/2011 modifiée 2023")
    )

    privacy_policy_accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Date d'acceptation de la politique de confidentialité")
    )

    # Champs d'audit
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name=_("Date de création")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Dernière modification")
    )

    # Optionnel : date de désactivation (soft delete futur)
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Compte actif"),
        help_text=_("Désactiver plutôt que supprimer pour conserver l'historique")
    )

    class Meta:
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")
        ordering = ['-created_at', 'last_name', 'first_name']
        permissions = [
            ("can_view_all_dossiers", _("Peut consulter tous les dossiers du cabinet")),
            ("can_manage_users", _("Peut gérer les comptes utilisateurs")),
            ("can_export_data", _("Peut exporter des données (RGPD)")),
        ]

    def __str__(self):
        full_name = self.get_full_name().strip()
        if not full_name:
            full_name = self.username
        return f"{full_name} ({self.get_role_display()})"

    # Propriétés utiles
    @property
    def is_legal_professional(self) -> bool:
        """Retourne True si l'utilisateur est avocat, notaire ou conseil juridique."""
        return self.role in {
            self.Role.AVOCAT,
            self.Role.NOTAIRE,
            self.Role.CONSEIL_JURIDIQUE
        }

    @property
    def is_admin_or_professional(self) -> bool:
        """Utile pour les permissions avancées."""
        return self.is_staff or self.is_legal_professional

    def accept_privacy_policy(self):
        """Méthode pour enregistrer l'acceptation RGPD."""
        self.has_accepted_privacy_policy = True
        self.privacy_policy_accepted_at = timezone.now()
        self.save(update_fields=['has_accepted_privacy_policy', 'privacy_policy_accepted_at'])

    def clean(self):
        """Validation personnalisée : professional_id obligatoire pour certains rôles."""
        from django.core.exceptions import ValidationError

        if self.is_legal_professional and not self.professional_id:
            raise ValidationError({
                'professional_id': _(
                    "Le numéro de carte professionnelle est obligatoire pour les avocats, notaires et conseils juridiques."
                )
            })

        super().clean()

    def save(self, *args, **kwargs):
        """Override save pour appliquer la validation clean()."""
        self.full_clean()
        super().save(*args, **kwargs)