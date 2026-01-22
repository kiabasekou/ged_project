# backend/apps/dossiers/management/commands/create_dossier_permissions.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from apps.dossiers.models import Dossier
from apps.documents.models import Document, Folder

class Command(BaseCommand):
    help = "Crée les permissions personnalisées pour Dossier, Document et Folder"

    def handle(self, *args, **options):
        models = [Dossier, Document, Folder]

        custom_perms = {
            Dossier: [
                ('view_dossier', 'Peut consulter le dossier'),
                ('change_dossier', 'Peut modifier le dossier'),
                ('delete_dossier', 'Peut archiver/supprimer le dossier'),
                ('assign_dossier', 'Peut assigner des collaborateurs au dossier'),
            ],
            Document: [
                ('view_document', 'Peut consulter le document'),
                ('download_document', 'Peut télécharger le document'),
                ('change_document', 'Peut modifier les métadonnées'),
                ('delete_document', 'Peut supprimer le document'),
                ('upload_new_version', 'Peut uploader une nouvelle version'),
            ],
            Folder: [
                ('view_folder', 'Peut voir le répertoire'),
                ('change_folder', 'Peut renommer/déplacer le répertoire'),
                ('delete_folder', 'Peut supprimer le répertoire'),
            ]
        }

        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            perms_to_create = custom_perms.get(model, [])

            for codename, name in perms_to_create:
                Permission.objects.get_or_create(
                    codename=codename,
                    name=name,
                    content_type=content_type
                )
                self.stdout.write(self.style.SUCCESS(f"Permission {codename} créée pour {model.__name__}"))

        self.stdout.write(self.style.SUCCESS("Toutes les permissions personnalisées ont été créées."))