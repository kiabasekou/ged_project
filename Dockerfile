# ====================
# Stage 1: Backend Builder
# ====================
FROM python:3.11-slim as backend-builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY backend/requirements.txt .
RUN pip install --user -r requirements.txt

# ====================
# Stage 2: Frontend Builder
# ====================
FROM node:18-alpine as frontend-builder

WORKDIR /app

# Installation des dépendances
COPY frontend/package*.json ./
RUN npm ci --only=production

# Build de production
COPY frontend/ .
RUN npm run build

# ====================
# Stage 3: Backend Runtime
# ====================
FROM python:3.11-slim as backend

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

# Utilisateur non-root pour sécurité
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Installation des dépendances runtime uniquement
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copie des dépendances Python depuis builder
COPY --from=backend-builder /root/.local /root/.local

# Copie du code backend
COPY --chown=appuser:appuser backend/ .

# Création des répertoires nécessaires
RUN mkdir -p /app/media /app/staticfiles /app/logs && \
    chown -R appuser:appuser /app/media /app/staticfiles /app/logs

# Collecte des fichiers statiques
RUN python manage.py collectstatic --noinput --clear

USER appuser

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health/', timeout=5)" || exit 1

# Commande de démarrage
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "config.wsgi:application"]

# ====================
# Stage 4: Nginx (Reverse Proxy + Static Files)
# ====================
FROM nginx:1.25-alpine as nginx

# Copie de la configuration Nginx
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker/nginx/default.conf /etc/nginx/conf.d/default.conf

# Copie des fichiers statiques Django
COPY --from=backend /app/staticfiles /usr/share/nginx/html/static

# Copie du build Vue.js
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Certificats SSL (à remplacer par Let's Encrypt en production)
RUN mkdir -p /etc/nginx/ssl

EXPOSE 80 443

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
