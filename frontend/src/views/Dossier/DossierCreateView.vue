<template>
  <v-container fluid class="pa-6">
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        
        <!-- En-tête -->
        <div class="d-flex align-center mb-6">
          <v-btn
            icon="mdi-arrow-left"
            variant="text"
            @click="router.back()"
            class="mr-4"
          />
          <div>
            <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
              Nouveau Dossier
            </h1>
            <p class="text-subtitle-1 text-grey-darken-1 mt-1">
              Ouverture d'un nouveau dossier juridique ou notarial
            </p>
          </div>
        </div>

        <!-- Formulaire principal -->
        <v-card elevation="2" class="rounded-lg">
          <v-card-text class="pa-8">
            <v-form ref="dossierForm" v-model="formValid" @submit.prevent="submitForm">
              
              <!-- Référence auto-générée (preview) -->
              <v-alert
                type="info"
                variant="tonal"
                prominent
                class="mb-6"
              >
                <template v-slot:prepend>
                  <v-icon size="32">mdi-folder-key</v-icon>
                </template>
                <div class="d-flex align-center justify-space-between">
                  <div>
                    <div class="text-subtitle-1 font-weight-bold">
                      Référence du dossier
                    </div>
                    <div class="text-h6 font-weight-bold text-indigo-darken-4 mt-1">
                      {{ generatedReference }}
                    </div>
                    <div class="text-caption mt-1">
                      Générée automatiquement à la création
                    </div>
                  </div>
                </div>
              </v-alert>

              <!-- Informations principales -->
              <h3 class="text-h6 font-weight-bold mb-4 text-indigo-darken-4">
                <v-icon start>mdi-folder-information</v-icon>
                Informations du dossier
              </h3>

              <v-row>
                <!-- Titre du dossier -->
                <v-col cols="12">
                  <v-text-field
                    v-model="dossierData.title"
                    label="Intitulé du dossier *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required, rules.maxLength(300)]"
                    counter="300"
                    prepend-inner-icon="mdi-format-title"
                    placeholder="Ex: Contentieux commercial - Recouvrement créances SARL XYZ"
                    hint="Titre descriptif et explicite"
                    persistent-hint
                  />
                </v-col>

                <!-- Catégorie -->
                <v-col cols="12" md="6">
                  <v-select
                    v-model="dossierData.category"
                    :items="categories"
                    label="Catégorie juridique *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required]"
                    prepend-inner-icon="mdi-scale-balance"
                  >
                    <template v-slot:item="{ item, props }">
                      <v-list-item v-bind="props">
                        <template v-slot:prepend>
                          <v-icon :color="getCategoryColor(item.value)">
                            {{ getCategoryIcon(item.value) }}
                          </v-icon>
                        </template>
                      </v-list-item>
                    </template>
                  </v-select>
                </v-col>

                <!-- Statut initial -->
                <v-col cols="12" md="6">
                  <v-select
                    v-model="dossierData.status"
                    :items="statuses"
                    label="Statut *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required]"
                    prepend-inner-icon="mdi-flag"
                  >
                    <template v-slot:selection="{ item }">
                      <v-chip :color="getStatusColor(item.value)" size="small">
                        {{ item.title }}
                      </v-chip>
                    </template>
                  </v-select>
                </v-col>
              </v-row>

              <v-divider class="my-8" />

              <!-- Client et responsable -->
              <h3 class="text-h6 font-weight-bold mb-4 text-indigo-darken-4">
                <v-icon start>mdi-account-group</v-icon>
                Parties et responsable
              </h3>

              <v-row>
                <!-- Client -->
                <v-col cols="12" md="6">
                  <v-autocomplete
                    v-model="dossierData.client"
                    :items="clients"
                    :loading="loadingClients"
                    item-title="display_name"
                    item-value="id"
                    label="Client (Mandant) *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required]"
                    prepend-inner-icon="mdi-account-circle"
                    clearable
                    :no-data-text="clients.length === 0 ? 'Aucun client enregistré' : 'Aucun résultat'"
                  >
                    <template v-slot:item="{ item, props }">
                      <v-list-item v-bind="props">
                        <template v-slot:prepend>
                          <v-avatar 
                            :color="item.raw.client_type === 'PHYSIQUE' ? 'blue' : 'amber-darken-3'"
                            size="40"
                          >
                            <v-icon color="white">
                              {{ item.raw.client_type === 'PHYSIQUE' ? 'mdi-account' : 'mdi-domain' }}
                            </v-icon>
                          </v-avatar>
                        </template>
                        <v-list-item-title>{{ item.raw.display_name }}</v-list-item-title>
                        <v-list-item-subtitle>
                          {{ item.raw.client_type === 'PHYSIQUE' ? 'Personne Physique' : 'Personne Morale' }}
                          <span v-if="item.raw.phone_primary"> • {{ item.raw.phone_primary }}</span>
                        </v-list-item-subtitle>
                      </v-list-item>
                    </template>

                    <template v-slot:append-inner>
                      <v-btn
                        icon="mdi-plus"
                        size="x-small"
                        variant="text"
                        color="indigo"
                        @click.stop="goToClientCreate"
                        title="Créer un nouveau client"
                      />
                    </template>
                  </v-autocomplete>
                </v-col>

                <!-- Avocat responsable -->
                <v-col cols="12" md="6">
                  <v-autocomplete
                    v-model="dossierData.responsible"
                    :items="lawyers"
                    :loading="loadingUsers"
                    item-title="full_name"
                    item-value="id"
                    label="Avocat responsable *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required]"
                    prepend-inner-icon="mdi-account-tie"
                  >
                    <template v-slot:item="{ item, props }">
                      <v-list-item v-bind="props">
                        <template v-slot:prepend>
                          <v-avatar color="indigo-darken-4" size="40">
                            <span class="text-white text-subtitle-2">
                              {{ getInitials(item.raw.full_name) }}
                            </span>
                          </v-avatar>
                        </template>
                        <v-list-item-title>{{ item.raw.full_name }}</v-list-item-title>
                        <v-list-item-subtitle>{{ item.raw.role_display }}</v-list-item-subtitle>
                      </v-list-item>
                    </template>
                  </v-autocomplete>
                </v-col>
              </v-row>

              <v-divider class="my-8" />

              <!-- Juridiction et dates -->
              <h3 class="text-h6 font-weight-bold mb-4 text-indigo-darken-4">
                <v-icon start>mdi-gavel</v-icon>
                Juridiction et échéances
              </h3>

              <v-row>
                <!-- Juridiction -->
                <v-col cols="12" md="6">
                  <v-autocomplete
                    v-model="dossierData.jurisdiction"
                    :items="jurisdictions"
                    label="Juridiction compétente"
                    variant="outlined"
                    density="comfortable"
                    clearable
                    prepend-inner-icon="mdi-scale-balance"
                    hint="Tribunal ou institution compétente"
                    persistent-hint
                  />
                </v-col>

                <!-- Numéro RG (optionnel) -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="dossierData.rg_number"
                    label="Numéro RG / Dossier"
                    variant="outlined"
                    density="comfortable"
                    prepend-inner-icon="mdi-numeric"
                    placeholder="Ex: RG 123/2025"
                    hint="Numéro de rôle général (si déjà attribué)"
                    persistent-hint
                  />
                </v-col>

                <!-- Date d'ouverture -->
                <v-col cols="12" md="4">
                  <v-text-field
                    v-model="dossierData.opening_date"
                    type="date"
                    label="Date d'ouverture *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required]"
                    prepend-inner-icon="mdi-calendar-start"
                  />
                </v-col>

                <!-- Délai critique -->
                <v-col cols="12" md="4">
                  <v-text-field
                    v-model="dossierData.critical_deadline"
                    type="date"
                    label="Délai critique"
                    variant="outlined"
                    density="comfortable"
                    prepend-inner-icon="mdi-calendar-alert"
                    :hint="deadlineHint"
                    persistent-hint
                  />
                </v-col>

                <!-- Auto-calcul délai -->
                <v-col cols="12" md="4" class="d-flex align-center">
                  <v-btn
                    variant="outlined"
                    color="indigo"
                    block
                    prepend-icon="mdi-calculator"
                    @click="calculateDeadline"
                  >
                    Calculer +60 jours
                  </v-btn>
                </v-col>
              </v-row>

              <v-divider class="my-8" />

              <!-- Montant et notes -->
              <h3 class="text-h6 font-weight-bold mb-4 text-indigo-darken-4">
                <v-icon start>mdi-file-document-edit</v-icon>
                Détails complémentaires
              </h3>

              <v-row>
                <!-- Montant du litige -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model.number="dossierData.amount_claimed"
                    type="number"
                    label="Montant du litige / Opération"
                    variant="outlined"
                    density="comfortable"
                    prefix="FCFA"
                    prepend-inner-icon="mdi-currency-usd"
                    hint="Valeur financière en jeu"
                    persistent-hint
                  />
                </v-col>

                <!-- Type de procédure -->
                <v-col cols="12" md="6">
                  <v-select
                    v-model="dossierData.procedure_type"
                    :items="procedureTypes"
                    label="Type de procédure"
                    variant="outlined"
                    density="comfortable"
                    clearable
                    prepend-inner-icon="mdi-file-tree"
                  />
                </v-col>

                <!-- Notes -->
                <v-col cols="12">
                  <v-textarea
                    v-model="dossierData.notes"
                    label="Notes internes"
                    variant="outlined"
                    density="comfortable"
                    rows="4"
                    :rules="[rules.maxLength(2000)]"
                    counter="2000"
                    prepend-inner-icon="mdi-note-text"
                    placeholder="Contexte, éléments importants, instructions du client..."
                    hint="Notes confidentielles visibles uniquement par l'équipe du cabinet"
                    persistent-hint
                  />
                </v-col>
              </v-row>

              <!-- Messages d'erreur -->
              <v-expand-transition>
                <v-alert
                  v-if="error"
                  type="error"
                  variant="tonal"
                  closable
                  class="mt-6"
                  @click:close="error = null"
                >
                  {{ error }}
                </v-alert>
              </v-expand-transition>

              <!-- Actions -->
              <div class="d-flex justify-end gap-3 mt-8">
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
                  size="large"
                  variant="elevated"
                  prepend-icon="mdi-folder-plus"
                  type="submit"
                  :loading="loading"
                  :disabled="!formValid"
                >
                  Ouvrir le dossier
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- Aide contextuelle -->
        <v-card elevation="1" class="mt-6 bg-blue-grey-lighten-5">
          <v-card-text>
            <h3 class="text-subtitle-1 font-weight-bold mb-3">
              <v-icon start color="info">mdi-lightbulb</v-icon>
              Bonnes pratiques
            </h3>
            <ul class="text-caption">
              <li class="mb-2">
                <strong>Titre :</strong> Soyez précis et descriptif pour faciliter les recherches futures
              </li>
              <li class="mb-2">
                <strong>Catégorie :</strong> La classification correcte permet un suivi statistique fiable
              </li>
              <li class="mb-2">
                <strong>Délai critique :</strong> Toujours prévoir une marge de sécurité (recommandation : -7 jours)
              </li>
              <li class="mb-2">
                <strong>Notes :</strong> Consignez immédiatement les instructions du client et les éléments sensibles
              </li>
              <li>
                <strong>Référence :</strong> Le format GAB-YYYY-NNNN est automatique et séquentiel
              </li>
            </ul>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDossierStore } from '@/stores/dossier'
