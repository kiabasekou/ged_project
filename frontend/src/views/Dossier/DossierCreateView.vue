<!-- ============================================================================
CORRECTION : frontend/src/views/Dossier/DossierCreateView.vue
PROBLÈME : Bug lors de la création de dossier
SOLUTION : Vérifier les champs requis et le format des données
============================================================================ -->

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDossierStore } from '@/stores/dossier'
import { useClientStore } from '@/stores/client'
import { useAuthStore } from '@/stores/auth'
import api from '@/plugins/axios'

const router = useRouter()
const dossierStore = useDossierStore()
const clientStore = useClientStore()
const authStore = useAuthStore()

// État
const dossierForm = ref(null)
const loading = ref(false)
const error = ref(null)
const loadingClients = ref(false)
const loadingLawyers = ref(false)

const clients = ref([])
const lawyers = ref([])

// Formulaire
const form = reactive({
  title: '',
  client: null,
  responsible: null,
  category: 'CONTENTIEUX',
  status: 'OUVERT',
  opening_date: new Date().toISOString().split('T')[0],
  critical_deadline: null,
  jurisdiction: '',
  description: ''
})

// Catégories juridiques (droit gabonais)
const categories = [
  { value: 'CONTENTIEUX', title: 'Contentieux (civil, pénal, administratif)' },
  { value: 'CONSEIL', title: 'Conseil juridique / Avis' },
  { value: 'RECOUVREMENT', title: 'Recouvrement de créances' },
  { value: 'TRAVAIL', title: 'Droit du travail' },
  { value: 'IMMOBILIER', title: 'Actes immobiliers / Foncier' },
  { value: 'SUCCESSION', title: 'Succession / Partage' },
  { value: 'MARIAGE', title: 'Contrat de mariage / Régime matrimonial' },
  { value: 'DONATION', title: 'Donation / Libéralité' },
  { value: 'SOCIETE', title: 'Constitution / Modification société OHADA' },
  { value: 'FAMILLE', title: 'Divorce, garde, filiation' },
  { value: 'COMMERCIAL', title: 'Droit commercial OHADA' },
  { value: 'AUTRE', title: 'Autre' }
]

// Statuts
const statuses = [
  { title: 'Ouvert / En cours', value: 'OUVERT' },
  { title: 'En attente de pièces ou décision', value: 'ATTENTE' },
  { title: 'Suspendu', value: 'SUSPENDU' },
  { title: 'Clôturé', value: 'CLOTURE' }
]

// Règles de validation
const rules = {
  required: v => !!v || 'Ce champ est requis',
  maxLength: max => v => !v || v.length <= max || `Maximum ${max} caractères`,
  futureDate: v => {
    if (!v) return true
    const selected = new Date(v)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    return selected >= today || 'La date limite doit être dans le futur'
  }
}

// Méthodes
const loadClients = async () => {
  loadingClients.value = true
  try {
    await clientStore.fetchList({ 
      is_active: true,
      page_size: 500,
      ordering: 'last_name,company_name'
    })
    
    clients.value = clientStore.list.map(c => ({
      value: c.id,
      title: c.client_type === 'PHYSIQUE' 
        ? `${c.last_name} ${c.first_name}` 
        : c.company_name,
      subtitle: c.client_type === 'PHYSIQUE' ? 'Personne physique' : 'Personne morale'
    }))
  } catch (err) {
    console.error('Erreur chargement clients:', err)
    error.value = 'Impossible de charger la liste des clients'
  } finally {
    loadingClients.value = false
  }
}

const loadLawyers = async () => {
  loadingLawyers.value = true
  try {
    const response = await api.get('/users/', {
      params: {
        role__in: 'AVOCAT,NOTAIRE,CONSEIL_JURIDIQUE',
        is_active: true,
        page_size: 100,
        ordering: 'last_name'
      }
    })
    
    lawyers.value = (response.data.results || response.data || []).map(u => ({
      value: u.id,
      title: u.full_name || `${u.last_name} ${u.first_name}`,
      subtitle: u.role_display || u.role
    }))
    
    // Pré-sélectionner l'utilisateur connecté s'il est avocat
    if (authStore.user && ['AVOCAT', 'NOTAIRE', 'CONSEIL_JURIDIQUE'].includes(authStore.user.role)) {
      form.responsible = authStore.user.id
    }
  } catch (err) {
    console.error('Erreur chargement avocats:', err)
    error.value = 'Impossible de charger la liste des avocats'
  } finally {
    loadingLawyers.value = false
  }
}

