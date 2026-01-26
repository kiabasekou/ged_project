"""
Script de peuplement complet GED Cabinet Gabon.
✅ Formats RCCM et NIF conformes aux standards officiels gabonais
✅ RCCM : GA-LBV-YYYY-AXX-NNNNN (standard OHADA)
✅ NIF : XXXXXX-L (6 chiffres + lettre de contrôle)
"""
import os
import sys
import django
from datetime import datetime, timedelta, date
import random
import re
import unicodedata

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.clients.models import Client
from apps.dossiers.models import Dossier
from apps.documents.models import Folder, Document
from apps.audit.models import AuditLog
from apps.agenda.models import Event
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db import connection

User = get_user_model()

# ============================================================================
# CHOIX CORRECTS
# ============================================================================

USER_ROLES = {
    'ADMIN': 'Administrateur système',
    'AVOCAT': 'Avocat',
    'NOTAIRE': 'Notaire',
    'CONSEIL_JURIDIQUE': 'Conseil juridique',
    'STAGIAIRE': 'Stagiaire / Collaborateur',
    'SECRETAIRE': 'Secrétaire / Clerc',
    'ASSISTANT': 'Assistant juridique',
}

CLIENT_TYPES = {
    'PHYSIQUE': 'Personne Physique',
    'MORALE': 'Personne Morale',
}

DOSSIER_CATEGORIES = {
    'CONTENTIEUX': 'Contentieux',
    'CONSEIL': 'Conseil juridique',
    'RECOUVREMENT': 'Recouvrement',
    'TRAVAIL': 'Droit du travail',
    'IMMOBILIER': 'Actes immobiliers',
    'SUCCESSION': 'Succession',
    'FAMILLE': 'Divorce, garde, filiation',
    'COMMERCIAL': 'Droit commercial OHADA',
    'AUTRE': 'Autre',
}

DOSSIER_STATUS = {
    'OUVERT': 'Ouvert',
    'ATTENTE': 'En attente',
    'SUSPENDU': 'Suspendu',
    'CLOTURE': 'Clôturé',
    'ARCHIVE': 'Archivé',
}

EVENT_TYPES = {
    'AUDIENCE': 'Audience',
    'RDV': 'Rendez-vous client',
    'FORMALITE': 'Formalité notariale',
    'CONGE': 'Congé',
    'AUTRE': 'Autre événement',
}

# ============================================================================
# DONNÉES GABON
# ============================================================================

QUARTIERS_LIBREVILLE = [
    'Quartier Louis', 'Lalala', 'Nzeng-Ayong', 'Akébé', 'PK8', 'PK9',
    'Glass', 'Batavéa', 'Mont-Bouët', 'Nombakélé', 'Mindoubé'
]

VILLES_GABON = [
    'Libreville', 'Port-Gentil', 'Franceville', 'Oyem', 'Lambaréné',
    'Mouila', 'Tchibanga', 'Koulamoutou', 'Moanda'
]

PRENOMS_M = ['Jean-Baptiste', 'Pierre', 'Paul', 'André', 'Michel', 'Louis', 'Patrick', 'Eric']
PRENOMS_F = ['Marie', 'Anne', 'Christine', 'Sylvie', 'Catherine', 'Nicole', 'Brigitte']
NOMS = ['Obame', 'Nguema', 'Ndong', 'Mba', 'Ondo', 'Bekale', 'Nze', 'Koumba', 'Moukala', 'Ntoutoume']

ENTREPRISES = [
    'BGFIBank Gabon', 'UGB', 'SEEG', 'Total Gabon', 'Shell Gabon',
    'Gabon Telecom', 'Airtel Gabon', 'COMILOG', 'SETRAG', 'Olam Gabon'
]

# ============================================================================
# UTILITAIRES
# ============================================================================

def nettoyer_pour_email(texte):
    """
    Nettoie un texte pour l'utiliser dans une adresse email.
    Supprime accents, espaces, tirets, caractères spéciaux.
    """
    texte = texte.lower()
    texte = unicodedata.normalize('NFD', texte)
    texte = ''.join(char for char in texte if unicodedata.category(char) != 'Mn')
    texte = re.sub(r'[^a-z0-9]', '', texte)
    return texte

