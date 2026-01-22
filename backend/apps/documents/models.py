import os
import uuid
import hashlib
from django.core.validators import FileExtensionValidator
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import get_valid_filename
from django.utils.translation import gettext_lazy as _
from apps.dossiers.models import Dossier


def secure_document_upload_path(instance, filename):
    """
    Chemin sécurisé et isolé par dossier :
    media/dossiers/<dossier_uuid>/<sous-dossier_uuid_ou_root>/<nom_fichier_sécurisé>
    """
    # Nettoyage du nom de fichier pour éviter attaques path traversal
    safe_filename = get_valid_filename(filename)
    dossier_uuid = instance.dossier.id

    if instance.folder and instance.folder.id:
        folder_part = str(instance.folder.id)
    else:
        folder_part = "root"

    # Ajout d'un UUID pour éviter les collisions et deviner les noms
    name, ext = os.path.splitext(safe_filename)
    unique_filename = f"{uuid.uuid4()}_{name}{ext}"

    return f"dossiers/{dossier_uuid}/{folder_part}/{unique_filename}"


class Folder(models.Model):
    """
    Répertoire virtuel à l'intérieur d'un dossier juridique.
    Permet une arborescence logique sans refléter le stockage physique.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, verbose_name=_("Nom du répertoire"))
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name="folders"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subfolders"
    )
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_folders"
    )

    class Meta:
        verbose_name = _("Répertoire virtuel")
        verbose_name_plural = _("Répertoires virtuels")
        unique_together = ('name', 'dossier', 'parent')
        ordering = ['name']
        indexes = [
            models.Index(fields=['dossier', 'parent']),
        ]

    def __str__(self):
        return self.name

    @property
    def full_path(self):
        """Retourne le chemin complet du dossier (ex: Contrats / 2024 / Fournisseurs)"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.append(parent.name)
            parent = parent.parent
        return " / ".join(reversed(path))

    def get_absolute_path(self):
        """Pour affichage dans l'interface Vue"""
        return self.full_path


class Document(models.Model):
    """
    Modèle GED principal : fichier physique + métadonnées riches + versioning par instance.
    Conforme secret professionnel et Loi gabonaise 001/2011 mod. 2023.
    """

    class SensitivityLevel(models.TextChoices):
        NORMAL = "NORMAL", _("Normal")
        CONFIDENTIAL = "CONFIDENTIEL", _("Confidentiel")
        HIGHLY_CONFIDENTIAL = "TRES_CONFIDENTIEL", _("Très confidentiel (secret professionnel renforcé)")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relations
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.PROTECT,  # Empêche suppression accidentelle
        related_name="documents"
    )
    folder = models.ForeignKey(
        Folder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
        verbose_name=_("Répertoire virtuel")
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_documents",
        verbose_name=_("Téléversé par")
    )

    # Fichier physique
    file = models.FileField(
        upload_to=secure_document_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=[
                'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png',
                'txt', 'rtf', 'msg', 'eml', 'zip'
            ])
        ],
        verbose_name=_("Fichier")
    )

    # Métadonnées descriptives
    title = models.CharField(max_length=300, verbose_name=_("Titre du document"))
    description = models.TextField(blank=True, verbose_name=_("Description / Notes"))

    # Métadonnées techniques automatiques
    original_filename = models.CharField(max_length=255, blank=True, verbose_name=_("Nom original"))
    file_extension = models.CharField(max_length=10, blank=True, editable=False)
    file_size = models.BigIntegerField(null=True, blank=True, verbose_name=_("Taille (octets)"))
    mime_type = models.CharField(max_length=100, blank=True, editable=False)
    file_hash = models.CharField(max_length=64, blank=True, editable=False)  # SHA-256 pour intégrité

    # Versioning : nouvelle instance à chaque modification importante
    version = models.PositiveIntegerField(default=1)
    is_current_version = models.BooleanField(default=True, verbose_name=_("Version actuelle"))
    previous_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="next_versions"
    )

    # Sécurité et conformité
    sensitivity = models.CharField(
        max_length=20,
        choices=SensitivityLevel.choices,
        default=SensitivityLevel.NORMAL,
        verbose_name=_("Niveau de confidentialité")
    )

    retention_until = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date de fin de conservation légale"),
        help_text=_("Au-delà : archivage ou destruction sécurisée")
    )

    # Dates
    uploaded_at = models.DateTimeField(default=timezone.now, verbose_name=_("Date de téléversement"))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
        ordering = ['-uploaded_at', 'title']
        indexes = [
            models.Index(fields=['dossier', 'folder']),
            models.Index(fields=['title']),
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['sensitivity']),
            models.Index(fields=['file_extension']),
        ]
        permissions = [
            ("can_view_confidential_docs", _("Peut consulter les documents confidentiels")),
            ("can_delete_documents", _("Peut supprimer définitivement des documents")),
        ]

    def __str__(self):
        return f"{self.title} (v{self.version}) - {self.dossier.reference_code}"

    @property
    def display_name(self):
        return self.title or self.original_filename or "Document sans titre"

    @property
    def folder_path(self):
        if self.folder:
            return self.folder.full_path
        return _("Racine")

    def compute_hash(self):
        """Calcule le SHA-256 du fichier pour vérification d'intégrité"""
        if not self.file:
            return ""
        hash_sha256 = hashlib.sha256()
        self.file.seek(0)
        for chunk in self.file.chunks():
            hash_sha256.update(chunk)
        self.file.seek(0)
        return hash_sha256.hexdigest()

    def save(self, *args, **kwargs):
        # Extraction métadonnées au premier upload
        if self.file and not self.pk:
            self.original_filename = os.path.basename(self.file.name)
            name, ext = os.path.splitext(self.original_filename)
            self.file_extension = ext.lower().lstrip('.')
            self.file_size = self.file.size
            self.file_hash = self.compute_hash()

            # MIME type basique (améliorable avec python-magic)
            if self.file_extension in ['pdf']:
                self.mime_type = 'application/pdf'
            elif self.file_extension in ['doc', 'docx']:
                self.mime_type = 'application/msword'
            elif self.file_extension in ['jpg', 'jpeg']:
                self.mime_type = 'image/jpeg'
            elif self.file_extension == 'png':
                self.mime_type = 'image/png'
            else:
                self.mime_type = 'application/octet-stream'

        # Gestion retention par défaut (ex: 10 ans après clôture dossier)
        if not self.retention_until and self.dossier.closing_date:
            from dateutil.relativedelta import relativedelta
            self.retention_until = self.dossier.closing_date + relativedelta(years=self.dossier.retention_period_years)

        super().save(*args, **kwargs)

    def create_new_version(self, new_file, user):
        """
        Crée une nouvelle version du document (utilisé lors de modification).
        L'ancienne devient non actuelle.
        """
        # Marquer l'ancienne comme non actuelle
        self.is_current_version = False
        self.save(update_fields=['is_current_version'])

        # Créer la nouvelle version
        new_doc = Document.objects.create(
            dossier=self.dossier,
            folder=self.folder,
            uploaded_by=user,
            file=new_file,
            title=self.title,
            description=self.description,
            sensitivity=self.sensitivity,
            retention_until=self.retention_until,
            version=self.version + 1,
            previous_version=self
        )
        return new_doc