import os
from pathlib import Path
import environ
from datetime import timedelta


# Initialisation de django-environ
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
)

# Construction des chemins
BASE_DIR = Path(__file__).resolve().parent.parent

# Lecture du fichier .env
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# --- État de l'environnement ---
# Valeurs possibles : 'development', 'production', 'deployment' (on-premise)
DJANGO_ENV = env.str('DJANGO_ENV', default='development')

# --- Paramètres de base ---
SECRET_KEY = env.str('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)

if DJANGO_ENV == 'development':
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Token court pour la sécurité
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),    # Renouvellement possible sur 24h
    'ROTATE_REFRESH_TOKENS': True,                 # Sécurité accrue : change le refresh à chaque usage
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# --- Applications ---
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'guardian',  # ← À ajouter
    
]
# Backends d'authentification pour supporter les permissions par objet
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',      # Auth classique
    'guardian.backends.ObjectPermissionBackend',      # Permissions par objet
)
THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'rest_framework_guardian',


]

# Les applications locales seront créées dans les étapes suivantes
LOCAL_APPS = [
    'apps.core',
    'apps.users',
    'apps.clients',
    'apps.dossiers',
    'apps.documents',
    'apps.audit',
    'apps.agenda',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# --- Middleware ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Placé avant CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Middleware personnalisé pour l'audit log (à créer plus tard)
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- Base de données ---


DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}

# --- Authentification et Sécurité ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'users.User' # Préparation du modèle personnalisé

# --- Configuration DRF ---
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

# --- Internationalisation (Adapté Gabon/OHADA) ---
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Libreville'
USE_I18N = True
USE_TZ = True

# --- Gestion des fichiers (GED) ---
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = 'media/'
# En mode 'deployment' (on-premise), on peut définir un chemin absolu externe 
# au projet pour faciliter les sauvegardes du serveur physique.
if DJANGO_ENV == 'deployment':
    MEDIA_ROOT = env.str('MEDIA_ROOT_PATH', default=os.path.join(BASE_DIR, 'media'))
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- Configuration spécifique aux environnements ---

if DJANGO_ENV == 'development':
    CORS_ALLOW_ALL_ORIGINS = True
    # Sécurité minimale pour le dev
    SECURE_SSL_REDIRECT = False

elif DJANGO_ENV in ['production', 'deployment']:
    # Sécurité renforcée
    CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')
    
    # Paramètres de cookies et session sécurisés
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # HSTS (uniquement si SSL est géré par Nginx en amont)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    if DJANGO_ENV == 'deployment':
        # Paramètres spécifiques au serveur local du cabinet
        # Augmentation de la taille max pour l'upload de gros dossiers d'actes
        DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
        FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'