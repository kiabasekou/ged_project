# 📘 GUIDE DE MIGRATION - PHASE 2

**Projet :** GED Cabinet Kiaba  
**Date :** 2026-01-26  
**Auteur :** Maître Ahmed

---

## 🎯 Objectif de la Refactorisation

Cette phase restructure le frontend selon les meilleures pratiques Vue.js 3 :
- ✅ Séparation claire des responsabilités (Composables / Services / Utils)
- ✅ Constantes centralisées pour maintenabilité
- ✅ Services métier réutilisables
- ✅ Configuration externalisée (.env)

---

## 📂 Nouvelle Architecture

```
frontend/src/
├── composables/           # 🆕 Hooks Composition API réactifs
│   ├── useFileValidation.js
│   └── useDebounce.js
│
├── services/              # 🆕 Logique métier et appels API
│   ├── clientService.js
│   ├── dossierService.js
│   ├── documentService.js
│   └── filePreviewService.js
│
├── utils/                 # ♻️ Fonctions pures uniquement
│   └── fileValidators.js  (refactorisé)
│
├── constants/             # 🆕 Constantes centralisées
│   └── index.js
│
├── stores/                # Pinia stores (inchangé)
├── components/            # Composants Vue (inchangé)
├── views/                 # Pages (inchangé)
└── plugins/               # ♻️ Axios mis à jour
    └── axios.js
```

---

## 🔄 Patterns de Migration

### 1️⃣ **Migration : Validation de Fichiers**

#### ❌ Ancien Pattern (utils surchargé)

```javascript
// Composant Vue
import { validateFile, generateImagePreview } from '@/utils/fileValidators'

const selectedFile = ref(null)
const errors = ref([])
const preview = ref(null)

const handleFile = async (file) => {
  const result = validateFile(file)
  if (!result.valid) {
    errors.value.push(result.error)
  } else {
    preview.value = await generateImagePreview(file)
  }
}
```

#### ✅ Nouveau Pattern (séparation concerns)

```javascript
// Composant Vue
import { useFileValidation } from '@/composables/useFileValidation'

const { 
  validationState, 
  fileMetadata, 
  imagePreview,
  validateSingleFile,
  clearValidation 
} = useFileValidation()

const handleFile = async (file) => {
  await validateSingleFile(file)
  // validationState.errors contient les erreurs
  // imagePreview.value contient la prévisualisation (si image)
}
```

**Avantages :**
- ✅ État réactif automatique
- ✅ Prévisualisation intégrée
- ✅ Pas de gestion manuelle des erreurs

---

### 2️⃣ **Migration : Appels API**

#### ❌ Ancien Pattern (appel direct dans store)

```javascript
// stores/client.js
import api from '@/plugins/axios'

export const useClientStore = defineStore('client', {
  actions: {
    async fetchList(params) {
      try {
        const response = await api.get('/clients/', { params })
        this.list = response.data.results
      } catch (error) {
        console.error(error)
        // Gestion d'erreur manuelle répétitive
      }
    }
  }
})
```

#### ✅ Nouveau Pattern (service layer)

```javascript
// stores/client.js
import clientService from '@/services/clientService'

export const useClientStore = defineStore('client', {
  actions: {
    async fetchList(params) {
      try {
        const data = await clientService.fetchList(params)
        this.list = data.results
      } catch (error) {
        // Erreur déjà formatée par le service
        this.error = error.message
      }
    }
  }
})
```

**Avantages :**
- ✅ Gestion d'erreurs centralisée
- ✅ Messages d'erreur cohérents
- ✅ Service réutilisable (hors store)
- ✅ Testable unitairement

---

### 3️⃣ **Migration : Constantes Hardcodées**

#### ❌ Ancien Pattern (constantes dispersées)

```javascript
// Composant A
const statuses = ['OUVERT', 'CLOTURE', 'ARCHIVE']

// Composant B  
const status_labels = {
  'OUVERT': 'Ouvert',
  'CLOTURE': 'Clôturé'
}

// ❌ Incohérent, non maintenable
```

#### ✅ Nouveau Pattern (constantes centralisées)

```javascript
// Partout dans l'application
import { DOSSIER_STATUS, getOptionsFromConstant } from '@/constants'

// Accès à une constante
const statusInfo = DOSSIER_STATUS.OUVERT
// { value: 'OUVERT', label: 'Ouvert / En cours', color: 'green', icon: 'mdi-folder-open' }

// Pour v-select
const statusOptions = getOptionsFromConstant(DOSSIER_STATUS)
```

**Template Vuetify :**
```vue
<v-select
  v-model="form.status"
  :items="getOptionsFromConstant(DOSSIER_STATUS)"
  item-title="title"
  item-value="value"
/>

<v-chip :color="DOSSIER_STATUS[dossier.status].color">
  <v-icon start>{{ DOSSIER_STATUS[dossier.status].icon }}</v-icon>
  {{ DOSSIER_STATUS[dossier.status].label }}
</v-chip>
```

---

### 4️⃣ **Migration : Debouncing de Recherche**

#### ❌ Ancien Pattern (gestion manuelle)

```javascript
let debounceTimer = null

watch(searchQuery, (newVal) => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    performSearch(newVal)
  }, 400)
})
```

#### ✅ Nouveau Pattern (composable)

```javascript
import { useDebounce } from '@/composables/useDebounce'

const searchQuery = ref('')
const debouncedQuery = useDebounce(searchQuery, 400)

watch(debouncedQuery, (newVal) => {
  performSearch(newVal)
})
```

