#!/bin/bash

# ============================================================================
# Script de refactorisation - Phase 2
# Projet : GED Cabinet Kiaba
# Auteur : Maître Ahmed
# Date : 2026-01-26
# ============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🔧 REFACTORISATION FRONTEND - PHASE 2                 ║${NC}"
echo -e "${BLUE}║   Réorganisation architecture et séparation concerns     ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Vérification prérequis
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Erreur : Ce script doit être exécuté depuis le dossier frontend/${NC}"
    exit 1
fi

if [ ! -d "src/composables" ]; then
    echo -e "${RED}❌ Erreur : Exécutez d'abord le script 01_cleanup.sh${NC}"
    exit 1
fi

# ============================================================================
# ÉTAPE 1 : Copie des nouveaux fichiers depuis le dossier de refactorisation
# ============================================================================
echo -e "${YELLOW}📦 Étape 1/5 : Installation des nouveaux fichiers...${NC}"

REFACTOR_DIR="../frontend_refactoring"

if [ ! -d "$REFACTOR_DIR" ]; then
    echo -e "${RED}❌ Erreur : Dossier de refactorisation introuvable${NC}"
    echo -e "${YELLOW}   Assurez-vous que le dossier frontend_refactoring existe${NC}"
    exit 1
fi

# Copie des composables
echo -e "${BLUE}   → Copie des composables...${NC}"
cp -v "$REFACTOR_DIR/composables/"*.js src/composables/ 2>/dev/null || true
echo -e "${GREEN}   ✓ Composables installés${NC}"

# Copie des services
echo -e "${BLUE}   → Copie des services...${NC}"
cp -v "$REFACTOR_DIR/services/"*.js src/services/ 2>/dev/null || true
echo -e "${GREEN}   ✓ Services installés${NC}"

# Remplacement de fileValidators.js
echo -e "${BLUE}   → Remplacement de fileValidators.js...${NC}"
if [ -f "src/utils/fileValidators.js" ]; then
    mv src/utils/fileValidators.js src/utils/fileValidators.js.backup
    echo -e "${YELLOW}   ⚠ Backup créé : fileValidators.js.backup${NC}"
fi
cp -v "$REFACTOR_DIR/utils/fileValidators.js" src/utils/
echo -e "${GREEN}   ✓ fileValidators.js refactorisé${NC}"

# Copie des constantes
echo -e "${BLUE}   → Installation des constantes...${NC}"
cp -v "$REFACTOR_DIR/constants/index.js" src/constants/
echo -e "${GREEN}   ✓ Constantes installées${NC}"

# ============================================================================
# ÉTAPE 2 : Mise à jour de vite.config.js
# ============================================================================
echo ""
echo -e "${YELLOW}⚙️  Étape 2/5 : Mise à jour de vite.config.js...${NC}"

if [ -f "vite.config.js" ]; then
    # Backup
    cp vite.config.js vite.config.js.backup
    
    cat > vite.config.js << 'EOF'
// frontend/vite.config.js

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    sourcemap: process.env.NODE_ENV === 'development',
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia'],
          'ui': ['vuetify']
        }
      }
    }
  }
})
EOF
    echo -e "${GREEN}   ✓ vite.config.js mis à jour${NC}"
else
    echo -e "${YELLOW}   ⚠ vite.config.js introuvable${NC}"
fi

# ============================================================================
# ÉTAPE 3 : Mise à jour de plugins/axios.js
# ============================================================================
echo ""
echo -e "${YELLOW}🔌 Étape 3/5 : Mise à jour de plugins/axios.js...${NC}"

if [ -f "src/plugins/axios.js" ]; then
    cp src/plugins/axios.js src/plugins/axios.js.backup
    
    cat > src/plugins/axios.js << 'EOF'
// frontend/src/plugins/axios.js

import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'
import { APP_CONFIG } from '@/constants'

const api = axios.create({
  baseURL: APP_CONFIG.API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Intercepteur de requête : injection du token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Intercepteur de réponse : gestion des erreurs d'authentification
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
    }
    
    return Promise.reject(error)
  }
)

