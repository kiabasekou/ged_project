import os
import django
from django.apps import apps

# Initialiser Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # adapte "config.settings" à ton projet
django.setup()

# Fichier de sortie
output_file = "django_models_details.txt"

with open(output_file, "w", encoding="utf-8") as f:
    for app_config in apps.get_app_configs():
        f.write(f"\n=== Application: {app_config.name} ===\n")
        for model in app_config.get_models():
            f.write(f"\n--- Modèle: {model.__name__} ---\n")
            f.write(f"Table: {model._meta.db_table}\n")
            f.write("Champs:\n")
            for field in model._meta.get_fields():
                field_info = f"  - {field.name} ({field.__class__.__name__})"
                if hasattr(field, "max_length") and field.max_length:
                    field_info += f", max_length={field.max_length}"
                if hasattr(field, "related_model") and field.related_model:
                    field_info += f", relation -> {field.related_model.__name__}"
                f.write(field_info + "\n")