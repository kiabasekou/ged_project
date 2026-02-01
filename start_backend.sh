#!/bin/bash

# ============================================================================
# SCRIPT DE DÉMARRAGE BACKEND DJANGO - GED CABINET KIABA
# ============================================================================

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║   DÉMARRAGE BACKEND DJANGO - GED CABINET KIABA                     ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# ÉTAPE 1 : VÉRIFICATION DE L'ENVIRONNEMENT
# ============================================================================

echo -e "${BLUE}📋 ÉTAPE 1/5 : Vérification de l'environnement...${NC}"

# Vérifier si manage.py existe
if [ ! -f "/mnt/project/manage.py" ]; then
    echo -e "${RED}❌ Erreur: manage.py introuvable dans /mnt/project${NC}"
    exit 1
fi

# Vérifier si le fichier .env existe
if [ ! -f "/mnt/project/_env" ]; then
    echo -e "${RED}❌ Erreur: Fichier _env introuvable${NC}"
    echo "   Créez-le avec les variables nécessaires"
    exit 1
fi

echo -e "${GREEN}✅ Fichiers de configuration trouvés${NC}"
echo ""

# ============================================================================
# ÉTAPE 2 : INSTALLATION DES DÉPENDANCES
# ============================================================================

echo -e "${BLUE}📦 ÉTAPE 2/5 : Vérification des dépendances Python...${NC}"

cd /mnt/project

# Installer les dépendances si nécessaire
if [ -f "requirements.txt" ]; then
    echo "   Installation des dépendances..."
    pip install -q -r requirements.txt --break-system-packages 2>&1 | grep -v "Requirement already satisfied" || true
    echo -e "${GREEN}✅ Dépendances installées${NC}"
else
    echo -e "${YELLOW}⚠️  Fichier requirements.txt introuvable${NC}"
fi

echo ""

# ============================================================================
# ÉTAPE 3 : VÉRIFICATION DE LA BASE DE DONNÉES
# ============================================================================

echo -e "${BLUE}🗄️  ÉTAPE 3/5 : Vérification de la base de données...${NC}"

# Charger les variables d'environnement
export $(cat _env | grep -v '^#' | xargs)

# Vérifier si la base de données existe et est accessible
python manage.py check --deploy 2>&1 | head -5

# Appliquer les migrations si nécessaire
echo "   Application des migrations..."
python manage.py migrate --noinput 2>&1 | tail -5

echo -e "${GREEN}✅ Base de données prête${NC}"
echo ""

# ============================================================================
# ÉTAPE 4 : VÉRIFICATION DES SUPERUTILISATEURS
# ============================================================================

echo -e "${BLUE}👤 ÉTAPE 4/5 : Vérification des utilisateurs...${NC}"

# Compter le nombre de superusers
SUPERUSER_COUNT=$(python manage.py shell -c "from apps.users.models import User; print(User.objects.filter(is_superuser=True).count())")

if [ "$SUPERUSER_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Aucun superutilisateur trouvé${NC}"
    echo "   Créez-en un avec: python manage.py createsuperuser"
else
    echo -e "${GREEN}✅ $SUPERUSER_COUNT superutilisateur(s) trouvé(s)${NC}"
fi

echo ""

# ============================================================================
# ÉTAPE 5 : DÉMARRAGE DU SERVEUR
# ============================================================================

echo -e "${BLUE}🚀 ÉTAPE 5/5 : Démarrage du serveur Django...${NC}"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Serveur démarré sur: http://127.0.0.1:8000${NC}"
echo -e "${GREEN}   API disponible sur: http://127.0.0.1:8000/api/${NC}"
echo -e "${GREEN}   Admin Django: http://127.0.0.1:8000/admin/${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Appuyez sur CTRL+C pour arrêter le serveur${NC}"
echo ""

# Démarrer le serveur sur toutes les interfaces pour permettre la connexion
python manage.py runserver 0.0.0.0:8000