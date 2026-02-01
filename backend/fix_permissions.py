#!/usr/bin/env python
"""
Script de correction des permissions des dossiers - GED Cabinet Kiaba

RÈGLES MÉTIER :
1. Superutilisateurs → Accès à TOUS les dossiers
2. Administrateurs (is_staff) → Accès à TOUS les dossiers  
3. Avocats/Notaires/Conseillers → Leurs dossiers + collaborations
4. Autres utilisateurs → Uniquement où ils sont assignés
"""

import os
import sys
import django

# Configuration Django
sys.path.insert(0, '/mnt/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.dossiers.models import Dossier
from guardian.shortcuts import assign_perm, remove_perm, get_perms
from django.db.models import Q

User = get_user_model()

# Couleurs pour l'affichage
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message):
    """Affiche un en-tête formaté"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(message):
    """Affiche un message de succès"""
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_warning(message):
    """Affiche un avertissement"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def print_error(message):
    """Affiche une erreur"""
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_info(message):
    """Affiche une information"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.ENDC}")


def audit_permissions():
    """Audit des permissions actuelles"""
    print_header("AUDIT DES PERMISSIONS ACTUELLES")
    
    dossiers = Dossier.objects.all()
    users = User.objects.filter(is_active=True)
    
    print_info(f"Total dossiers: {dossiers.count()}")
    print_info(f"Total utilisateurs actifs: {users.count()}")
    print()
    
    # Statistiques par rôle
    roles_count = {}
    for user in users:
        role = user.role or 'UNKNOWN'
        roles_count[role] = roles_count.get(role, 0) + 1
    
    print(f"{Colors.BOLD}Utilisateurs par rôle:{Colors.ENDC}")
    for role, count in sorted(roles_count.items()):
        print(f"  - {role}: {count}")
    print()
    
    # Dossiers par responsable
    print(f"{Colors.BOLD}Répartition des dossiers:{Colors.ENDC}")
    for user in users.filter(role__in=['AVOCAT', 'NOTAIRE', 'CONSEIL_JURIDIQUE']):
        dossier_count = Dossier.objects.filter(responsible=user).count()
        if dossier_count > 0:
            print(f"  - {user.get_full_name()}: {dossier_count} dossier(s)")
    print()


def fix_responsible_permissions():
    """S'assure que tous les responsables ont bien les permissions sur leurs dossiers"""
    print_header("CORRECTION DES PERMISSIONS DES RESPONSABLES")
    
    dossiers = Dossier.objects.all()
    fixed_count = 0
    
    for dossier in dossiers:
        responsible = dossier.responsible
        
        # Vérifier les permissions existantes
        current_perms = get_perms(responsible, dossier)
        required_perms = ['view_dossier', 'change_dossier', 'delete_dossier']
        
        missing_perms = [p for p in required_perms if p not in current_perms]
        
        if missing_perms:
            print_warning(f"Dossier {dossier.reference_code} - Permissions manquantes pour {responsible.get_full_name()}")
            
            for perm in missing_perms:
                assign_perm(perm, responsible, dossier)
                print_success(f"  → Permission '{perm}' ajoutée")
            
            fixed_count += 1
    
    if fixed_count == 0:
        print_success("Toutes les permissions des responsables sont correctes")
    else:
        print_success(f"{fixed_count} dossier(s) corrigé(s)")
    print()


