# 🏗️ ARCHITECTURE FRONTEND - GED CABINET KIABA

**Version :** 2.0 (Post-Refactorisation)  
**Date :** 2026-01-26  
**Stack :** Vue.js 3 + Vuetify 3 + Pinia

---

## 📐 Principes Architecturaux

### 🎯 Séparation des Responsabilités (SoC)

Notre architecture suit strictement le principe de **Separation of Concerns** :

```
┌─────────────────────────────────────────────────┐
│                   COMPOSANTS                    │  ← Présentation (UI)
│  - Affichage                                    │
│  - Interactions utilisateur                     │
│  - Gestion locale des états UI                  │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│                  COMPOSABLES                    │  ← Logique Réactive
│  - Hooks Composition API                        │
│  - État réactif encapsulé                       │
│  - Logique métier côté client                   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│                    STORES                       │  ← État Global
│  - Pinia stores                                 │
│  - État partagé entre composants               │
│  - Orchestration services                       │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│                   SERVICES                      │  ← Couche Métier
│  - Appels API REST                              │
│  - Gestion erreurs centralisée                  │
│  - Transformation données                       │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│                     UTILS                       │  ← Fonctions Pures
│  - Helpers sans état                            │
│  - Validateurs                                  │
│  - Formatters                                   │
└─────────────────────────────────────────────────┘
```

---

## 📂 Structure Détaillée

### 🗂️ /src/composables (Composition API Hooks)

**Rôle :** Encapsuler la logique réactive réutilisable

```javascript
composables/
├── useFileValidation.js    # Validation fichiers avec état réactif
├── useDebounce.js           # Optimisation recherches
├── usePermissions.js        # Gestion permissions utilisateur (à créer)
└── useNotifications.js      # Système de notifications (à créer)
```

**Pattern d'utilisation :**
```javascript
// Dans un composant
import { useFileValidation } from '@/composables/useFileValidation'

const { validationState, validateSingleFile } = useFileValidation()
await validateSingleFile(file)

// Accès aux états réactifs
console.log(validationState.errors) // Array réactif
```

**Règles :**
- ✅ Retourne toujours des refs/reactive
- ✅ Peut utiliser les services
- ✅ Peut utiliser d'autres composables
- ❌ Ne doit pas dépendre d'un composant spécifique

---

### 🔧 /src/services (Business Logic Layer)

**Rôle :** Abstraire les appels API et la logique métier

```javascript
services/
├── clientService.js         # CRUD clients + validations RGPD
├── dossierService.js        # CRUD dossiers + gestion statuts
├── documentService.js       # GED + versionnage + intégrité
├── filePreviewService.js    # Génération prévisualisations
└── authService.js           # Authentification JWT (à créer)
```

**Pattern d'utilisation :**
```javascript
import clientService from '@/services/clientService'

// Appel simple
const clients = await clientService.fetchList({ page_size: 25 })

// Avec gestion d'erreur
try {
  await clientService.create(formData)
} catch (error) {
  // error.message contient un message utilisateur formaté
  showToast(error.message, 'error')
}
```

**Règles :**
- ✅ Un service = un domaine métier
- ✅ Gestion d'erreurs centralisée (méthode `_handleError`)
- ✅ Retourne des objets JavaScript (pas de `response.data` brut)
- ❌ Ne doit jamais importer de composants Vue
- ❌ Ne doit pas contenir de logique UI

---

### 🛠️ /src/utils (Pure Functions)

**Rôle :** Fonctions utilitaires sans effets de bord

```javascript
utils/
├── fileValidators.js        # Validations pures (REFACTORISÉ)
├── formatters.js            # Formatage dates, tailles, etc.
└── constants.js             # (Déprécié → utiliser /constants)
```

**Pattern d'utilisation :**
```javascript
import { validateFileSize, formatFileSize } from '@/utils/fileValidators'

// Fonctions pures (pas de side effects)
const result = validateFileSize(file)
if (!result.valid) {
  console.error(result.error)
}

const formattedSize = formatFileSize(1048576) // "1 MB"
```

**Règles :**
- ✅ Fonctions pures uniquement
- ✅ Pas d'état global
- ✅ Testables unitairement facilement
- ❌ Pas de refs/reactive
- ❌ Pas d'appels API

---

### 🎨 /src/constants (Configuration Centralisée)

**Rôle :** Source unique de vérité pour les constantes métier

```javascript
constants/
└── index.js                 # Toutes les constantes de l'app
```

**Contenu :**
- Statuts dossiers avec labels, couleurs, icônes
- Catégories juridiques
- Types de clients
- Niveaux de sensibilité documents
- Rôles utilisateurs
- Patterns de validation (NIF, RCCM)
- Configuration pagination, upload, etc.

**Pattern d'utilisation :**
```javascript
import { DOSSIER_STATUS, getOptionsFromConstant } from '@/constants'

// Accès direct
const statusInfo = DOSSIER_STATUS.OUVERT
// { value: 'OUVERT', label: 'Ouvert / En cours', color: 'green', icon: 'mdi-folder-open' }

// Pour Vuetify v-select
const options = getOptionsFromConstant(DOSSIER_STATUS)
```

