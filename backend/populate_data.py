"""
Script de peuplement avec détection automatique de TOUS les choix.
Version finale production-ready.
"""
import os
import sys
import django
from datetime import datetime, timedelta, date
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.clients.models import Client
from apps.dossiers.models import Dossier
from apps.agenda.models import Event
from django.utils import timezone

User = get_user_model()

# ============================================================================
# DÉTECTION AUTOMATIQUE DES CHOIX
# ============================================================================

def get_field_choices(model, field_name):
    """Récupère les choix d'un champ"""
    field = model._meta.get_field(field_name)
    if hasattr(field, 'choices') and field.choices:
        return {value: label for value, label in field.choices}
    return {}

def get_choice(choices_dict, preferences):
    """Retourne le premier choix disponible parmi les préférences"""
    if not choices_dict:
        return preferences[0]
    
    for pref in preferences:
        if pref in choices_dict or pref.upper() in choices_dict:
            return pref.upper() if pref.upper() in choices_dict else pref
    
    return list(choices_dict.keys())[0]

# Détecter tous les choix
print("\n🔍 Détection des choix disponibles...")
USER_ROLES = get_field_choices(User, 'role')
CLIENT_TYPES = get_field_choices(Client, 'client_type')
DOSSIER_CATEGORIES = get_field_choices(Dossier, 'category')
DOSSIER_STATUS = get_field_choices(Dossier, 'status')
EVENT_TYPES = get_field_choices(Event, 'type')

print(f"✓ Rôles users: {list(USER_ROLES.keys())}")
print(f"✓ Types clients: {list(CLIENT_TYPES.keys())}")
print(f"✓ Catégories dossiers: {list(DOSSIER_CATEGORIES.keys())}")
print(f"✓ Statuts dossiers: {list(DOSSIER_STATUS.keys())}")
print(f"✓ Types événements: {list(EVENT_TYPES.keys())}")

# ============================================================================
# DONNÉES DE BASE
# ============================================================================

QUARTIERS_LIBREVILLE = [
    'Quartier Louis', 'Lalala', 'Nzeng-Ayong', 'Akébé', 'PK8', 'Glass', 'Batavéa'
]

VILLES_GABON = [
    'Libreville', 'Port-Gentil', 'Franceville', 'Oyem', 'Lambaréné'
]

PRENOMS_MASCULINS = [
    'Jean-Baptiste', 'Pierre', 'Paul', 'André', 'Michel', 'Louis', 'Patrick'
]

PRENOMS_FEMININS = [
    'Marie', 'Anne', 'Christine', 'Sylvie', 'Catherine', 'Nicole'
]

NOMS_FAMILLE = [
    'Obame', 'Nguema', 'Ndong', 'Mba', 'Ondo', 'Bekale', 'Nze', 'Koumba'
]

ENTREPRISES_GABON = [
    'BGFIBank', 'UGB', 'SEEG', 'Total Gabon', 'Airtel Gabon'
]

# ============================================================================
# UTILITAIRES
# ============================================================================

def generer_ni():
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])

def generer_nif():
    return ''.join([str(random.randint(0, 9)) for _ in range(9)])

def generer_rccm():
    return f"LBV/{random.randint(2020, 2024)}/A/N/{random.randint(1000, 9999)}"

def generer_telephone():
    return f"+24107{random.randint(1000000, 9999999)}"

def generer_reference():
    return f"CAB/2024/{random.randint(1, 999):04d}"

# ============================================================================
# CRÉATION UTILISATEURS
# ============================================================================

