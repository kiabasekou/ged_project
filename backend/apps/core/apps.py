"""
Configuration de l'application Core.
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core - Fondation'
    
    def ready(self):
        """
        Code exécuté au démarrage de l'application.
        Idéal pour enregistrer les signals, etc.
        """
        # Importer les signals si nécessaire
        # import apps.core.signals
        pass