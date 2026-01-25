"""
Script d'extraction complète des détails de tous les modèles Django.
Affiche : tables, champs, types, choix, contraintes, relations, validations.

Usage: python get_models_details.py > models_complete.txt
"""
import os
import django
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.apps import apps
from django.db import models
import inspect


def print_separator(char='=', length=80):
    """Affiche un séparateur"""
    print(char * length)


def get_field_details(field):
    """Extrait tous les détails d'un champ"""
    details = []
    
    # Type de champ
    field_type = field.__class__.__name__
    details.append(f"Type: {field_type}")
    
    # Contraintes de base
    if hasattr(field, 'max_length') and field.max_length:
        details.append(f"max_length={field.max_length}")
    
    if hasattr(field, 'null'):
        details.append(f"null={field.null}")
    
    if hasattr(field, 'blank'):
        details.append(f"blank={field.blank}")
    
    if hasattr(field, 'unique') and field.unique:
        details.append(f"UNIQUE")
    
    if hasattr(field, 'default') and field.default != models.NOT_PROVIDED:
        default_val = field.default
        if callable(default_val):
            details.append(f"default={default_val.__name__}()")
        else:
            details.append(f"default={repr(default_val)}")
    
    # Choix
    if hasattr(field, 'choices') and field.choices:
        details.append(f"CHOICES:")
        for value, label in field.choices:
            details.append(f"    → '{value}': {label}")
    
    # Relations
    if hasattr(field, 'related_model') and field.related_model:
        related_name = field.related_model.__name__
        details.append(f"relation → {related_name}")
        
        if hasattr(field, 'on_delete'):
            on_delete = field.on_delete.__name__
            details.append(f"on_delete={on_delete}")
        
        if hasattr(field, 'related_name'):
            details.append(f"related_name='{field.related_name}'")
    
    # Validators
    if hasattr(field, 'validators') and field.validators:
        details.append(f"Validators:")
        for validator in field.validators:
            validator_name = getattr(validator, '__name__', str(validator))
            details.append(f"    → {validator_name}")
    
    # Help text
    if hasattr(field, 'help_text') and field.help_text:
        details.append(f"help_text: {field.help_text}")
    
    # Verbose name
    if hasattr(field, 'verbose_name') and field.verbose_name:
        details.append(f"verbose_name: {field.verbose_name}")
    
    return details


def get_model_constraints(model):
    """Extrait les contraintes du modèle"""
    constraints = []
    
    if hasattr(model._meta, 'constraints'):
        for constraint in model._meta.constraints:
            constraint_type = constraint.__class__.__name__
            constraint_name = getattr(constraint, 'name', 'unnamed')
            constraints.append(f"  • {constraint_type}: {constraint_name}")
            
            # Détails spécifiques
            if hasattr(constraint, 'fields'):
                constraints.append(f"    Fields: {list(constraint.fields)}")
            
            if hasattr(constraint, 'condition') and constraint.condition:
                constraints.append(f"    Condition: {constraint.condition}")
    
    return constraints


def get_model_indexes(model):
    """Extrait les index du modèle"""
    indexes = []
    
    if hasattr(model._meta, 'indexes'):
        for index in model._meta.indexes:
            index_name = getattr(index, 'name', 'unnamed')
            fields = getattr(index, 'fields', [])
            indexes.append(f"  • Index '{index_name}': {list(fields)}")
    
    return indexes


def get_model_methods(model):
    """Extrait les méthodes importantes du modèle"""
    methods = []
    
    # Méthodes personnalisées (exclure les méthodes Django de base)
    django_methods = dir(models.Model)
    
    for name, method in inspect.getmembers(model, predicate=inspect.isfunction):
        if name not in django_methods and not name.startswith('_'):
            # Récupérer la signature
            try:
                sig = inspect.signature(method)
                methods.append(f"  • {name}{sig}")
            except:
                methods.append(f"  • {name}()")
    
    return methods


