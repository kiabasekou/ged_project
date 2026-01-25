"""
Modèle Document avec versionnage immuable et stockage chiffré.
Garantit l'intégrité et la traçabilité complète des pièces du cabinet.
"""
import hashlib
import uuid
from pathlib import Path

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from apps.core.models import BaseModel
from .storage import AuditedFileStorage


class Folder(BaseModel):
    """Structure hiérarchique pour organiser les documents"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, verbose_name="Nom du dossier")
    
    dossier = models.ForeignKey(
        'dossiers.Dossier',
        on_delete=models.CASCADE,
        related_name='folders',
        verbose_name="Dossier juridique"
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='subfolders',
        null=True,
        blank=True,
        verbose_name="Dossier parent"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_folders',
        verbose_name="Créé par"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'documents_folder'
        verbose_name = "Dossier"
        verbose_name_plural = "Dossiers"
        ordering = ['name']
        constraints = [
            # Éviter les boucles infinies dans la hiérarchie
            models.CheckConstraint(
                check=~models.Q(id=models.F('parent_id')),
                name='folder_no_self_parent'
            )
        ]
    
    def __str__(self):
        return f"{self.dossier.reference_code}/{self.get_full_path()}"
    
    def get_full_path(self) -> str:
        """Retourne le chemin complet du dossier"""
        path_parts = [self.name]
        current = self.parent
        
        while current:
            path_parts.insert(0, current.name)
            current = current.parent
        
        return '/'.join(path_parts)
    
    def clean(self):
        """Validation personnalisée"""
        super().clean()
        
        # Vérifier que le parent appartient au même dossier juridique
        if self.parent and self.parent.dossier_id != self.dossier_id:
            raise ValidationError({
                'parent': "Le dossier parent doit appartenir au même dossier juridique"
            })


class Document(BaseModel):
    """
    Document avec versionnage immuable et chiffrement.
    Chaque modification crée une nouvelle version liée à la précédente.
    """
    
    SENSITIVITY_CHOICES = [
        ('public', 'Public'),
        ('internal', 'Usage Interne'),
        ('confidential', 'Confidentiel'),
        ('secret', 'Secret Professionnel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    dossier = models.ForeignKey(
        'dossiers.Dossier',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name="Dossier juridique"
    )
    
    folder = models.ForeignKey(
        Folder,
        on_delete=models.SET_NULL,
        related_name='documents',
        null=True,
        blank=True,
        verbose_name="Sous-dossier"
    )
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='uploaded_documents',
        verbose_name="Uploadé par"
    )
    
    # Stockage chiffré
    file = models.FileField(
        upload_to='documents/',
        storage=AuditedFileStorage(),
        verbose_name="Fichier"
    )
    
    # Métadonnées
    title = models.CharField(max_length=300, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    original_filename = models.CharField(max_length=255, verbose_name="Nom original")
    file_extension = models.CharField(max_length=10, verbose_name="Extension")
    file_size = models.BigIntegerField(verbose_name="Taille (octets)")
    mime_type = models.CharField(max_length=100, verbose_name="Type MIME")
    
    # Intégrité cryptographique
    file_hash = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Hash SHA-256",
        help_text="Empreinte cryptographique garantissant l'intégrité"
    )
    
    # Versionnage immuable
    version = models.PositiveIntegerField(default=1, verbose_name="Numéro de version")
    is_current_version = models.BooleanField(
        default=True,
        verbose_name="Version actuelle",
        help_text="True uniquement pour la dernière version"
    )
    
    previous_version = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        related_name='next_versions',
        null=True,
        blank=True,
        verbose_name="Version précédente"
    )
    
    # Sécurité et rétention
    sensitivity = models.CharField(
        max_length=20,
        choices=SENSITIVITY_CHOICES,
        default='internal',
        verbose_name="Niveau de sensibilité"
    )
    
    retention_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="Conservation jusqu'au",
        help_text="Date de suppression automatique (RGPD)"
    )
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploadé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        db_table = 'documents_document'
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['dossier', 'is_current_version']),
            models.Index(fields=['file_hash']),
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['original_filename']),
        ]
        constraints = [
            # Une seule version courante par nom de fichier et dossier
            models.UniqueConstraint(
                fields=['dossier', 'original_filename'],
                condition=models.Q(is_current_version=True),
                name='unique_current_version_per_dossier'
            ),
            # Version 1 ne doit pas avoir de précédente
            models.CheckConstraint(
                check=(
                    models.Q(version=1, previous_version__isnull=True) |
                    models.Q(version__gt=1, previous_version__isnull=False)
                ),
                name='version_integrity_check'
            ),
            # Les versions courantes doivent avoir previous_version (sauf v1)
            models.CheckConstraint(
                check=(
                    models.Q(is_current_version=False) |
                    models.Q(is_current_version=True, version=1, previous_version__isnull=True) |
                    models.Q(is_current_version=True, version__gt=1, previous_version__isnull=False)
                ),
                name='current_version_must_have_history'
            ),
        ]
    
    def __str__(self):
        return f"{self.title} (v{self.version})"
    
    def save(self, *args, **kwargs):
        """Calcul automatique du hash et des métadonnées"""
        if self.file and not self.file_hash:
            # Calcul du hash SHA-256
            self.file.seek(0)
            file_content = self.file.read()
            self.file_hash = hashlib.sha256(file_content).hexdigest()
            self.file.seek(0)
            
            # Extraction des métadonnées si non définies
            if not self.original_filename:
                self.original_filename = Path(self.file.name).name
            
            if not self.file_extension:
                self.file_extension = Path(self.file.name).suffix.lower()
            
            if not self.file_size:
                self.file_size = self.file.size
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validations métier"""
        super().clean()
        
        # Vérifier que folder appartient au même dossier
        if self.folder and self.folder.dossier_id != self.dossier_id:
            raise ValidationError({
                'folder': "Le sous-dossier doit appartenir au même dossier juridique"
            })
        
        # Vérifier la cohérence du versionnage
        if self.previous_version:
            if self.previous_version.dossier_id != self.dossier_id:
                raise ValidationError({
                    'previous_version': "La version précédente doit appartenir au même dossier"
                })
            
            if self.version != self.previous_version.version + 1:
                raise ValidationError({
                    'version': f"Version incohérente (attendu: {self.previous_version.version + 1})"
                })
    
    def create_new_version(self, new_file, uploaded_by, **metadata):
        """
        Crée une nouvelle version de ce document.
        Marque l'actuelle comme ancienne.
        
        Args:
            new_file: Nouveau fichier à uploader
            uploaded_by: Utilisateur effectuant l'upload
            **metadata: Métadonnées supplémentaires (title, description, etc.)
            
        Returns:
            La nouvelle version du document
        """
        if not self.is_current_version:
            raise ValidationError("Impossible de créer une version depuis une version non-courante")
        
        # Archivage de la version actuelle
        self.is_current_version = False
        self.save(update_fields=['is_current_version'])
        
        # Création de la nouvelle version
        new_version = Document(
            dossier=self.dossier,
            folder=self.folder,
            uploaded_by=uploaded_by,
            file=new_file,
            original_filename=metadata.get('original_filename', self.original_filename),
            title=metadata.get('title', self.title),
            description=metadata.get('description', self.description),
            sensitivity=metadata.get('sensitivity', self.sensitivity),
            retention_until=metadata.get('retention_until', self.retention_until),
            version=self.version + 1,
            is_current_version=True,
            previous_version=self
        )
        
        new_version.save()
        return new_version
    
    def get_version_history(self):
        """Retourne la chaîne complète des versions (de la plus récente à la plus ancienne)"""
        history = [self]
        current = self.previous_version
        
        while current:
            history.append(current)
            current = current.previous_version
        
        return history
    
    def verify_integrity(self) -> bool:
        """Vérifie que le fichier n'a pas été altéré"""
        return self.file.storage.verify_integrity(self.file.name, self.file_hash)
    
    def get_absolute_url(self):
        """URL de téléchargement du document"""
        from django.urls import reverse
        return reverse('document-download', kwargs={'pk': self.pk})
