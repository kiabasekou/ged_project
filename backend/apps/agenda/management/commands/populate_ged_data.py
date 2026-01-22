import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from apps.clients.models import Client
from apps.dossiers.models import Dossier
from apps.documents.models import Folder, Document

User = get_user_model()

class Command(BaseCommand):
    help = "Peuple la GED avec une structure de dossiers et des fichiers types"

    def handle(self, *args, **options):
        self.stdout.write("🏗️ Construction de la structure documentaire (Correction NIF)...")

        # 1. Sélection d'un responsable métier (Avocat/Notaire)
        # On privilégie les utilisateurs créés par le script précédent
        responsible = User.objects.filter(role__in=['AVOCAT', 'NOTAIRE']).first()
        
        if not responsible:
            responsible = User.objects.filter(is_superuser=True).first()
            if responsible:
                responsible.role = 'AVOCAT'
                responsible.save()

        # 2. Création/MAJ du Client (NIF 10 chiffres exactement)
        client, created = Client.objects.update_or_create(
            company_name="TotalEnergies Gabon",
            defaults={
                'client_type': 'MORALE',
                'rccm': 'LBV/2024/B/88888',
                'nif': '2024888888',         # CORRECTION : 10 chiffres exactement
                'phone_primary': '+24166000000',
                'city': 'Port-Gentil',
                'email': 'contact.ga@totalenergies.com'
            }
        )
        self.stdout.write(f"🏢 Client : {client.company_name}")

        # 3. Création du Dossier
        dossier, created = Dossier.objects.update_or_create(
            title="Audit Foncier Site Oloumi",
            client=client,
            defaults={
                'category': 'IMMOBILIER',
                'responsible': responsible,
                'status': 'OUVERT',
                'description': 'Analyse des baux et titres fonciers zone industrielle.'
            }
        )
        self.stdout.write(f"📁 Dossier : {dossier.reference_code}")

        # 4. Création des répertoires virtuels
        folder_names = ["Pièces Administratives", "Actes Notariés", "Correspondances"]
        folder_objs = {}

        for name in folder_names:
            folder, _ = Folder.objects.get_or_create(
                name=name,
                dossier=dossier,
                defaults={'created_by': responsible}
            )
            folder_objs[name] = folder

        # 5. Création de documents types (PDF simulés)
        docs_to_create = [
            ('Statuts_Total_2024.pdf', "Pièces Administratives", 'NORMAL'),
            ('Titre_Foncier_Oloumi.pdf', "Actes Notariés", 'STRICTLY_CONFIDENTIAL'),
        ]

        for title, f_name, sensitivity in docs_to_create:
            target_folder = folder_objs[f_name]
            
            if not Document.objects.filter(title=title, dossier=dossier).exists():
                doc = Document(
                    title=title,
                    dossier=dossier,
                    folder=target_folder,
                    uploaded_by=responsible,
                    sensitivity=sensitivity,
                    file_extension='.pdf'
                )
                content = ContentFile(b"Document genere pour test GED.")
                doc.file.save(title, content, save=True)
                self.stdout.write(self.style.SUCCESS(f"📄 Fichier généré : {title}"))

        self.stdout.write(self.style.SUCCESS("\n✅ Base GED opérationnelle !"))