def analyze_all_models():
    """Analyse complète de tous les modèles"""
    
    print_separator('=')
    print(" " * 20 + "ANALYSE COMPLÈTE DES MODÈLES DJANGO")
    print(" " * 20 + "GED CABINET - GABON")
    print_separator('=')
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base de données: SQLite (développement)")
    print_separator('=')
    
    # Parcourir toutes les apps
    for app_config in apps.get_app_configs():
        app_name = app_config.name
        
        # Ignorer les apps Django de base
        if app_name.startswith('django.contrib') or app_name in ['rest_framework', 'corsheaders', 'guardian', 'django_filters']:
            continue
        
        models_list = app_config.get_models()
        if not models_list:
            continue
        
        print(f"\n\n{'#' * 80}")
        print(f"# APPLICATION: {app_name}")
        print(f"{'#' * 80}\n")
        
        for model in models_list:
            print_separator('-', 80)
            print(f"📋 MODÈLE: {model.__name__}")
            print_separator('-', 80)
            
            # Informations de base
            print(f"\n🏷️  INFORMATIONS GÉNÉRALES:")
            print(f"   Table: {model._meta.db_table}")
            print(f"   App: {model._meta.app_label}")
            print(f"   Verbose name: {model._meta.verbose_name}")
            print(f"   Verbose name plural: {model._meta.verbose_name_plural}")
            
            # Champs
            print(f"\n📊 CHAMPS ({len(model._meta.get_fields())} champs):")
            
            for field in model._meta.get_fields():
                # Ignorer les relations inverses
                if field.auto_created and not field.concrete:
                    continue
                
                print(f"\n   └─ {field.name}")
                
                details = get_field_details(field)
                for detail in details:
                    if detail.startswith('CHOICES:') or detail.startswith('Validators:'):
                        print(f"      {detail}")
                    elif detail.startswith('   '):
                        print(f"   {detail}")
                    else:
                        print(f"      {detail}")
            
            # Contraintes
            constraints = get_model_constraints(model)
            if constraints:
                print(f"\n🔒 CONTRAINTES:")
                for constraint in constraints:
                    print(constraint)
            
            # Index
            indexes = get_model_indexes(model)
            if indexes:
                print(f"\n📑 INDEX:")
                for index in indexes:
                    print(index)
            
            # Meta options
            print(f"\n⚙️  META OPTIONS:")
            if hasattr(model._meta, 'ordering') and model._meta.ordering:
                print(f"   • Ordering: {model._meta.ordering}")
            
            if hasattr(model._meta, 'unique_together') and model._meta.unique_together:
                print(f"   • Unique together: {model._meta.unique_together}")
            
            if hasattr(model._meta, 'permissions') and model._meta.permissions:
                print(f"   • Permissions: {model._meta.permissions}")
            
            # Méthodes personnalisées
            methods = get_model_methods(model)
            if methods:
                print(f"\n🔧 MÉTHODES PERSONNALISÉES:")
                for method in methods:
                    print(method)
            
            print()  # Ligne vide


def extract_choices_summary():
    """Extrait un résumé rapide de tous les choix"""
    print("\n\n")
    print_separator('=')
    print(" " * 25 + "RÉSUMÉ DES CHOIX (CHOICES)")
    print_separator('=')
    
    choices_found = {}
    
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('django.contrib'):
            continue
            
        for model in app_config.get_models():
            for field in model._meta.get_fields():
                if hasattr(field, 'choices') and field.choices and field.concrete:
                    key = f"{model.__name__}.{field.name}"
                    choices_found[key] = list(field.choices)
    
    if choices_found:
        for field_path, choices in sorted(choices_found.items()):
            print(f"\n{field_path}:")
            for value, label in choices:
                print(f"  '{value}' → {label}")
    else:
        print("\nAucun choix trouvé.")


def extract_required_fields():
    """Extrait les champs obligatoires (null=False, blank=False)"""
    print("\n\n")
    print_separator('=')
    print(" " * 20 + "CHAMPS OBLIGATOIRES (null=False, blank=False)")
    print_separator('=')
    
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('django.contrib'):
            continue
        
        for model in app_config.get_models():
            required = []
            
            for field in model._meta.get_fields():
                if not field.concrete or field.auto_created:
                    continue
                
                is_required = (
                    hasattr(field, 'null') and not field.null and
                    hasattr(field, 'blank') and not field.blank and
                    not hasattr(field, 'default')
                )
                
                if is_required:
                    field_type = field.__class__.__name__
                    required.append(f"  • {field.name} ({field_type})")
            
            if required:
                print(f"\n{model.__name__}:")
                for req in required:
                    print(req)


def main():
    """Exécute l'analyse complète"""
    
    # Analyse détaillée
    analyze_all_models()
    
    # Résumé des choix
    extract_choices_summary()
    
    # Champs obligatoires
    extract_required_fields()
    
    print("\n\n")
    print_separator('=')
    print("✅ ANALYSE TERMINÉE")
    print_separator('=')
    print("\nFichier généré avec succès!")
    print("Utilisez les informations ci-dessus pour créer des scripts de peuplement sans erreurs.")


if __name__ == '__main__':
    main()