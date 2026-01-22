# Utilisation d'une image Python stable et légère
FROM python:3.12-slim

# Empêche Python d'écrire des fichiers .pyc et d'utiliser un tampon pour les logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installation des dépendances système nécessaires (Postgres, Pillow, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    && apt-get clean

# Définition du répertoire de travail
WORKDIR /app

# Installation des dépendances Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . /app/

# Script d'entrée pour les migrations et le lancement
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]