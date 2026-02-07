from django.db import migrations, models


def migrate_sensitivity_values(apps, schema_editor):
    """Migre les anciennes valeurs de sensibilité vers les nouvelles."""
    Document = apps.get_model('documents', 'Document')
    mapping = {
        'public': 'NORMAL',
        'internal': 'NORMAL',
        'confidential': 'CONFIDENTIAL',
        'secret': 'CRITICAL',
    }
    for old_val, new_val in mapping.items():
        Document.objects.filter(sensitivity=old_val).update(sensitivity=new_val)


def reverse_sensitivity_values(apps, schema_editor):
    """Reverse : remet les anciennes valeurs."""
    Document = apps.get_model('documents', 'Document')
    mapping = {
        'NORMAL': 'internal',
        'CONFIDENTIAL': 'confidential',
        'CRITICAL': 'secret',
    }
    for old_val, new_val in mapping.items():
        Document.objects.filter(sensitivity=old_val).update(sensitivity=new_val)


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        # 1. D'abord, migrer les données existantes
        migrations.RunPython(migrate_sensitivity_values, reverse_sensitivity_values),

        # 2. Puis changer les choices et le default
        migrations.AlterField(
            model_name='document',
            name='sensitivity',
            field=models.CharField(
                choices=[
                    ('NORMAL', 'Normal'),
                    ('CONFIDENTIAL', 'Confidentiel'),
                    ('CRITICAL', 'Secret Professionnel'),
                ],
                default='NORMAL',
                max_length=20,
                verbose_name='Niveau de sensibilité',
            ),
        ),
    ]
