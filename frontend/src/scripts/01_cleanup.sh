#!/bin/bash

# ============================================================================
# Script de nettoyage du frontend - Phase 1
# Projet : GED Cabinet Kiaba
# Auteur : Maître Ahmed
# Date : 2026-01-26
# ============================================================================

set -e  # Arrêt en cas d'erreur

# Couleurs pour le terminal
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🧹 NETTOYAGE FRONTEND - GED CABINET KIABA             ║${NC}"
echo -e "${BLUE}║   Phase 1 : Suppression fichiers obsolètes              ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Vérification qu'on est dans le bon répertoire
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Erreur : Ce script doit être exécuté depuis le dossier frontend/${NC}"
    echo -e "${YELLOW}Usage : cd frontend && bash scripts/01_cleanup.sh${NC}"
    exit 1
fi

# Fonction de backup
backup_file() {
    local file=$1
    if [ -f "$file" ]; then
        local backup_dir=".cleanup_backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        cp "$file" "$backup_dir/"
        echo -e "${GREEN}   ✓ Backup créé : $backup_dir/$(basename $file)${NC}"
    fi
}

# ============================================================================
# ÉTAPE 1 : Suppression des fichiers de démonstration Vite/Vue
# ============================================================================
echo -e "${YELLOW}📦 Étape 1/4 : Suppression des fichiers de démonstration...${NC}"

FILES_TO_DELETE=(
    "src/components/HelloWorld.vue"
    "src/assets/vue.svg"
    "public/vite.svg"
    "src/views/Dashboard.vue"
)

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        backup_file "$file"
        rm -f "$file"
        echo -e "${GREEN}   ✓ Supprimé : $file${NC}"
    else
        echo -e "${YELLOW}   ⚠ Déjà absent : $file${NC}"
    fi
done

# ============================================================================
# ÉTAPE 2 : Correction de la typo AppdCard → AppCard
# ============================================================================
echo ""
echo -e "${YELLOW}✏️  Étape 2/4 : Correction du nom AppdCard → AppCard...${NC}"

if [ -f "src/components/common/AppdCard.vue" ]; then
    backup_file "src/components/common/AppdCard.vue"
    mv src/components/common/AppdCard.vue src/components/common/AppCard.vue
    echo -e "${GREEN}   ✓ Fichier renommé : AppdCard.vue → AppCard.vue${NC}"
    
    # Recherche et alerte sur les imports à corriger
    echo -e "${YELLOW}   ⚠ Attention : Vous devez mettre à jour les imports manuellement${NC}"
    echo -e "${YELLOW}   Recherchez 'AppdCard' dans votre éditeur et remplacez par 'AppCard'${NC}"
else
    echo -e "${YELLOW}   ⚠ Fichier AppdCard.vue déjà absent ou déjà renommé${NC}"
fi

# ============================================================================
# ÉTAPE 3 : Création de la structure de dossiers manquante
# ============================================================================
echo ""
echo -e "${YELLOW}📁 Étape 3/4 : Création des dossiers manquants...${NC}"

FOLDERS_TO_CREATE=(
    "src/composables"
    "src/services"
    "src/types"
    "src/constants"
)

for folder in "${FOLDERS_TO_CREATE[@]}"; do
    if [ ! -d "$folder" ]; then
        mkdir -p "$folder"
        echo -e "${GREEN}   ✓ Créé : $folder/${NC}"
        
        # Créer un fichier .gitkeep pour que Git track les dossiers vides
        touch "$folder/.gitkeep"
    else
        echo -e "${YELLOW}   ⚠ Déjà existant : $folder/${NC}"
    fi
done

# ============================================================================
# ÉTAPE 4 : Création du fichier .env.example
# ============================================================================
echo ""
echo -e "${YELLOW}⚙️  Étape 4/4 : Création du template .env.example...${NC}"

if [ ! -f ".env.example" ]; then
    cat > .env.example << 'EOF'
# ============================================================================
# Configuration Environnement - GED Cabinet Kiaba
# ============================================================================

# Backend API
VITE_API_BASE_URL=http://127.0.0.1:8000/api/

# Application
VITE_APP_NAME="GED Cabinet Kiaba"
VITE_APP_ENV=development
VITE_APP_VERSION=1.0.0

# Features flags
VITE_ENABLE_DEBUG=true
VITE_ENABLE_MOCK_DATA=false

# Sécurité
VITE_ENABLE_CONSOLE_LOGS=true

# Upload
VITE_MAX_FILE_SIZE=52428800
VITE_ALLOWED_FILE_TYPES=pdf,doc,docx,xls,xlsx,jpg,jpeg,png

# Pagination
VITE_DEFAULT_PAGE_SIZE=25
EOF
    echo -e "${GREEN}   ✓ Créé : .env.example${NC}"
else
    echo -e "${YELLOW}   ⚠ Fichier .env.example déjà existant${NC}"
fi

# ============================================================================
# RÉCAPITULATIF
# ============================================================================
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   ✅ PHASE 1 TERMINÉE AVEC SUCCÈS                        ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📊 Récapitulatif :${NC}"
echo -e "   • Fichiers obsolètes supprimés : 4"
echo -e "   • Fichiers renommés : 1 (AppdCard → AppCard)"
echo -e "   • Dossiers créés : 4 (composables, services, types, constants)"
echo -e "   • Configuration créée : .env.example"
echo ""
echo -e "${YELLOW}📝 Actions manuelles requises :${NC}"
echo -e "   1. Rechercher et remplacer 'AppdCard' par 'AppCard' dans tous les fichiers"
echo -e "   2. Copier .env.example vers .env.local et ajuster les valeurs"
echo -e "   3. Exécuter : npm install (pour vérifier l'intégrité)"
echo ""
echo -e "${BLUE}🚀 Prochaine étape :${NC}"
echo -e "   Exécuter le script 02_refactor_utils.sh pour la Phase 2"
echo ""
