import uuid
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.clients.models import Client  # À adapter selon ta structure d'apps



class Dossier(models.Model):
    """
    Modèle central représentant un dossier juridique ou notarial.
    Conçu pour cabinets au Gabon (Libreville) et zone OHADA.
    Intègre secret professionnel, conformité RGPD gabonais et gestion sécurisée on-premise.
    """

    class Status(models.TextChoices):
        OPEN = "OUVERT", _("Ouvert / En cours")
        PENDING = "ATTENTE", _("En attente de pièces ou décision")
        ON_HOLD = "SUSPENDU", _("Suspendu")
        CLOSED = "CLOTURE", _("Clôturé")
        ARCHIVED = "ARCHIVE", _("Archivé")

    class Category(models.TextChoices):
        # Avocat
        CONTENTIEUX = "CONTENTIEUX", _("Contentieux (civil, pénal, administratif)")
        CONSEIL = "CONSEIL", _("Conseil juridique / Avis")
        RECOUVREMENT = "RECOUVREMENT", _("Recouvrement de créances")
        TRAVAIL = "TRAVAIL", _("Droit du travail")
        
        # Notaire
        IMMOBILIER = "IMMOBILIER", _("Actes immobiliers / Foncier")
        SUCCESSION = "SUCCESSION", _("Succession / Partage")
        CONTRAT_MARIAGE = "MARIAGE", _("Contrat de mariage / Régime matrimonial")
        DONATION = "DONATION", _("Donation / Libéralité")
        SOCIETE = "SOCIETE", _("Constitution / Modification société OHADA")
        
        # Commun
        FAMILLE = "FAMILLE", _("Divorce, garde, filiation")
        COMMERCIAL = "COMMERCIAL", _("Droit commercial OHADA")
        AUTRE = "AUTRE", _("Autre")

    # Identifiant sécurisé
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("Identifiant unique")
    )

    # Relations
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,  # Protège l'intégrité des données client
        related_name="dossiers",
        verbose_name=_("Client")
    )

    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="managed_dossiers",
        limit_choices_to={'role__in': ['AVOCAT', 'NOTAIRE', 'CONSEIL_JURIDIQUE']},
        verbose_name=_("Responsable principal")
    )

    # Utilisateurs autorisés à consulter (en plus du responsable)
    assigned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="accessible_dossiers",
        verbose_name=_("Utilisateurs autorisés"),
        help_text=_("Clercs, stagiaires ou collaborateurs ayant accès au dossier")
    )

    # Informations dossier
    title = models.CharField(max_length=300, verbose_name=_("Intitulé du dossier"))

    # Référence interne automatique : format GAB-YYYY-NNNN (ex: GAB-2026-0001)
    reference_code = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        verbose_name=_("Référence interne"),
        help_text=_("Générée automatiquement : GAB-YYYY-NNNN")
    )

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.AUTRE,
        verbose_name=_("Catégorie")
    )

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name=_("Statut")
    )

    description = models.TextField(blank=True, verbose_name=_("Résumé et notes confidentielles"))

    # Champs pratiques
    opponent = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Partie adverse / Opposant")
    )

    jurisdiction = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Juridiction / Tribunal / Office notarial")
    )

    critical_deadline = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Délai critique / Audience / Formalité")
    )

    # Conformité RGPD gabonais
    legal_basis = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Base légale du traitement"),
        help_text=_("Ex. : Exécution mandat, obligation légale, intérêt légitime")
    )

    retention_period_years = models.PositiveIntegerField(
        default=10,
        verbose_name=_("Durée de conservation (années)"),
        help_text=_("Illimitée pour actes notariés authentiques")
    )

    # Dates
    opening_date = models.DateField(default=timezone.now, verbose_name=_("Date d'ouverture"))
    closing_date = models.DateField(null=True, blank=True, verbose_name=_("Date de clôture"))
    archived_date = models.DateTimeField(null=True, blank=True, editable=False)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Dossier")
        verbose_name_plural = _("Dossiers")
        ordering = ['-opening_date', '-created_at']
        permissions = [
            ("can_view_confidential_dossier", _("Peut consulter les dossiers confidentiels")),
            ("can_archive_dossier", _("Peut archiver un dossier")),
        ]
        indexes = [
            models.Index(fields=['reference_code']),
            models.Index(fields=['client']),
            models.Index(fields=['responsible']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['critical_deadline']),
            models.Index(fields=['opening_date']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(closing_date__gte=models.F('opening_date')) | models.Q(closing_date__isnull=True),
                name='closing_date_after_opening'
            )
        ]

    def __str__(self):
        return f"[{self.reference_code}] {self.title} - {self.client.display_name}"

    @property
    def is_overdue(self):
        """Vérifie si un délai critique est dépassé."""
        if self.critical_deadline and self.status in [self.Status.OPEN, self.Status.PENDING]:
            return timezone.now().date() > self.critical_deadline
        return False

    @property
    def full_reference(self):
        return self.reference_code

    def generate_reference_code(self):
        """Génère une référence unique : GAB-YYYY-NNNN"""
        year = timezone.now().year
        prefix = f"GAB-{year}-"
        last_dossier = Dossier.objects.filter(
            reference_code__startswith=prefix
        ).order_by('-reference_code').first()

        if last_dossier and last_dossier.reference_code.startswith(prefix):
            try:
                num = int(last_dossier.reference_code.split('-')[-1]) + 1
            except ValueError:
                num = 1
        else:
            num = 1

        return f"{prefix}{str(num).zfill(4)}"

    def clean(self):
        errors = {}

        if self.closing_date and self.closing_date < self.opening_date:
            errors['closing_date'] = _("La date de clôture ne peut pas être antérieure à la date d'ouverture.")

        if self.status == self.Status.CLOSED and not self.closing_date:
            errors['closing_date'] = _("La date de clôture est obligatoire pour un dossier clôturé.")

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Génération automatique de la référence si nouvelle instance
        if not self.reference_code:
            self.reference_code = self.generate_reference_code()

        # Archivage automatique
        if self.status == self.Status.ARCHIVED and not self.archived_date:
            self.archived_date = timezone.now()

        self.full_clean()
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = _("Dossier")
        verbose_name_plural = _("Dossiers")
        ordering = ['-opening_date', '-created_at']
        
        # PERMISSIONS PERSONNALISÉES
        permissions = [
            # Permissions de base (déjà existantes)
            ("can_view_confidential_dossier", _("Peut consulter les dossiers confidentiels")),
            ("can_archive_dossier", _("Peut archiver un dossier")),
            
            # NOUVELLES PERMISSIONS pour gestion des collaborateurs
            ("assign_users_dossier", _("Peut assigner des collaborateurs au dossier")),
            ("view_all_dossiers", _("Peut voir tous les dossiers du cabinet")),
            ("manage_dossier_permissions", _("Peut gérer les permissions d'un dossier")),
        ]
        
        indexes = [
            models.Index(fields=['reference_code']),
            models.Index(fields=['client']),
            models.Index(fields=['responsible']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['critical_deadline']),
            models.Index(fields=['opening_date']),
        ]
        
        constraints = [
            models.CheckConstraint(
                check=models.Q(closing_date__gte=models.F('opening_date')) | 
                      models.Q(closing_date__isnull=True),
                name='closing_date_after_opening'
            )
        ]