from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from apps.agenda.models import Event

class Command(BaseCommand):
    help = "Crée les permissions personnalisées pour le modèle Event"

    def handle(self, *args, **options):
        content_type = ContentType.objects.get_for_model(Event)

        permissions = [
            ('view_event', 'Peut consulter un événement'),
            ('change_event', 'Peut modifier un événement'),
            ('delete_event', 'Peut supprimer un événement'),
            ('create_event', 'Peut créer un événement'),
        ]

        for codename, name in permissions:
            Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type
            )
            self.stdout.write(self.style.SUCCESS(f"Permission {codename} créée"))

        self.stdout.write(self.style.SUCCESS("Permissions Event créées avec succès !"))