**Ou pour recherche avec loading :**

```javascript
import { useDebouncedSearch } from '@/composables/useDebounce'

const { execute, isLoading } = useDebouncedSearch(
  async (query) => {
    const results = await clientService.quickSearch(query)
    return results
  },
  400
)

// Usage
const handleInput = (value) => {
  execute(value)
}
```

---

### 5️⃣ **Migration : Variables d'Environnement**

#### ❌ Ancien Pattern (URLs hardcodées)

```javascript
// plugins/axios.js
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/', // ❌ Hardcodé
})
```

#### ✅ Nouveau Pattern (configuration externalisée)

```javascript
// plugins/axios.js
import { APP_CONFIG } from '@/constants'

const api = axios.create({
  baseURL: APP_CONFIG.API_BASE_URL, // ✅ Depuis .env
})
```

**Fichier .env.local :**
```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/
```

**Fichier .env.production :**
```env
VITE_API_BASE_URL=https://ged.cabinet-kiaba.ga/api/
```

---

## 🛠️ Checklist de Migration Composant par Composant

### 📄 DocumentUpload.vue

**Imports à changer :**
```javascript
// ❌ Ancien
import { validateFile, formatFileSize, generateImagePreview } from '@/utils/fileValidators'

// ✅ Nouveau
import { useFileValidation } from '@/composables/useFileValidation'
import { formatFileSize } from '@/utils/fileValidators'
import documentService from '@/services/documentService'
import { DOCUMENT_SENSITIVITY } from '@/constants'
```

**Logique à adapter :**
```javascript
// ❌ Ancien
const selectedFile = ref(null)
const errors = ref([])
const validateFile = (file) => { /* ... */ }

// ✅ Nouveau
const { validationState, validateSingleFile, imagePreview } = useFileValidation()

// Upload
const handleUpload = async () => {
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  // ...
  
  await documentService.upload(formData, (progress) => {
    uploadProgress.value = progress
  })
}
```

---

### 📄 ClientListView.vue

**Store à simplifier :**
```javascript
// ❌ Ancien
const fetchClients = async () => {
  try {
    const response = await api.get('/clients/', { params })
    clients.value = response.data.results
  } catch (error) {
    console.error(error)
  }
}

// ✅ Nouveau
import { useClientStore } from '@/stores/client'
const clientStore = useClientStore()

onMounted(async () => {
  await clientStore.fetchList({ page_size: 25 })
  clients.value = clientStore.list
})
```

**Constantes à utiliser :**
```javascript
import { CLIENT_TYPES } from '@/constants'

// Dans le template
<v-select
  v-model="filters.client_type"
  :items="getOptionsFromConstant(CLIENT_TYPES)"
/>
```

---

### 📄 DossierDetailView.vue

**Services à intégrer :**
```javascript
import dossierService from '@/services/dossierService'
import documentService from '@/services/documentService'

// Charger dossier + documents
onMounted(async () => {
  const [dossierData, documents] = await Promise.all([
    dossierService.fetchDetail(route.params.id),
    documentService.fetchByDossier(route.params.id)
  ])
  
  dossier.value = dossierData
  documentList.value = documents
})
```

---

## 🧪 Stratégie de Test

### Phase 1 : Tests Manuels
1. ✅ Login/Logout
2. ✅ Création client (PHYSIQUE + MORALE)
3. ✅ Création dossier
4. ✅ Upload document (avec validation)
5. ✅ Recherche (debounce fonctionnel)
6. ✅ Navigation entre pages

### Phase 2 : Tests de Non-Régression
- Comparer avec version backup
- Vérifier les appels API (Network DevTools)
- Valider les messages d'erreur

---

## 📋 Plan de Rollout

### Semaine 1 : Migration Services
- [ ] Mise à jour stores/client.js
- [ ] Mise à jour stores/dossier.js
- [ ] Mise à jour stores/document.js

### Semaine 2 : Migration Composants
- [ ] DocumentUpload.vue
- [ ] ClientListView.vue + ClientDetailView.vue
- [ ] DossierListView.vue + DossierDetailView.vue

### Semaine 3 : Migration Utilitaires
- [ ] Remplacer constantes hardcodées
- [ ] Intégrer useDebounce dans recherches
- [ ] Tests de non-régression complets

---

## 🚨 Points d'Attention

### ⚠️ Breaking Changes
- `validateFile()` retourne maintenant `{ valid, error, warnings }` au lieu de booléen
- Les services lancent des `Error` avec messages formatés (pas de `response.data` brut)
- Constantes nécessitent import explicite

### 🔧 Configuration Requise
```bash
# Créer .env.local depuis .env.example
cp .env.example .env.local

# Installer les dépendances (aucune nouvelle lib)
npm install

# Lancer en mode dev
npm run dev
```

---

## 📞 Support

En cas de problème :
1. Consulter les backups : `*.backup`
2. Vérifier les imports dans DevTools Console
3. Comparer avec patterns de ce guide

---

## ✅ Checklist Finale

Avant de considérer la migration terminée :

- [ ] Aucun import depuis l'ancien `fileValidators.js` (sauf utils pures)
- [ ] Tous les appels API passent par les services
- [ ] Constantes importées depuis `@/constants`
- [ ] Variables d'environnement dans `.env.local`
- [ ] Tests manuels complets réussis
- [ ] Pas d'erreurs console en mode dev
- [ ] Build de production fonctionnel (`npm run build`)

---

**🎉 Félicitations, Maître Ahmed !**  
Votre frontend suit maintenant les standards Vue.js 3 du Top 1%.