import { useClientStore } from '@/stores/client'
import api from '@/plugins/axios'

const router = useRouter()
const dossierStore = useDossierStore()
const clientStore = useClientStore()

// État
const dossierForm = ref(null)
const formValid = ref(false)
const loading = ref(false)
const loadingClients = ref(false)
const loadingUsers = ref(false)
const error = ref(null)

const clients = ref([])
const lawyers = ref([])

// Données du formulaire
const dossierData = ref({
  title: '',
  category: 'CONTENTIEUX',
  status: 'OUVERT',
  client: null,
  responsible: null,
  jurisdiction: null,
  rg_number: '',
  opening_date: new Date().toISOString().split('T')[0],
  critical_deadline: null,
  amount_claimed: null,
  procedure_type: null,
  notes: ''
})

// Computed
const generatedReference = computed(() => {
  const year = new Date().getFullYear()
  return `GAB-${year}-XXXX`
})

const deadlineHint = computed(() => {
  if (!dossierData.value.critical_deadline) {
    return 'Date limite pour agir ou répondre'
  }
  
  const deadline = new Date(dossierData.value.critical_deadline)
  const today = new Date()
  const diffTime = deadline - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) {
    return '⚠️ Date dépassée !'
  } else if (diffDays === 0) {
    return '⚠️ Aujourd\'hui !'
  } else if (diffDays <= 7) {
    return `⚠️ Dans ${diffDays} jour${diffDays > 1 ? 's' : ''} !`
  } else {
    return `Dans ${diffDays} jours`
  }
})

