<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useClientStore } from '@/stores/client'
import api from '@/plugins/axios'

const route = useRoute()
const router = useRouter()
const clientStore = useClientStore()

// === ÉTATS PRINCIPAUX ===
const client = ref<Client | null>(null)
const dossiers = ref<Dossier[]>([])
const loading = ref(true)
const actionLoading = ref(false)
const error = ref<string | null>(null)
const showEditDialog = ref(false)
const editLoading = ref(false)
const editForm = ref(null)
const editData = ref<Record<string, any>>({})

// === COMPUTED ===
const clientId = computed(() => route.params.id as string)

const clientDisplayName = computed(() => {
  if (!client.value) return 'Client'
  return client.value.display_name || `${client.value.last_name} ${client.value.first_name}`.trim()
})

const isPersonnePhysique = computed(() => client.value?.client_type === 'PHYSIQUE')

// === ACTIONS ===
const loadClientDetail = async () => {
  if (!clientId.value || clientId.value === 'create') {
    loading.value = false
    return
  }

  loading.value = true
  error.value = null

  try {
    await clientStore.fetchDetail(clientId.value)
    client.value = clientStore.current

    if (!client.value) {
      throw new Error('Client non trouvé')
    }

    // Chargement parallèle des dossiers associés
    const [dossiersRes] = await Promise.all([
      api.get('/dossiers/', { params: { client: clientId.value } }),
      // Possibilité d'ajouter d'autres appels parallèles ici
    ])

    dossiers.value = dossiersRes.data.results || dossiersRes.data
  } catch (err: any) {
    console.error('Erreur chargement détail client', err)
    error.value = err.response?.status === 404
      ? 'Ce client n’existe pas ou a été archivé.'
      : 'Impossible de charger les informations du client.'
  } finally {
    loading.value = false
  }
}

const grantConsent = async () => {
  if (!client.value?.id || client.value.consent_given) return

  actionLoading.value = true
  try {
    await clientStore.grantConsent(client.value.id)
    client.value.consent_given = true
  } catch (err) {
    console.error('Échec de la régularisation du consentement', err)
    error.value = 'Échec de la mise à jour du consentement.'
  } finally {
    actionLoading.value = false
  }
}

// === MODIFICATION CLIENT ===
const openEditDialog = () => {
  if (!client.value) return
  const c = client.value
  editData.value = {
    first_name: c.first_name || '',
    last_name: c.last_name || '',
    company_name: c.company_name || '',
    rccm: c.rccm || '',
    nif: c.nif || '',
    email: c.email || '',
    phone_primary: c.phone_primary || '',
    phone_secondary: c.phone_secondary || '',
    address_line: c.address_line || '',
    city: c.city || '',
    neighborhood: c.neighborhood || ''
  }
  showEditDialog.value = true
}

const saveClient = async () => {
  if (!client.value?.id) return
  editLoading.value = true
  try {
    const response = await api.patch(`/clients/${client.value.id}/`, editData.value)
    client.value = response.data
    clientStore.current = response.data
    showEditDialog.value = false
  } catch (err: any) {
    console.error('Erreur modification client:', err)
    const data = err.response?.data
    if (data && typeof data === 'object') {
      const msg = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join('\n')
      alert(msg)
    } else {
      alert('Erreur lors de la modification')
    }
  } finally {
    editLoading.value = false
  }
}

// === CYCLE DE VIE ===
onMounted(() => {
  loadClientDetail()
})
</script>