**Avantages :**
- ✅ Cohérence garantie dans toute l'app
- ✅ Changement centralisé (modifier une fois, appliqué partout)
- ✅ Autocomplétion IDE complète

---

### 🗃️ /src/stores (État Global - Pinia)

**Rôle :** Orchestrer les services et gérer l'état partagé

```javascript
stores/
├── auth.js                  # Session utilisateur + JWT
├── client.js                # Liste clients + stats
├── dossier.js               # Liste dossiers + stats
├── document.js              # GED
└── notification.js          # Alertes délais critiques
```

**Pattern d'utilisation :**
```javascript
// stores/client.js (REFACTORISÉ)
import { defineStore } from 'pinia'
import clientService from '@/services/clientService'

export const useClientStore = defineStore('client', {
  state: () => ({
    list: [],
    current: null,
    stats: {}
  }),
  
  actions: {
    async fetchList(params) {
      const data = await clientService.fetchList(params)
      this.list = data.results
      return data
    }
  }
})
```

**Règles :**
- ✅ Utilise les services (pas d'appel API direct)
- ✅ Gère l'état partagé entre composants
- ✅ Peut appeler d'autres stores
- ❌ Ne contient pas de logique métier complexe

---

## 🔄 Flux de Données

### Exemple : Upload de Document

```
┌──────────────────────┐
│  DocumentUpload.vue  │  (Composant)
│  - Affichage         │
│  - Événements        │
└──────────────────────┘
          ↓
┌──────────────────────┐
│ useFileValidation()  │  (Composable)
│  - Validation        │
│  - État réactif      │
└──────────────────────┘
          ↓
┌──────────────────────┐
│  documentService     │  (Service)
│  - POST /documents/  │
│  - Gestion erreurs   │
└──────────────────────┘
          ↓
┌──────────────────────┐
│   axios (api.js)     │  (HTTP Client)
│  - Injection JWT     │
│  - Intercepteurs     │
└──────────────────────┘
          ↓
    Django Backend
```

---

## 🎨 Conventions de Nommage

### Fichiers
```
✅ CORRECT                     ❌ INCORRECT
ClientListView.vue            clientList.vue
useFileValidation.js          file-validation.js
clientService.js              ClientService.js
DOSSIER_STATUS                dossierStatus
```

### Composants
- **Pages (Views) :** `NomView.vue` (PascalCase + suffixe View)
- **Composants :** `PascalCase.vue`
- **Composables :** `useCamelCase.js` (préfixe use)
- **Services :** `camelCaseService.js` (suffixe Service)
- **Constantes :** `SCREAMING_SNAKE_CASE`

---

## 🔐 Gestion de la Sécurité

### Authentification JWT
```javascript
// plugins/axios.js
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

### Gestion Session Expirée
```javascript
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      authStore.logout()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

---

## 🧪 Testabilité

### Services (Testables Unitairement)
```javascript
// clientService.test.js
import clientService from '@/services/clientService'

test('fetchList returns formatted data', async () => {
  const data = await clientService.fetchList()
  expect(data).toHaveProperty('results')
})
```

### Utils (Testables Facilement)
```javascript
// fileValidators.test.js
import { validateFileSize } from '@/utils/fileValidators'

test('rejects files > 100 MB', () => {
  const hugeFile = { size: 200 * 1024 * 1024 }
  const result = validateFileSize(hugeFile)
  expect(result.valid).toBe(false)
})
```

---

## 📦 Build et Déploiement

### Variables d'Environnement

```env
# .env.development
VITE_API_BASE_URL=http://127.0.0.1:8000/api/
VITE_APP_ENV=development

# .env.production
VITE_API_BASE_URL=https://ged.cabinet-kiaba.ga/api/
VITE_APP_ENV=production
```

### Optimisations Build

```javascript
// vite.config.js
export default defineConfig({
  build: {
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
```

---

## 📚 Ressources et Documentation

### Liens Utiles
- [Vue.js 3 Documentation](https://vuejs.org/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vuetify 3 Documentation](https://vuetifyjs.com/)

### Documentation Interne
- `/docs/MIGRATION_GUIDE.md` - Guide de migration Phase 2
- `/scripts/01_cleanup.sh` - Script de nettoyage
- `/scripts/02_refactor.sh` - Script de refactorisation

---

## ✅ Checklist Qualité

Votre code respecte l'architecture si :

- [ ] Les composants n'appellent jamais `axios` directement
- [ ] Les services gèrent toutes les erreurs API
- [ ] Les constantes ne sont jamais hardcodées
- [ ] Les composables retournent des refs/reactive
- [ ] Les utils sont des fonctions pures
- [ ] Les variables d'environnement sont dans `.env`
- [ ] Aucun import de composant Vue dans services/utils
- [ ] Les noms de fichiers suivent les conventions

---

**🎉 Architecture Validée - Niveau Production**

Maître Ahmed, cette architecture garantit :
- ✅ Maintenabilité sur le long terme
- ✅ Scalabilité (ajout de features facile)
- ✅ Testabilité complète
- ✅ Onboarding simplifié nouveaux développeurs