def fix_collaborator_permissions():
    """S'assure que tous les collaborateurs ont les bonnes permissions"""
    print_header("CORRECTION DES PERMISSIONS DES COLLABORATEURS")
    
    dossiers = Dossier.objects.all()
    fixed_count = 0
    
    for dossier in dossiers:
        for collaborator in dossier.assigned_users.all():
            # Vérifier les permissions existantes
            current_perms = get_perms(collaborator, dossier)
            
            # Permissions minimales pour un collaborateur
            if 'view_dossier' not in current_perms:
                assign_perm('view_dossier', collaborator, dossier)
                print_success(f"  → Permission 'view' ajoutée pour {collaborator.get_full_name()} sur {dossier.reference_code}")
                fixed_count += 1
            
            # Les avocats/notaires collaborateurs devraient avoir 'change'
            if collaborator.role in ['AVOCAT', 'NOTAIRE', 'CONSEIL_JURIDIQUE']:
                if 'change_dossier' not in current_perms:
                    assign_perm('change_dossier', collaborator, dossier)
                    print_success(f"  → Permission 'change' ajoutée pour {collaborator.get_full_name()} sur {dossier.reference_code}")
                    fixed_count += 1
    
    if fixed_count == 0:
        print_success("Toutes les permissions des collaborateurs sont correctes")
    else:
        print_success(f"{fixed_count} permission(s) corrigée(s)")
    print()


def remove_orphan_permissions():
    """Supprime les permissions orphelines (utilisateurs qui ne sont ni responsables ni collaborateurs)"""
    print_header("NETTOYAGE DES PERMISSIONS ORPHELINES")
    
    # Cette partie nécessite Django Guardian
    # Pour l'instant, on fait un simple audit
    
    print_info("Vérification des permissions orphelines...")
    
    # À implémenter si nécessaire
    print_warning("Fonctionnalité non implémentée - nécessite analyse Guardian avancée")
    print()


def verify_queryset_filtering():
    """Vérifie que le filtrage QuerySet fonctionne correctement"""
    print_header("VÉRIFICATION DU FILTRAGE PAR RÔLE")
    
    users = User.objects.filter(is_active=True)
    
    for user in users:
        # Simuler le queryset du ViewSet
        if user.is_superuser or user.is_staff:
            accessible_dossiers = Dossier.objects.all()
        elif user.role in ['AVOCAT', 'NOTAIRE', 'CONSEIL_JURIDIQUE']:
            accessible_dossiers = Dossier.objects.filter(
                Q(responsible=user) | Q(assigned_users=user)
            ).distinct()
        else:
            accessible_dossiers = Dossier.objects.filter(assigned_users=user).distinct()
        
        count = accessible_dossiers.count()
        
        if count > 0:
            print_info(f"{user.get_full_name()} ({user.role}): {count} dossier(s) accessibles")
        
    print()


def generate_report():
    """Génère un rapport détaillé"""
    print_header("RAPPORT DÉTAILLÉ DES PERMISSIONS")
    
    dossiers = Dossier.objects.all()
    
    for dossier in dossiers[:5]:  # Limiter à 5 pour la lisibilité
        print(f"\n{Colors.BOLD}Dossier: {dossier.reference_code}{Colors.ENDC}")
        print(f"  Client: {dossier.client.get_display_name()}")
        print(f"  Responsable: {dossier.responsible.get_full_name()} ({dossier.responsible.role})")
        
        collaborators = dossier.assigned_users.all()
        if collaborators.exists():
            print(f"  Collaborateurs:")
            for collab in collaborators:
                perms = get_perms(collab, dossier)
                print(f"    - {collab.get_full_name()} ({collab.role}): {', '.join(perms)}")
        else:
            print(f"  Collaborateurs: Aucun")
    
    if dossiers.count() > 5:
        print(f"\n{Colors.YELLOW}... et {dossiers.count() - 5} autres dossiers{Colors.ENDC}")
    print()


def main():
    """Fonction principale"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     CORRECTION DES PERMISSIONS - GED CABINET KIABA             ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    try:
        # 1. Audit initial
        audit_permissions()
        
        # 2. Correction des permissions des responsables
        fix_responsible_permissions()
        
        # 3. Correction des permissions des collaborateurs
        fix_collaborator_permissions()
        
        # 4. Nettoyage (si nécessaire)
        # remove_orphan_permissions()
        
        # 5. Vérification du filtrage
        verify_queryset_filtering()
        
        # 6. Rapport final
        generate_report()
        
        print_header("OPÉRATION TERMINÉE AVEC SUCCÈS")
        print_success("Toutes les permissions ont été vérifiées et corrigées")
        print()
        
    except Exception as e:
        print_error(f"Erreur lors de l'exécution: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()