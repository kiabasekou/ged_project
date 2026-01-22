import uuid
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, EmailValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Client(models.Model):
    """
    Modèle Client unifié pour Personnes Physiques et Morales.
    Conçu pour les cabinets d'avocats et notaires au Gabon (Libreville) et zone OHADA.
    Intègre conformité RGPD gabonais (Loi 001/2011 mod. 2023) et secret professionnel.
    """

    class ClientType(models.TextChoices):
        INDIVIDUAL = "PHYSIQUE", _("Personne Physique")
        COMPANY = "MORALE", _("Personne Morale")

    # Identifiant sécurisé
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("Identifiant unique")
    )

    client_type = models.CharField(
        max_length=10,
        choices=ClientType.choices,
        default=ClientType.INDIVIDUAL,
        verbose_name=_("Type de client")
    )

    # === CHAMPS PERSONNE PHYSIQUE ===
    first_name = models.CharField(max_length=150, blank=True, verbose_name=_("Prénom(s)"))
    last_name = models.CharField(max_length=150, blank=True, verbose_name=_("Nom de famille"))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_("Date de naissance"))
    place_of_birth = models.CharField(max_length=150, blank=True, verbose_name=_("Lieu de naissance"))

    # Pièce d'identité (CNI ou Passeport gabonais)
    ni_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("N° pièce d'identité (CNI / Passeport)"),
        help_text=_("Ex. : 123456789 pour CNI gabonaise")
    )
    ni_type = models.CharField(
        max_length=20,
        choices=[("CNI", "Carte Nationale d'Identité"), ("PASSPORT", "Passeport")],
        blank=True,
        verbose_name=_("Type de pièce")
    )

    # === CHAMPS PERSONNE MORALE ===
    company_name = models.CharField(max_length=255, blank=True, verbose_name=_("Raison sociale"))
    
    # RCCM gabonais : format comme LBV/2023/A/12345
    rccm_validator = RegexValidator(
        regex=r'^[A-Z]{3}/\d{4}/[A-Z]/\d+$',
        message=_("Format RCCM attendu : ex. LBV/2023/A/12345")
    )
    rccm = models.CharField(
        max_length=50,
        blank=True,
        validators=[rccm_validator],
        verbose_name=_("N° RCCM"),
        unique=True
    )

    # NIF gabonais : 10 chiffres (ex. 2023000123)
    nif_validator = RegexValidator(
        regex=r'^\d{10}$',
        message=_("Le NIF gabonais doit comporter exactement 10 chiffres.")
    )
    nif = models.CharField(
        max_length=10,
        blank=True,
        validators=[nif_validator],
        unique=True,
        verbose_name=_("NIF / Identifiant Fiscal Unique")
    )

    representative_name = models.CharField(max_length=255, blank=True, verbose_name=_("Nom du représentant légal"))
    representative_role = models.CharField(max_length=100, blank=True, verbose_name=_("Fonction du représentant"))

    # === COORDONNÉES COMMUNES ===
    email = models.EmailField(
        blank=True,
        null=True,
        unique=True,
        validators=[EmailValidator()],
        verbose_name=_("Adresse email principale")
    )

    phone_regex = RegexValidator(regex=r'^\+?\d{8,15}$', message=_("Numéro de téléphone invalide."))
    phone_primary = models.CharField(
        max_length=20,
        validators=[phone_regex],
        verbose_name=_("Téléphone principal"),
        help_text=_("Ex. : +241 01 23 45 67")
    )
    phone_secondary = models.CharField(max_length=20, blank=True, validators=[phone_regex], verbose_name=_("Téléphone secondaire"))

    # === ADRESSE (adaptée Gabon) ===
    address_line = models.CharField(max_length=255, blank=True, verbose_name=_("Rue / BP"))
    neighborhood = models.CharField(max_length=100, blank=True, verbose_name=_("Quartier"), help_text=_("Ex. : Glass, Louis, Akébé, Nkembo"))
    city = models.CharField(max_length=100, default="Libreville", verbose_name=_("Ville"))
    country = models.CharField(max_length=100, default="Gabon", verbose_name=_("Pays"))

    # === CONFORMITÉ RGPD GABONAIS ===
    data_source = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Source des données"),
        help_text=_("Ex. : Fournies par le client, acte notarié, jugement...")
    )

    consent_given = models.BooleanField(
        default=False,
        verbose_name=_("Consentement RGPD obtenu"),
        help_text=_("Coché si le client a été informé et a consenti au traitement")
    )
    consent_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Date du consentement"))

    retention_period_years = models.PositiveIntegerField(
        default=10,
        verbose_name=_("Durée de conservation (années)"),
        help_text=_("Au-delà : archivage ou anonymisation. Illimité pour actes notariés.")
    )

    # === MÉTADONNÉES ===
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name=_("Client actif"))

    notes = models.TextField(blank=True, verbose_name=_("Notes internes (confidentielles)"))

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['ni_number', 'ni_type'],
                condition=models.Q(client_type='PHYSIQUE'),
                name='unique_ni_per_individual'
            )
        ]
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['company_name']),
            models.Index(fields=['nif']),
            models.Index(fields=['rccm']),
        ]

    def __str__(self):
        if self.client_type == self.ClientType.COMPANY and self.company_name:
            return self.company_name
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or f"Client {self.id}"

    @property
    def display_name(self):
        """Nom affiché uniformément dans l'interface."""
        return self.__str__()

    @property
    def full_address(self):
        parts = [self.address_line, self.neighborhood, self.city, self.country]
        return ", ".join(filter(None, parts))

    @property
    def is_individual(self):
        return self.client_type == self.ClientType.INDIVIDUAL

    @property
    def is_company(self):
        return self.client_type == self.ClientType.COMPANY

    def grant_consent(self):
        """Enregistre le consentement RGPD."""
        self.consent_given = True
        self.consent_date = timezone.now()
        self.save(update_fields=['consent_given', 'consent_date'])

    def clean(self):
        """Validation conditionnelle selon le type de client."""
        errors = {}

        if self.is_individual:
            if not self.last_name:
                errors['last_name'] = _("Le nom est obligatoire pour une personne physique.")
            if not self.first_name:
                errors['first_name'] = _("Le prénom est obligatoire pour une personne physique.")
            if self.company_name or self.rccm or self.nif:
                errors['client_type'] = _("Ces champs ne doivent pas être remplis pour une personne physique.")

        elif self.is_company:
            if not self.company_name:
                errors['company_name'] = _("La raison sociale est obligatoire pour une personne morale.")
            if self.first_name or self.last_name or self.date_of_birth:
                errors['client_type'] = _("Les champs personne physique ne doivent pas être remplis pour une entreprise.")

        if errors:
            raise ValidationError(errors)

        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()  # Applique la validation personnalisée
        super().save(*args, **kwargs)