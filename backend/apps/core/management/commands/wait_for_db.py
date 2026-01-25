"""
Management command pour attendre que la base de données soit prête.
Utile lors du démarrage de Docker Compose.
"""
import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Attend que la base de données soit disponible avant de continuer"

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Temps maximum d\'attente en secondes (défaut: 30)'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=1,
            help='Intervalle entre les tentatives en secondes (défaut: 1)'
        )

    def handle(self, *args, **options):
        timeout = options['timeout']
        interval = options['interval']
        
        self.stdout.write('En attente de la base de données...')
        
        db_conn = None
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                db_conn = connections['default']
                db_conn.cursor()
                break
            except OperationalError:
                self.stdout.write(
                    self.style.WARNING(
                        f'Base de données indisponible, nouvelle tentative dans {interval}s...'
                    )
                )
                time.sleep(interval)
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'Impossible de se connecter à la base de données après {timeout}s'
                )
            )
            raise OperationalError('Timeout de connexion à la base de données')
        
        self.stdout.write(self.style.SUCCESS('✓ Base de données disponible !'))