def creer_utilisateurs():
    print("\n📋 Création des utilisateurs...")
    users = []
    
    # Rôles à utiliser
    role_admin = get_choice(USER_ROLES, ['ADMIN', 'admin', 'AVOCAT'])
    role_avocat = get_choice(USER_ROLES, ['AVOCAT', 'avocat', 'NOTAIRE'])
    role_secretaire = get_choice(USER_ROLES, ['SECRETAIRE', 'secretaire', 'ASSISTANT'])
    role_assistant = get_choice(USER_ROLES, ['ASSISTANT', 'assistant', 'STAGIAIRE'])
    
    print(f"  Rôles: admin={role_admin}, avocat={role_avocat}, "
          f"secrétaire={role_secretaire}, assistant={role_assistant}")
    
    # Admin
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@cabinet.ga',
            password='admin123',
            first_name='Jean-Baptiste',
            last_name='Obame',
            role=role_admin,
            professional_id='BAR/001',
            phone_number=generer_telephone(),
            has_accepted_privacy_policy=True,
            privacy_policy_accepted_at=timezone.now()
        )
        users.append(admin)
        print(f"✓ Admin: {admin.get_full_name()}")
    
    # Avocats
    for i, (nom, prenom) in enumerate([
        ('Ondo', 'Marie'), ('Nze', 'Pierre'), ('Mba', 'Christine')
    ], 1):
        username = f"{prenom.lower()}.{nom.lower()}"
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f'{username}@cabinet.ga',
                password='avocat123',
                first_name=prenom,
                last_name=nom,
                role=role_avocat,
                professional_id=f'BAR/{i+1:03d}',
                phone_number=generer_telephone(),
                is_staff=True,
                has_accepted_privacy_policy=True,
                privacy_policy_accepted_at=timezone.now()
            )
            users.append(user)
            print(f"✓ Avocat: {user.get_full_name()}")
    
    # Collaborateurs
    for nom, prenom, role in [
        ('Koumba', 'Sylvie', role_secretaire),
        ('Moukala', 'Paul', role_assistant),
    ]:
        username = f"{prenom.lower()}.{nom.lower()}"
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f'{username}@cabinet.ga',
                password='collab123',
                first_name=prenom,
                last_name=nom,
                role=role,
                phone_number=generer_telephone(),
                has_accepted_privacy_policy=True,
                privacy_policy_accepted_at=timezone.now()
            )
            users.append(user)
            print(f"✓ Collaborateur: {user.get_full_name()}")
    
    return users

# ============================================================================
# CRÉATION CLIENTS
# ============================================================================

def creer_clients():
    print("\n👥 Création des clients...")
    clients = []
    
    # Types clients
    type_personne = get_choice(CLIENT_TYPES, ['PERSONNE_PHYSIQUE', 'personne', 'particulier'])
    type_entreprise = get_choice(CLIENT_TYPES, ['PERSONNE_MORALE', 'entreprise', 'societe'])
    
    print(f"  Types: personne={type_personne}, entreprise={type_entreprise}")
    
    # Particuliers (20)
    for i in range(20):
        prenom = random.choice(PRENOMS_MASCULINS + PRENOMS_FEMININS)
        nom = random.choice(NOMS_FAMILLE)
        
        client = Client.objects.create(
            client_type=type_personne,
            first_name=prenom,
            last_name=nom,
            date_of_birth=date(1970, 1, 1) + timedelta(days=random.randint(0, 10000)),
            place_of_birth=random.choice(VILLES_GABON),
            ni_number=generer_ni(),
            ni_type='CNI',
            email=f'{prenom.lower()}.{nom.lower()}{i}@gmail.com',
            phone_primary=generer_telephone(),
            address_line=f'BP {random.randint(1000, 9999)}',
            neighborhood=random.choice(QUARTIERS_LIBREVILLE),
            city='Libreville',
            country='Gabon',
            consent_given=True,
            consent_date=timezone.now(),
            retention_period_years=10,
            is_active=True
        )
        clients.append(client)
    
    print(f"✓ {len(clients)} particuliers créés")
    
    # Entreprises (10)
    for i in range(10):
        entreprise = random.choice(ENTREPRISES_GABON)
        
        client = Client.objects.create(
            client_type=type_entreprise,
            company_name=entreprise + f" {i}",
            rccm=generer_rccm(),
            nif=generer_nif(),
            representative_name=f"{random.choice(PRENOMS_MASCULINS)} {random.choice(NOMS_FAMILLE)}",
            representative_role='Directeur Général',
            email=f'contact{i}@entreprise.ga',
            phone_primary=generer_telephone(),
            address_line=f'BP {random.randint(5000, 9999)}',
            city='Libreville',
            country='Gabon',
            consent_given=True,
            consent_date=timezone.now(),
            retention_period_years=10,
            is_active=True
        )
        clients.append(client)
    
    print(f"✓ {len(clients)-20} entreprises créées")
    return clients