def generer_email(prenom, nom, index):
    """Génère une adresse email valide"""
    prenom_clean = nettoyer_pour_email(prenom)
    nom_clean = nettoyer_pour_email(nom)
    return f'{prenom_clean}.{nom_clean}.{index}@gmail.com'

def generer_ni(index):
    """
    NI gabonais unique : 10 chiffres
    Format: 1NNNNNNNNN (commence par 1)
    """
    base = 1000000000 + index
    return str(base)

def generer_nif(index):
    """
    NIF gabonais conforme : XXXXXX-L
    Format: 6 chiffres + lettre de contrôle
    Exemple: 370669-C, 123456-A
    """
    numero = 300000 + index  # Commence à 300000
    lettre = chr(65 + (index % 26))  # A-Z pour la lettre de contrôle
    return f"{numero}-{lettre}"

def generer_rccm(index):
    """
    RCCM gabonais conforme au standard OHADA
    Format: GA-LBV-YYYY-AXX-NNNNN
    Exemple: GA-LBV-2024-A12-00567
    
    Structure:
    - GA-LBV : Gabon-Libreville (juridiction)
    - 2024 : Année d'immatriculation
    - A12 : Type de registre (A) + secteur (12)
    - 00567 : Numéro séquentiel
    """
    annee = 2024
    type_registre = 'A'  # A pour personnes morales principales
    secteur = 10 + (index % 90)  # Secteurs de 10 à 99
    numero = index + 1  # Numéro séquentiel
    
    return f"GA-LBV-{annee}-{type_registre}{secteur:02d}-{numero:05d}"

def generer_telephone():
    """Téléphone gabonais : +241 XX XXX XXX"""
    prefixe = random.choice(['06', '07', '05'])
    numero = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return f"+241{prefixe}{numero}"

def generer_reference(index):
    """Code référence dossier : GAB-2024-XXXX"""
    annee = 2024
    return f"GAB-{annee}-{index+1:04d}"