const handleSubmit = async () => {
  const { valid } = await dossierForm.value.validate()
  if (!valid) return

  loading.value = true
  error.value = null

  try {
    // Construction du payload avec TOUS les champs requis
    const payload = {
      title: form.title.trim(),
      client: form.client,
      responsible: form.responsible,
      category: form.category,
      status: form.status,
      opening_date: form.opening_date
    }
    
    // Champs optionnels
    if (form.critical_deadline) {
      payload.critical_deadline = form.critical_deadline
    }
    
    if (form.jurisdiction && form.jurisdiction.trim()) {
      payload.jurisdiction = form.jurisdiction.trim()
    }
    
    if (form.description && form.description.trim()) {
      payload.description = form.description.trim()
    }
    
    // Debug: afficher le payload
    console.log('Payload création dossier:', payload)
    
    // Appel API via le store
    const newDossier = await dossierStore.createDossier(payload)
    
    // Succès: redirection vers le détail du dossier
    router.push({ 
      name: 'DossierDetail', 
      params: { id: newDossier.id } 
    })
    
  } catch (err) {
    console.error('Erreur création dossier:', err)
    
    // Gestion des erreurs backend
    if (err.response?.data) {
      const errors = err.response.data
      
      // Afficher les erreurs de validation de manière lisible
      if (typeof errors === 'object' && !errors.detail) {
        error.value = Object.entries(errors)
          .map(([field, messages]) => {
            const fieldLabel = {
              'title': 'Titre',
              'client': 'Client',
              'responsible': 'Avocat responsable',
              'category': 'Catégorie',
              'opening_date': 'Date d\'ouverture',
              'critical_deadline': 'Date limite critique',
              'jurisdiction': 'Juridiction'
            }[field] || field
            
            const errorMessages = Array.isArray(messages) ? messages : [messages]
            return `${fieldLabel}: ${errorMessages.join(', ')}`
          })
          .join('\n')
      } else {
        error.value = errors.detail || 'Erreur lors de la création du dossier'
      }
    } else if (err.request) {
      error.value = 'Impossible de contacter le serveur. Vérifiez votre connexion.'
    } else {
      error.value = 'Erreur lors de la préparation de la requête. Vérifiez les données saisies.'
    }
  } finally {
    loading.value = false
  }
}

// Chargement initial
onMounted(async () => {
  await Promise.all([
    loadClients(),
    loadLawyers()
  ])
})
</script>

