"""
Migration Django pour ajout des contraintes de versionnage.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),  # Adapter selon votre numérotation
    ]

    operations = [
        # Contrainte: Version 1 ne doit pas avoir de previous_version
        migrations.AddConstraint(
            model_name='document',
            constraint=models.CheckConstraint(
                check=(
                    models.Q(version=1, previous_version__isnull=True) |
                    models.Q(version__gt=1, previous_version__isnull=False)
                ),
                name='version_integrity_check'
            ),
        ),
        
        # Contrainte: Une seule version courante par fichier et dossier
        migrations.AddConstraint(
            model_name='document',
            constraint=models.UniqueConstraint(
                fields=['dossier', 'original_filename'],
                condition=models.Q(is_current_version=True),
                name='unique_current_version_per_dossier'
            ),
        ),
        
        # Contrainte: Les versions courantes doivent avoir un historique (sauf v1)
        migrations.AddConstraint(
            model_name='document',
            constraint=models.CheckConstraint(
                check=(
                    models.Q(is_current_version=False) |
                    models.Q(is_current_version=True, version=1, previous_version__isnull=True) |
                    models.Q(is_current_version=True, version__gt=1, previous_version__isnull=False)
                ),
                name='current_version_must_have_history'
            ),
        ),
        
        # Index sur les champs critiques pour performance
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['dossier', 'is_current_version'], name='doc_dossier_current_idx'),
        ),
        
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['file_hash'], name='doc_hash_idx'),
        ),
        
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['uploaded_at'], name='doc_uploaded_idx'),
        ),
        
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['original_filename'], name='doc_filename_idx'),
        ),
        
        # Contrainte sur Folder: pas de boucle infinie
        migrations.AddConstraint(
            model_name='folder',
            constraint=models.CheckConstraint(
                check=~models.Q(id=models.F('parent_id')),
                name='folder_no_self_parent'
            ),
        ),
    ]
