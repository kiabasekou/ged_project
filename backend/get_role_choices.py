import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User

# Récupérer les choix du champ role
role_field = User._meta.get_field('role')

print("=" * 60)
print("CHOIX VALIDES POUR LE CHAMP 'role'")
print("=" * 60)

if hasattr(role_field, 'choices') and role_field.choices:
    for value, label in role_field.choices:
        print(f"  '{value}' -> {label}")
else:
    print("  Aucun choix défini (champ libre)")

print("\n" + "=" * 60)