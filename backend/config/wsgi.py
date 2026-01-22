import os
from django.core.wsgi import get_wsgi_application

# On définit le module de réglages par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# C'est cette variable 'application' que Django cherche et ne trouvait pas
application = get_wsgi_application()