def print_header(text):
    """Affiche un en-tête"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print('='*70)

# ============================================================================
# RÉINITIALISATION BASE
# ============================================================================

def reinitialiser_base():
    """Supprime toutes les données"""
    print_header("🔄 RÉINITIALISATION DE LA BASE DE DONNÉES")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = OFF")
        
        print("  ⏳ Suppression des événements...")
        Event.objects.all().delete()
        
        print("  ⏳ Suppression des documents...")
        Document.objects.all().delete()
        
        print("  ⏳ Suppression des dossiers (folders)...")
        Folder.objects.all().delete()
        
        print("  ⏳ Suppression des dossiers juridiques...")
        Dossier.objects.all().delete()
        
        print("  ⏳ Suppression des clients...")
        Client.objects.all().delete()
        
        print("  ⏳ Suppression des logs d'audit...")
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM audit_auditlog")
        
        print("  ⏳ Suppression des utilisateurs...")
        User.objects.all().delete()
        
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence")
            cursor.execute("PRAGMA foreign_keys = ON")
        
        print("  ✅ Base de données réinitialisée avec succès!")
        
    except Exception as e:
        print(f"  ❌ Erreur lors de la réinitialisation: {str(e)}")
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = ON")
        raise

# ============================================================================
# CRÉATION UTILISATEURS
# ============================================================================

def creer_utilisateurs():
    """Crée les utilisateurs du cabinet"""
    print_header("👥 CRÉATION DES UTILISATEURS")
    
    users = []
    
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@cabinet-gabon.ga',
        password='admin123',
        first_name='Jean-Baptiste',
        last_name='Obame Nguema',
        role='ADMIN',
        professional_id='BAR/GAB/2010/001',
        phone_number=generer_telephone(),
        has_accepted_privacy_policy=True,
        privacy_policy_accepted_at=timezone.now()
    )
    users.append(admin)
    print(f"  ✅ Admin: {admin.get_full_name()} ({admin.role})")
    
    avocats_data = [
        ('marie.ondo', 'Marie-Claire', 'Ondo Ela', 'AVOCAT', 'BAR/GAB/2012/045'),
        ('pierre.nze', 'Pierre', 'Nze Bekale', 'AVOCAT', 'BAR/GAB/2015/089'),
        ('christine.mba', 'Christine', 'Mba Nguema', 'AVOCAT', 'BAR/GAB/2018/124'),
    ]
    
    for username, prenom, nom, role, prof_id in avocats_data:
        user = User.objects.create_user(
            username=username,
            email=f'{username}@cabinet-gabon.ga',
            password='avocat123',
            first_name=prenom,
            last_name=nom,
            role=role,
            professional_id=prof_id,
            phone_number=generer_telephone(),
            is_staff=True,
            has_accepted_privacy_policy=True,
            privacy_policy_accepted_at=timezone.now()
        )
        users.append(user)
        print(f"  ✅ Avocat: {user.get_full_name()}")
    
    notaire = User.objects.create_user(
        username='paul.meye',
        email='paul.meye@cabinet-gabon.ga',
        password='notaire123',
        first_name='Paul',
        last_name='Meye Essono',
        role='NOTAIRE',
        professional_id='NOT/GAB/001',
        phone_number=generer_telephone(),
        is_staff=True,
        has_accepted_privacy_policy=True,
        privacy_policy_accepted_at=timezone.now()
    )
    users.append(notaire)
    print(f"  ✅ Notaire: {notaire.get_full_name()}")
    
    collaborateurs_data = [
        ('sylvie.koumba', 'Sylvie', 'Koumba', 'SECRETAIRE'),
        ('paul.moukala', 'Paul', 'Moukala', 'ASSISTANT'),
        ('anne.ntoutoume', 'Anne', 'Ntoutoume', 'STAGIAIRE'),
    ]
    
    for username, prenom, nom, role in collaborateurs_data:
        user = User.objects.create_user(
            username=username,
            email=f'{username}@cabinet-gabon.ga',
            password='collab123',
            first_name=prenom,
            last_name=nom,
            role=role,
            phone_number=generer_telephone(),
            has_accepted_privacy_policy=True,
            privacy_policy_accepted_at=timezone.now()
        )
        users.append(user)
        print(f"  ✅ {role.title()}: {user.get_full_name()}")
    
    print(f"\n  📊 Total: {len(users)} utilisateurs créés")
    return users

# ============================================================================
# CRÉATION CLIENTS
# ============================================================================

def creer_clients():
    """Crée les clients (particuliers et entreprises)"""
    print_header("🏢 CRÉATION DES CLIENTS")
    
    clients = []
    
    # Particuliers (25)
    print("  ⏳ Création des particuliers...")
    for i in range(25):
        prenom = random.choice(PRENOMS_M + PRENOMS_F)
        nom = random.choice(NOMS)
        
        email = generer_email(prenom, nom, i)
        
        client = Client.objects.create(
            client_type='PHYSIQUE',
            first_name=prenom,
            last_name=nom,
            date_of_birth=date(1960, 1, 1) + timedelta(days=random.randint(0, 15000)),
            place_of_birth=random.choice(VILLES_GABON),
            ni_number=generer_ni(i),
            ni_type='CNI',
            email=email,
            phone_primary=generer_telephone(),
            phone_secondary=generer_telephone() if random.random() > 0.6 else None,
            address_line=f'BP {random.randint(1000, 9999)}',
            neighborhood=random.choice(QUARTIERS_LIBREVILLE),
            city='Libreville',
            country='Gabon',
            data_source='Consultation initiale',
            consent_given=True,
            consent_date=timezone.now() - timedelta(days=random.randint(1, 365)),
            retention_period_years=random.choice([5, 10, 15]),
            notes=f'Client particulier depuis {random.randint(2018, 2024)}',
        )
        clients.append(client)
    
    print(f"  ✅ {len(clients)} particuliers créés")
    
    # Entreprises (15)
    print("  ⏳ Création des entreprises...")
    count_entreprises = 0
    for i in range(15):
        entreprise = f"{random.choice(ENTREPRISES)} Succursale {i+1}"
        
        client = Client.objects.create(
            client_type='MORALE',
            company_name=entreprise,
            rccm=generer_rccm(i),  # Format: GA-LBV-2024-A12-00001
            nif=generer_nif(i),    # Format: 300000-A
            representative_name=f"{random.choice(PRENOMS_M)} {random.choice(NOMS)}",
            representative_role=random.choice(['Directeur Général', 'PDG', 'Gérant']),
            email=f'contact.entreprise{i}@gabon.ga',
            phone_primary=generer_telephone(),
            address_line=f'BP {random.randint(5000, 9999)}',
            neighborhood=random.choice(['Glass', 'Batavéa', 'Mont-Bouët']),
            city='Libreville',
            country='Gabon',
            data_source='Référence professionnelle',
            consent_given=True,
            consent_date=timezone.now() - timedelta(days=random.randint(30, 730)),
            retention_period_years=10,
            notes=f'Société {random.choice(["SA", "SARL", "SAS"])}',
        )
        clients.append(client)
        count_entreprises += 1
    
    print(f"  ✅ {count_entreprises} entreprises créées")
    print(f"\n  📊 Total: {len(clients)} clients créés")
    
    # Afficher quelques exemples
    print(f"\n  📋 Exemples de numéros générés:")
    exemple_entreprise = Client.objects.filter(client_type='MORALE').first()
    if exemple_entreprise:
        print(f"     • RCCM: {exemple_entreprise.rccm}")
        print(f"     • NIF:  {exemple_entreprise.nif}")
    
    return clients

# ============================================================================
# CRÉATION DOSSIERS
# ============================================================================

def creer_dossiers(clients):
    """Crée les dossiers juridiques"""
    print_header("📁 CRÉATION DES DOSSIERS JURIDIQUES")

    from apps.users.models import User
    # Correction : Retrait de 'ADMIN' pour respecter le limit_choices_to du modèle Dossier
    avocats = list(User.objects.filter(role__in=['AVOCAT', 'NOTAIRE', 'CONSEIL_JURIDIQUE']))

    if not avocats:
        print("❌ Aucun avocat trouvé en base")
        return []

    dossiers = []
    print(f"⏳ Création des dossiers (avec {len(avocats)} avocats disponibles)...")

    for i in range(40):
        client = random.choice(clients)
        avocat = random.choice(avocats)
        category = random.choice(list(DOSSIER_CATEGORIES.keys()))
        status = random.choice(list(DOSSIER_STATUS.keys()))

        date_ouverture = date.today() - timedelta(days=random.randint(1, 730))

        # Titre du dossier selon le type de client
        if client.client_type == 'PHYSIQUE':
            titre = f"{DOSSIER_CATEGORIES[category]} - {client.last_name}"
        else:
            titre = f"{DOSSIER_CATEGORIES[category]} - {client.company_name}"

        dossier = Dossier.objects.create(
            client=client,
            responsible=avocat,
            title=titre,
            reference_code=generer_reference(i),
            category=category,
            status=status,
            description=f"Dossier {DOSSIER_CATEGORIES[category].lower()}. "
                        f"Ouvert le {date_ouverture.strftime('%d/%m/%Y')}.",
            opponent=f"{random.choice(PRENOMS_M + PRENOMS_F)} {random.choice(NOMS)}",
            jurisdiction=random.choice([
                'Tribunal de Première Instance de Libreville',
                "Cour d'Appel de Libreville",
                'Tribunal de Commerce',
                "Conseil de Prud'hommes",
                'Office Notarial Libreville'
            ]),
            critical_deadline=(
                date_ouverture + timedelta(days=random.randint(30, 180))
                if status == 'OUVERT' else None
            ),
            legal_basis=random.choice(['Code Civil', 'Code Pénal', 'Code de Commerce', 'OHADA']),
            retention_period_years=random.choice([5, 10, 15, 20]),
            opening_date=date_ouverture,
            closing_date=(
                date_ouverture + timedelta(days=random.randint(180, 730))
                if status == 'CLOTURE' else None
            ),
        )

        # ✅ Collaborateurs pris en base aussi
        if random.random() < 0.3:
            collaborateurs = list(User.objects.filter(role__in=['ASSISTANT', 'STAGIAIRE']))
            if collaborateurs:
                dossier.assigned_users.set(
                    random.sample(collaborateurs, k=min(2, len(collaborateurs)))
                )

        dossiers.append(dossier)

    print(f"  ✅ {len(dossiers)} dossiers créés")
    return dossiers

# ============================================================================
# CRÉATION ÉVÉNEMENTS
# ============================================================================

def creer_evenements(dossiers, users):
    """Crée les événements d'agenda"""
    print_header("📅 CRÉATION DES ÉVÉNEMENTS")
    
    evenements = []
    
    print("  ⏳ Création des événements...")
    for i in range(60):
        dossier = random.choice(dossiers)
        type_event = random.choice(list(EVENT_TYPES.keys()))
        
        if random.random() < 0.7:
            start_date = date.today() + timedelta(days=random.randint(1, 90))
        else:
            start_date = date.today() - timedelta(days=random.randint(1, 180))
        
        heure = random.randint(8, 17)
        start_time = datetime.strptime(f"{heure}:00", "%H:%M").time()
        end_time = (datetime.combine(date.today(), start_time) + timedelta(hours=random.choice([1, 2, 3]))).time()
        
        titres = {
            'AUDIENCE': f"Audience - {dossier.jurisdiction}",
            'RDV': f"RDV {dossier.client.first_name or dossier.client.company_name}",
            'FORMALITE': f"Formalité - {dossier.reference_code}",
            'CONGE': f"Congé - {dossier.responsible.get_full_name()}",
            'AUTRE': f"Événement - {dossier.reference_code}",
        }
        
        event = Event.objects.create(
            title=titres[type_event],
            type=type_event,
            start_date=start_date,
            start_time=start_time,
            all_day=False,
            end_date=start_date,
            end_time=end_time,
            location='Cabinet - Libreville' if type_event == 'RDV' else dossier.jurisdiction,
            description=f"Événement lié au dossier {dossier.reference_code}",
            dossier=dossier,
            created_by=dossier.responsible,
        )
        evenements.append(event)
    
    print(f"  ✅ {len(evenements)} événements créés")
    return evenements

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Exécute le peuplement complet"""
    
    print("\n" + "="*70)
    print("  🇬🇦 PEUPLEMENT GED CABINET GABON")
    print("  📋 Formats conformes OHADA et DGI")
    print("="*70)
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Base: SQLite (développement)")
    print("="*70)
    
    try:
        reinitialiser_base()
        users = creer_utilisateurs()
        clients = creer_clients()
        dossiers = creer_dossiers(clients)
        evenements = creer_evenements(dossiers, users)
        
        print_header("✅ PEUPLEMENT TERMINÉ AVEC SUCCÈS")
        
        print(f"\n  📊 STATISTIQUES FINALES:")
        print(f"     • Utilisateurs:  {User.objects.count()}")
        print(f"     • Clients:       {Client.objects.count()}")
        print(f"       - Particuliers: {Client.objects.filter(client_type='PHYSIQUE').count()}")
        print(f"       - Entreprises:  {Client.objects.filter(client_type='MORALE').count()}")
        print(f"     • Dossiers:      {Dossier.objects.count()}")
        print(f"     • Événements:    {Event.objects.count()}")
        
        print(f"\n  🔐 IDENTIFIANTS DE CONNEXION:")
        print(f"\n     Admin Principal:")
        print(f"       Username: admin")
        print(f"       Password: admin123")
        
        print(f"\n     Avocats:")
        print(f"       Username: marie.ondo / Password: avocat123")
        print(f"       Username: pierre.nze / Password: avocat123")
        
        print(f"\n  🌐 ACCÈS:")
        print(f"     API:   http://localhost:8000/api/")
        print(f"     Admin: http://localhost:8000/admin/")
        
        print("\n" + "="*70)
        print("  🎉 Système opérationnel - Prêt pour utilisation !")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()