// Options
const categories = [
  { title: 'Contentieux (civil, pénal, administratif)', value: 'CONTENTIEUX' },
  { title: 'Conseil juridique / Avis', value: 'CONSEIL' },
  { title: 'Recouvrement de créances', value: 'RECOUVREMENT' },
  { title: 'Droit du travail', value: 'TRAVAIL' },
  { title: 'Actes immobiliers / Foncier', value: 'IMMOBILIER' },
  { title: 'Succession / Partage', value: 'SUCCESSION' },
  { title: 'Contrat de mariage / Régime matrimonial', value: 'MARIAGE' },
  { title: 'Donation / Libéralité', value: 'DONATION' },
  { title: 'Constitution / Modification société OHADA', value: 'SOCIETE' },
  { title: 'Divorce, garde, filiation', value: 'FAMILLE' },
  { title: 'Droit commercial OHADA', value: 'COMMERCIAL' },
  { title: 'Autre', value: 'AUTRE' }
]

const statuses = [
  { title: 'Ouvert / En cours', value: 'OUVERT' },
  { title: 'En attente', value: 'ATTENTE' },
  { title: 'Suspendu', value: 'SUSPENDU' }
]

const jurisdictions = [
  'Tribunal de Première Instance de Libreville',
  'Tribunal de Première Instance de Port-Gentil',
  'Tribunal de Première Instance de Franceville',
  'Cour d\'Appel de Libreville',
  'Cour d\'Appel de Franceville',
  'Cour de Cassation',
  'Tribunal Administratif',
  'Cour des Comptes',
  'Tribunal de Commerce',
  'Notariat',
  'Autre'
]