export default api
EOF
    echo -e "${GREEN}   ✓ axios.js mis à jour avec variables d'environnement${NC}"
else
    echo -e "${YELLOW}   ⚠ axios.js introuvable${NC}"
fi

# ============================================================================
# ÉTAPE 4 : Création du fichier .env.local
# ============================================================================
echo ""
echo -e "${YELLOW}🔑 Étape 4/5 : Configuration des variables d'environnement...${NC}"

if [ ! -f ".env.local" ]; then
    cat > .env.local << 'EOF'
# ============================================================================
# Configuration Environnement Local - GED Cabinet Kiaba
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
VITE_MAX_FILE_SIZE=104857600
VITE_ALLOWED_FILE_TYPES=pdf,doc,docx,xls,xlsx,jpg,jpeg,png

# Pagination
VITE_DEFAULT_PAGE_SIZE=25
EOF
    echo -e "${GREEN}   ✓ Fichier .env.local créé${NC}"
    echo -e "${YELLOW}   ℹ️  Personnalisez ce fichier selon vos besoins${NC}"
else
    echo -e "${YELLOW}   ⚠ .env.local existe déjà (non modifié)${NC}"
fi

# ============================================================================
# ÉTAPE 5 : Mise à jour du .gitignore
# ============================================================================
echo ""
echo -e "${YELLOW}📝 Étape 5/5 : Mise à jour du .gitignore...${NC}"

if [ -f ".gitignore" ]; then
    # Ajouter les patterns manquants s'ils n'existent pas
    if ! grep -q ".env.local" .gitignore; then
        cat >> .gitignore << 'EOF'

# Environment variables
.env.local
.env.*.local

# Backups de refactorisation
*.backup

# IDE
.vscode/
.idea/
EOF
        echo -e "${GREEN}   ✓ .gitignore mis à jour${NC}"
    else
        echo -e "${YELLOW}   ⚠ .gitignore déjà à jour${NC}"
    fi
fi

# ============================================================================
# RÉCAPITULATIF
# ============================================================================
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   ✅ PHASE 2 TERMINÉE AVEC SUCCÈS                        ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📊 Récapitulatif :${NC}"
echo -e "   • Composables installés : useFileValidation, useDebounce"
echo -e "   • Services créés : clientService, dossierService, documentService, filePreviewService"
echo -e "   • Utils refactorisé : fileValidators.js (fonctions pures)"
echo -e "   • Constantes centralisées : constants/index.js"
echo -e "   • Configuration mise à jour : vite.config.js, axios.js"
echo -e "   • Variables d'environnement : .env.local créé"
echo ""
echo -e "${YELLOW}📝 Actions manuelles requises :${NC}"
echo -e "   1. Mettre à jour les imports dans les composants :"
echo -e "      ${BLUE}Ancien :${NC} import { validateFile } from '@/utils/fileValidators'"
echo -e "      ${GREEN}Nouveau :${NC} import { useFileValidation } from '@/composables/useFileValidation'"
echo ""
echo -e "   2. Mettre à jour les stores pour utiliser les services :"
echo -e "      ${BLUE}Ancien :${NC} await api.get('/clients/')"
echo -e "      ${GREEN}Nouveau :${NC} await clientService.fetchList()"
echo ""
echo -e "   3. Remplacer les constantes hardcodées :"
echo -e "      ${BLUE}Ancien :${NC} const statuses = ['OUVERT', 'CLOTURE']"
echo -e "      ${GREEN}Nouveau :${NC} import { DOSSIER_STATUS } from '@/constants'"
echo ""
echo -e "   4. Exécuter : ${GREEN}npm install${NC} (vérifier l'intégrité)"
echo -e "   5. Tester l'application : ${GREEN}npm run dev${NC}"
echo ""
echo -e "${BLUE}🚀 Prochaine étape :${NC}"
echo -e "   Consulter le guide de migration : MIGRATION_GUIDE.md"
echo ""
