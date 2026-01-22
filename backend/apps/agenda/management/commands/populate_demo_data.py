from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from apps.clients.models import Client
from apps.dossiers.models import Dossier
from apps.agenda.models import Event
from datetime import date, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = "Peuple la base avec des données de démonstration pour tests"

    def handle(self, *args, **options):
        self.stdout.write("Début du peuplement des données...")

        # === 1. Utilisateurs ===
        users_data = [
            {
                'username': 'maitre_kiaba',
                'first_name': 'Jean-Paul',
                'last_name': 'Kiaba',
                'email': 'jp.kiaba@cabinet.ga',
                'role': 'AVOCAT',
                'professional_id': 'BAR/GAB/2020/001',
                'phone_number': '+24177123456'
            },
            {
                'username': 'notaire_ondo',
                'first_name': 'Marie',
                'last_name': 'Ondo',
                'email': 'm.ondo@notaire.ga',
                'role': 'NOTAIRE',
                'professional_id': 'NOT/GAB/2018/045',
                'phone_number': '+24166123456'
            },
            {
                'username': 'clerc_assistant',
                'first_name': 'Pierre',
                'last_name': 'Moussavou',
                'email': 'p.moussavou@cabinet.ga',
                'role': 'SECRETAIRE',
                'professional_id': None, # Utiliser None au lieu de ''
                'phone_number': '+24105123456'
            },
            {
                'username': 'stagiaire',
                'first_name': 'Aline',
                'last_name': 'Ngoma',
                'email': 'a.ngoma@cabinet.ga',
                'role': 'STAGIAIRE',
                'professional_id': None, # Utiliser None au lieu de ''
                'phone_number': '+24107123456'
            }
        ]

        users_map = {}
        for data in users_data:
            # Sécurité pour l'unicité du professional_id si vide
            prof_id = data.get('professional_id')
            if prof_id == '':
                data['professional_id'] = None

            user, created = User.objects.update_or_create(
                username=data['username'],
                defaults={
                    **data,
                    'is_active': True,
                    'password': make_password('demo123')
                }
            )
            
            status = "créé" if created else "mis à jour"
            self.stdout.write(self.style.SUCCESS(f"Utilisateur {user.username} {status}"))
            users_map[data['username']] = user

        # === 2. Clients ===
        clients_data = [
            {
                'client_type': 'PHYSIQUE',
                'first_name': 'Paul',
                'last_name': 'Biyoghe',
                'phone_primary': '+24177111222',
                'email': 'p.biyoghe@gmail.com',
                'city': 'Libreville',
            },
            {
                'client_type': 'MORALE',
                'company_name': 'Gabon Transit SARL',
                'rccm': 'LBV/2023/B/12345',
                'nif': '2023000456',
                'phone_primary': '+24166111222',
                'email': 'contact@gabontransit.ga',
                'city': 'Libreville'
            }
        ]

        clients = []
        for data in clients_data:
            client, created = Client.objects.update_or_create(
                phone_primary=data['phone_primary'],
                defaults=data
            )
            clients.append(client)
            self.stdout.write(f"Client {client.display_name} prêt.")

        # === 3. Dossiers ===
        # Utilisation de users_map pour garantir qu'on a les bons objets
        dossiers_data = [
            {
                'title': 'Succession Biyoghe',
                'category': 'SUCCESSION',
                'client': clients[0],
                'responsible': users_map['maitre_kiaba'],
                'description': 'Partage succession après décès'
            },
            {
                'title': 'Constitution Gabon Transit SARL',
                'category': 'COMMERCIAL',
                'client': clients[1],
                'responsible': users_map['notaire_ondo'],
                'description': 'Rédaction actes constitutifs OHADA'
            }
        ]

        for data in dossiers_data:
            # On utilise le titre et le client comme identifiant unique pour le peuplement
            dossier, created = Dossier.objects.update_or_create(
                title=data['title'],
                client=data['client'],
                defaults={
                    'category': data['category'],
                    'responsible': data['responsible'],
                    'description': data['description'],
                    'status': 'OUVERT'
                }
            )
            # Ajout du clerc en tant qu'utilisateur assigné
            dossier.assigned_users.add(users_map['clerc_assistant'])
            self.stdout.write(self.style.SUCCESS(f"Dossier {dossier.reference_code} prêt."))

        self.stdout.write(self.style.SUCCESS("Peuplement terminé ! MDP: demo123"))