# ============================================================================
# CRÉATION DOSSIERS
# ============================================================================

def creer_dossiers(clients, users):
    print("\n📁 Création des dossiers...")
    dossiers = []
    
    # Catégories et statuts
    categories = list(DOSSIER_CATEGORIES.keys())[:3] if DOSSIER_CATEGORIES else ['civil', 'penal', 'commercial']
    statuts = list(DOSSIER_STATUS.keys())[:3] if DOSSIER_STATUS else ['ouvert', 'en_cours', 'cloture']
    
    avocats = [u for u in users if u.is_staff or u.is_superuser]
    
    for i in range(30):
        client = random.choice(clients)
        avocat = random.choice(avocats)
        
        dossier = Dossier.objects.create(
            client=client,
            responsible=avocat,
            title=f"Dossier {client.last_name or client.company_name}",
            reference_code=generer_reference(),
            category=random.choice(categories),
            status=random.choice(statuts),
            description=f"Dossier créé automatiquement",
            opponent=f"{random.choice(PRENOMS_MASCULINS)} {random.choice(NOMS_FAMILLE)}",
            jurisdiction='Tribunal de Libreville',
            retention_period_years=10,
            opening_date=date.today() - timedelta(days=random.randint(1, 365)),
        )
        dossiers.append(dossier)
    
    print(f"✓ {len(dossiers)} dossiers créés")
    return dossiers

# ============================================================================
# CRÉATION ÉVÉNEMENTS
# ============================================================================

def creer_evenements(dossiers, users):
    print("\n📅 Création des événements...")
    evenements = []
    
    types_events = list(EVENT_TYPES.keys())[:3] if EVENT_TYPES else ['audience', 'rendez_vous', 'reunion']
    
    for i in range(50):
        dossier = random.choice(dossiers)
        
        start_date = date.today() + timedelta(days=random.randint(1, 90))
        start_time = datetime.strptime(f"{random.randint(8, 17)}:00", "%H:%M").time()
        
        event = Event.objects.create(
            title=f"Événement {dossier.reference_code}",
            type=random.choice(types_events),
            start_date=start_date,
            start_time=start_time,
            all_day=False,
            end_date=start_date,
            end_time=start_time,
            location='Cabinet',
            description=f"Événement lié au dossier",
            dossier=dossier,
            created_by=dossier.responsible,
        )
        evenements.append(event)
    
    print(f"✓ {len(evenements)} événements créés")
    return evenements

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("   PEUPLEMENT GED CABINET GABON - VERSION FINALE")
    print("=" * 70)
    
    try:
        users = creer_utilisateurs()
        clients = creer_clients()
        dossiers = creer_dossiers(clients, users)
        evenements = creer_evenements(dossiers, users)
        
        print("\n" + "=" * 70)
        print("✅ PEUPLEMENT RÉUSSI !")
        print("=" * 70)
        print(f"\n📊 Statistiques:")
        print(f"   • Utilisateurs: {User.objects.count()}")
        print(f"   • Clients: {Client.objects.count()}")
        print(f"   • Dossiers: {Dossier.objects.count()}")
        print(f"   • Événements: {Event.objects.count()}")
        
        print(f"\n🔐 Connexion:")
        print(f"   admin / admin123")
        print(f"   marie.ondo / avocat123")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()