const procedureTypes = [
  'Procédure ordinaire',
  'Référé',
  'Procédure accélérée',
  'Arbitrage',
  'Médiation',
  'Conciliation',
  'Consultation juridique',
  'Rédaction d\'actes',
  'Autre'
]

// Règles de validation
const rules = {
  required: v => !!v || 'Ce champ est requis',
  maxLength: max => v => !v || v.length <= max || `Maximum ${max} caractères`
}

// Méthodes
const loadClients = async () => {
  loadingClients.value = true
  try {
    const response = await api.get('/clients/', {
      params: { 
        page_size: 200,
        is_active: true,
        ordering: '-created_at'
      }
    })
    clients.value = response.data.results || []
  } catch (err) {
    console.error('Erreur chargement clients:', err)
  } finally {
    loadingClients.value = false
  }
}

const loadLawyers = async () => {
  loadingUsers.value = true
  try {
    const response = await api.get('/users/', {
      params: { 
        page_size: 100,
        is_active: true,
        role__in: 'AVOCAT,NOTAIRE'
      }
    })
    lawyers.value = response.data.results || []
    
    // Pré-sélectionner l'utilisateur connecté si avocat/notaire
    const currentUser = lawyers.value.find(u => u.is_current_user)
    if (currentUser) {
      dossierData.value.responsible = currentUser.id
    }
  } catch (err) {
    console.error('Erreur chargement avocats:', err)
  } finally {
    loadingUsers.value = false
  }
}