<template>
  <!-- CHARGEMENT -->
  <div v-if="loading" class="pa-8">
    <v-row>
      <v-col cols="12" md="6">
        <v-skeleton-loader type="card-heading, list-item-two-line@3" class="mb-6" />
        <v-skeleton-loader type="card" height="300" />
      </v-col>
      <v-col cols="12" md="6">
        <v-skeleton-loader type="card-heading" class="mb-6" />
        <v-skeleton-loader type="list-item-two-line@4" height="300" />
      </v-col>
    </v-row>
  </div>

  <!-- ERREUR GLOBALE -->
  <v-alert
    v-else-if="error"
    type="error"
    variant="tonal"
    prominent
    class="ma-8"
    title="Client introuvable"
  >
    {{ error }}
    <template #append>
      <v-btn color="error" variant="text" @click="router.push('/clients')">
        Retour à la liste des clients
      </v-btn>
    </template>
  </v-alert>

  <!-- CONTENU PRINCIPAL -->
  <div v-else-if="client">
    <!-- En-tête -->
    <div class="d-flex align-center justify-space-between flex-wrap gap-4 mb-8">
      <div class="d-flex align-center gap-4">
        <v-avatar size="80" color="indigo-darken-4">
          <v-icon size="48" color="white">
            {{ isPersonnePhysique ? 'mdi-account' : 'mdi-domain' }}
          </v-icon>
        </v-avatar>
        <div>
          <h1 class="text-h4 font-weight-black text-indigo-darken-4">
            {{ clientDisplayName }}
          </h1>
          <v-chip
            :color="isPersonnePhysique ? 'blue-darken-1' : 'amber-darken-3'"
            class="mt-2 font-weight-medium"
            label
          >
            <v-icon start>
              {{ isPersonnePhysique ? 'mdi-account' : 'mdi-domain' }}
            </v-icon>
            {{ isPersonnePhysique ? 'Personne physique' : 'Personne morale' }}
          </v-chip>
        </div>
      </div>

      <div class="d-flex gap-3">
        <v-btn
          color="indigo-darken-4"
          variant="flat"
          prepend-icon="mdi-pencil"
          size="large"
          @click="openEditDialog"
        >
          Modifier
        </v-btn>
        <v-btn
          color="indigo-darken-4"
          variant="outlined"
          prepend-icon="mdi-arrow-left"
          size="large"
          @click="router.push('/clients')"
        >
          Retour
        </v-btn>
      </div>
    </div>

    <v-row>
      <!-- Fiche d'identité -->
      <v-col cols="12" md="6">
        <v-card elevation="6" rounded="lg">
          <v-card-title class="bg-indigo-darken-4 text-white py-4">
            <v-icon start color="white">mdi-card-account-details</v-icon>
            <span class="text-h6 font-weight-bold">Fiche d’identité</span>
          </v-card-title>

          <v-card-text class="pt-8 pb-6">
            <div class="space-y-6">
              <!-- Coordonnées -->
              <div>
                <p class="text-overline text-grey-darken-2 mb-2">Coordonnées</p>
                <div class="text-body-1 space-y-2">
                  <p v-if="client.email">
                    <v-icon size="small" class="mr-2 text-grey-darken-1">mdi-email</v-icon>
                    {{ client.email }}
                  </p>
                  <p v-else class="text-grey">Aucun email renseigné</p>

                  <p v-if="client.phone_primary">
                    <v-icon size="small" class="mr-2 text-grey-darken-1">mdi-phone</v-icon>
                    {{ client.phone_primary }}
                  </p>
                  <p v-else class="text-grey">Aucun téléphone renseigné</p>
                </div>
              </div>

              <v-divider />

              <!-- Identification légale -->
              <div>
                <p class="text-overline text-grey-darken-2 mb-2">Identification légale</p>
                <div class="text-body-1 space-y-1">
                  <p v-if="client.nif"><strong>NIF :</strong> {{ client.nif }}</p>
                  <p v-if="client.rccm"><strong>RCCM :</strong> {{ client.rccm }}</p>
                  <p>
                    <strong>Adresse :</strong>
                    {{ client.full_address || 'Libreville, Estuaire, Gabon' }}
                  </p>
                </div>
              </div>

              <v-divider />

              <!-- Consentement RGPD -->
              <div class="d-flex align-center justify-space-between flex-wrap gap-4">
                <div>
                  <p class="text-overline text-grey-darken-2 mb-2">Consentement RGPD</p>
                  <v-chip
                    :color="client.consent_given ? 'success' : 'warning'"
                    :prepend-icon="client.consent_given ? 'mdi-check-circle' : 'mdi-alert'"
                    class="font-weight-bold"
                  >
                    {{ client.consent_given ? 'Accordé' : 'Manquant' }}
                  </v-chip>
                </div>

                <v-btn
                  v-if="!client.consent_given"
                  color="warning"
                  size="small"
                  :loading="actionLoading"
                  :disabled="actionLoading"
                  @click="grantConsent"
                >
                  Régulariser
                </v-btn>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Dossiers associés -->
      <v-col cols="12" md="6">
        <v-card elevation="6" rounded="lg" class="fill-height d-flex flex-column">
          <v-card-title class="bg-grey-lighten-4 py-4">
            <v-icon start color="indigo-darken-4">mdi-folder-text</v-icon>
            <span class="text-h6 font-weight-bold">
              Procédures liées ({{ dossiers.length }})
            </span>
          </v-card-title>

          <div v-if="dossiers.length > 0" class="flex-grow-1">
            <v-list lines="two" class="py-0">
              <v-list-item
                v-for="dossier in dossiers"
                :key="dossier.id"
                :to="`/dossiers/${dossier.id}`"
                link
                class="border-b"
                active-class="bg-indigo-lighten-5"
              >
                <template #prepend>
                  <v-icon color="indigo" class="mr-3">mdi-folder-text</v-icon>
                </template>

                <v-list-item-title class="font-weight-bold text-indigo-darken-3">
                  {{ dossier.reference_code }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ dossier.title }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </div>

          <div v-else class="d-flex flex-column align-center justify-center fill-height pa-8 text-center">
            <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-folder-open-outline</v-icon>
            <p class="text-h6 text-grey-darken-1 font-weight-medium">Aucun dossier</p>
            <p class="text-body-2 text-grey">Ce client n’a pas encore de procédure enregistrée.</p>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Dialog Modification Client -->
    <v-dialog v-model="showEditDialog" max-width="700" persistent>
      <v-card>
        <v-card-title class="bg-indigo-darken-4 text-white py-4">
          <v-icon start color="white">mdi-pencil</v-icon>
          Modifier le client
        </v-card-title>
        <v-card-text class="pa-6">
          <v-form ref="editForm">
            <!-- Champs personne physique -->
            <template v-if="isPersonnePhysique">
              <v-row>
                <v-col cols="6">
                  <v-text-field v-model="editData.last_name" label="Nom *" variant="outlined" :rules="[v => !!v || 'Requis']" />
                </v-col>
                <v-col cols="6">
                  <v-text-field v-model="editData.first_name" label="Prénom *" variant="outlined" :rules="[v => !!v || 'Requis']" />
                </v-col>
              </v-row>
            </template>
            <!-- Champs personne morale -->
            <template v-else>
              <v-text-field v-model="editData.company_name" label="Raison sociale *" variant="outlined" class="mb-4" :rules="[v => !!v || 'Requis']" />
              <v-row>
                <v-col cols="6">
                  <v-text-field v-model="editData.rccm" label="RCCM" variant="outlined" />
                </v-col>
                <v-col cols="6">
                  <v-text-field v-model="editData.nif" label="NIF" variant="outlined" />
                </v-col>
              </v-row>
            </template>
            <!-- Champs communs -->
            <v-row>
              <v-col cols="6">
                <v-text-field v-model="editData.email" label="Email" variant="outlined" type="email" />
              </v-col>
              <v-col cols="6">
                <v-text-field v-model="editData.phone_primary" label="Téléphone *" variant="outlined" :rules="[v => !!v || 'Requis']" />
              </v-col>
            </v-row>
            <v-text-field v-model="editData.address_line" label="Adresse" variant="outlined" class="mb-4" />
            <v-row>
              <v-col cols="6">
                <v-text-field v-model="editData.city" label="Ville" variant="outlined" />
              </v-col>
              <v-col cols="6">
                <v-text-field v-model="editData.neighborhood" label="Quartier" variant="outlined" />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-6 pt-0">
          <v-spacer />
          <v-btn variant="text" @click="showEditDialog = false" :disabled="editLoading">Annuler</v-btn>
          <v-btn color="indigo-darken-4" variant="flat" prepend-icon="mdi-check" :loading="editLoading" @click="saveClient">
            Enregistrer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.space-y-6 > * + * {
  margin-top: 1.5rem;
}
.space-y-2 > * + * {
  margin-top: 0.5rem;
}
.space-y-1 > * + * {
  margin-top: 0.25rem;
}
</style>