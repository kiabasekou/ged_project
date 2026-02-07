from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='priority',
            field=models.CharField(
                choices=[
                    ('LOW', 'Faible'),
                    ('NORMAL', 'Normal'),
                    ('HIGH', 'Haute'),
                    ('URGENT', 'Urgente'),
                ],
                default='NORMAL',
                max_length=10,
                verbose_name='Priorité',
            ),
        ),
        migrations.AddField(
            model_name='event',
            name='reminder',
            field=models.CharField(
                blank=True,
                choices=[
                    ('NONE', 'Aucun'),
                    ('15MIN', '15 minutes avant'),
                    ('30MIN', '30 minutes avant'),
                    ('1H', '1 heure avant'),
                    ('24H', '24 heures avant'),
                ],
                default='NONE',
                max_length=10,
                verbose_name='Rappel',
            ),
        ),
    ]