const calculateDeadline = () => {
  if (!dossierData.value.opening_date) {
    alert('Veuillez d\'abord saisir la date d\'ouverture')
    return
  }
  
  const opening = new Date(dossierData.value.opening_date)
  const deadline = new Date(opening)
  deadline.setDate(deadline.getDate() + 60) // +60 jours
  
  dossierData.value.critical_deadline = deadline.toISOString().split('T')[0]
}

const goToClientCreate = () => {
  router.push({ name: 'ClientCreate' })
}

const getInitials = (fullName) => {
  if (!fullName) return '?'
  const parts = fullName.split(' ')
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

const getCategoryIcon = (category) => {
  const icons = {
    CONTENTIEUX: 'mdi-gavel',
    CONSEIL: 'mdi-lightbulb',
    RECOUVREMENT: 'mdi-cash',
    TRAVAIL: 'mdi-briefcase',
    IMMOBILIER: 'mdi-home',
    SUCCESSION: 'mdi-family-tree',
    MARIAGE: 'mdi-ring',
    DONATION: 'mdi-gift',
    SOCIETE: 'mdi-domain',
    FAMILLE: 'mdi-account-group',
    COMMERCIAL: 'mdi-cart',
    AUTRE: 'mdi-folder'
  }
  return icons[category] || 'mdi-folder'
}

const getCategoryColor = (category) => {
  const colors = {
    CONTENTIEUX: 'red',
    CONSEIL: 'blue',
    RECOUVREMENT: 'green',
    TRAVAIL: 'orange',
    IMMOBILIER: 'teal',
    SUCCESSION: 'purple',
    MARIAGE: 'pink',
    DONATION: 'amber',
    SOCIETE: 'indigo',
    FAMILLE: 'cyan',
    COMMERCIAL: 'lime',
    AUTRE: 'grey'
  }
  return colors[category] || 'grey'
}

const getStatusColor = (status) => {
  const colors = {
    OUVERT: 'success',
    ATTENTE: 'warning',
    SUSPENDU: 'orange'
  }
  return colors[status] || 'grey'
}

const submitForm = async () => {
  // Validation finale
  const { valid } = await dossierForm.value.validate()
  if (!valid) {
    error.value = 'Veuillez corriger les erreurs dans le formulaire'
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    // Préparer les données
    const payload = { ...dossierData.value }
    
    // Nettoyer les champs optionnels vides
    if (!payload.jurisdiction) delete payload.jurisdiction
    if (!payload.rg_number) delete payload.rg_number
    if (!payload.critical_deadline) delete payload.critical_deadline
    if (!payload.amount_claimed) delete payload.amount_claimed
    if (!payload.procedure_type) delete payload.procedure_type
    if (!payload.notes) delete payload.notes
    
    // Créer le dossier
    const newDossier = await dossierStore.createDossier(payload)
    
    // Redirection vers le dossier
    router.push({ 
      name: 'DossierDetail', 
      params: { id: newDossier.id } 
    })
    
  } catch (err) {
    console.error('Erreur création dossier:', err)
    
    // Gestion des erreurs backend
    if (err.response?.data) {
      const errors = err.response.data
      
      if (errors.client) {
        error.value = `Client invalide : ${errors.client[0]}`
      } else if (errors.responsible) {
        error.value = `Avocat responsable invalide : ${errors.responsible[0]}`
      } else if (errors.title) {
        error.value = `Titre invalide : ${errors.title[0]}`
      } else if (errors.detail) {
        error.value = errors.detail
      } else {
        error.value = 'Une erreur est survenue lors de la création. Vérifiez les données saisies.'
      }
    } else {
      error.value = 'Erreur de connexion au serveur. Veuillez réessayer.'
    }
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadClients(),
    loadLawyers()
  ])
})
</script>

<style scoped>
.gap-3 {
  gap: 12px;
}
</style>