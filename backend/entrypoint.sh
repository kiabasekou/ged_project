#!/bin/sh

# Attendre que la base de données soit disponible
echo "Attente de la base de données..."
# Optionnel : ajouter un test de connexion netcat (nc) ici

# Appliquer les migrations
echo "Application des migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques
echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Lancer l'application
exec "$@"