<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col cols="12" lg="10" xl="8" class="mx-auto">
        <!-- Header -->
        <div class="d-flex align-center mb-6">
          <v-btn
            icon="mdi-arrow-left"
            variant="text"
            @click="router.back()"
          />
          <div class="ml-4">
            <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
              Nouveau Dossier
            </h1>
            <p class="text-body-2 text-grey-darken-1 mt-1">
              Créer un nouveau dossier juridique
            </p>
          </div>
        </div>

        <!-- Formulaire -->
        <v-card elevation="2">
          <v-card-text class="pa-6">
            <v-form ref="dossierForm" @submit.prevent="handleSubmit">
              <!-- Informations principales -->
              <div class="text-h6 font-weight-bold text-indigo-darken-4 mb-4">
                <v-icon start>mdi-information</v-icon>
                Informations principales
              </div>

              <v-text-field
                v-model="form.title"
                label="Titre du dossier *"
                variant="outlined"
                prepend-inner-icon="mdi-text"
                :rules="[rules.required, rules.maxLength(200)]"
                counter="200"
                hint="Ex: Contentieux commercial SARL Alpha vs SARL Beta"
                persistent-hint
                class="mb-4"
              />

              <v-autocomplete
                v-model="form.client"
                :items="clients"
                item-title="title"
                item-value="value"
                label="Client *"
                variant="outlined"
                prepend-inner-icon="mdi-account"
                :loading="loadingClients"
                :rules="[rules.required]"
                no-data-text="Aucun client trouvé"
                class="mb-4"
              >
                <template #item="{ props: itemProps, item }">
                  <v-list-item v-bind="itemProps">
                    <v-list-item-subtitle>{{ item.raw.subtitle }}</v-list-item-subtitle>
                  </v-list-item>
                </template>
              </v-autocomplete>

              <v-autocomplete
                v-model="form.responsible"
                :items="lawyers"
                item-title="title"
                item-value="value"
                label="Avocat responsable *"
                variant="outlined"
                prepend-inner-icon="mdi-scale-balance"
                :loading="loadingLawyers"
                :rules="[rules.required]"
                no-data-text="Aucun avocat trouvé"
                class="mb-4"
              >
                <template #item="{ props: itemProps, item }">
                  <v-list-item v-bind="itemProps">
                    <v-list-item-subtitle>{{ item.raw.subtitle }}</v-list-item-subtitle>
                  </v-list-item>
                </template>
              </v-autocomplete>

              <!-- Classification -->
              <v-divider class="my-6" />
              
              <div class="text-h6 font-weight-bold text-indigo-darken-4 mb-4">
                <v-icon start>mdi-tag</v-icon>
                Classification
              </div>

              <v-row>
                <v-col cols="12" md="6">
                  <v-select
                    v-model="form.category"
                    :items="categories"
                    item-title="title"
                    item-value="value"
                    label="Catégorie *"
                    variant="outlined"
                    prepend-inner-icon="mdi-shape"
                    :rules="[rules.required]"
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-select
                    v-model="form.status"
                    :items="statuses"
                    item-title="title"
                    item-value="value"
                    label="Statut *"
                    variant="outlined"
                    prepend-inner-icon="mdi-state-machine"
                    :rules="[rules.required]"
                  />
                </v-col>
              </v-row>

              <!-- Dates -->
              <v-divider class="my-6" />
              
              <div class="text-h6 font-weight-bold text-indigo-darken-4 mb-4">
                <v-icon start>mdi-calendar</v-icon>
                Dates importantes
              </div>

              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.opening_date"
                    type="date"
                    label="Date d'ouverture *"
                    variant="outlined"
                    prepend-inner-icon="mdi-calendar-start"
                    :rules="[rules.required]"
                    hint="Date d'ouverture du dossier"
                    persistent-hint
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.critical_deadline"
                    type="date"
                    label="Date limite critique (optionnel)"
                    variant="outlined"
                    prepend-inner-icon="mdi-alert-circle"
                    :rules="[rules.futureDate]"
                    hint="Date d'échéance critique (audience, prescription...)"
                    persistent-hint
                    clearable
                  />
                </v-col>
              </v-row>

              <!-- Détails supplémentaires -->
              <v-divider class="my-6" />
              
              <div class="text-h6 font-weight-bold text-indigo-darken-4 mb-4">
                <v-icon start>mdi-file-document</v-icon>
                Détails supplémentaires
              </div>

              <v-text-field
                v-model="form.jurisdiction"
                label="Juridiction / Tribunal (optionnel)"
                variant="outlined"
                prepend-inner-icon="mdi-gavel"
                :rules="[rules.maxLength(200)]"
                hint="Ex: Tribunal de Commerce de Libreville"
                persistent-hint
                class="mb-4"
              />

              <v-textarea
                v-model="form.description"
                label="Description / Notes (optionnel)"
                variant="outlined"
                prepend-inner-icon="mdi-text"
                rows="4"
                :rules="[rules.maxLength(2000)]"
                counter="2000"
                hint="Notes internes, contexte, historique..."
                persistent-hint
              />

              <!-- Message d'erreur -->
              <v-alert
                v-if="error"
                type="error"
                variant="tonal"
                class="mt-6"
                closable
                @click:close="error = null"
              >
                <div class="font-weight-bold mb-2">Erreur lors de la création</div>
                <pre style="white-space: pre-wrap; font-family: inherit;">{{ error }}</pre>
              </v-alert>
            </v-form>
          </v-card-text>

          <!-- Actions -->
          <v-card-actions class="pa-6 pt-0">
            <v-spacer />
            <v-btn
              variant="text"
              size="large"
              @click="router.back()"
              :disabled="loading"
            >
              Annuler
            </v-btn>
            <v-btn
              color="indigo-darken-4"
              variant="flat"
              size="large"
              prepend-icon="mdi-check"
              @click="handleSubmit"
              :loading="loading"
            >
              Créer le dossier
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.gap-3 {
  gap: 12px;
}
</style>