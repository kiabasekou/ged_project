<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/plugins/axios'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  title: '',
  category: '',
  client: null,
  responsible: authStore.user?.id || null, // Par défaut l'utilisateur connecté
  assigned_users: [],
  critical_deadline: null,
  opponent: '',
  jurisdiction: '',
  description: ''
})

const clients = ref([])
const users = ref([])
const loading = ref(false)
const clientSearch = ref('')
const errors = ref({})

const categories = [
  'CONTENTIEUX',
  'CONSEIL',
  'RECOUVREMENT',
  'TRAVAIL',
  'IMMOBILIER',
  'SUCCESSION',
  'MARIAGE',
  'DONATION',
  'SOCIETE',
  'FAMILLE',
  'COMMERCIAL',
  'AUTRE'
]

onMounted(async () => {
  await Promise.all([fetchClients(), fetchUsers()])
})

const fetchClients = async () => {
  try {
    const response = await api.get('/clients/', {
      params: { page_size: 100, ordering: 'company_name,last_name' }
    })
    clients.value = response.data.results || response.data
  } catch (err) {
    console.error('Erreur chargement clients', err)
  }
}

const fetchUsers = async () => {
  try {
    const response = await api.get('/users/')
    users.value = response.data
  } catch (err) {
    console.error('Erreur chargement utilisateurs', err)
  }
}

const filteredClients = computed(() => {
  if (!clientSearch.value) return clients.value
  const search = clientSearch.value.toLowerCase()
  return clients.value.filter(client =>
    client.display_name?.toLowerCase().includes(search) ||
    client.company_name?.toLowerCase().includes(search) ||
    client.nif?.includes(search) ||
    client.rccm?.includes(search)
  )
})

const submit = async () => {
  loading.value = true
  errors.value = {}

  try {
    const payload = {
      title: form.value.title,
      category: form.value.category,
      client: form.value.client,
      responsible: form.value.responsible,
      assigned_users: form.value.assigned_users,
      critical_deadline: form.value.critical_deadline,
      opponent: form.value.opponent || undefined,
      jurisdiction: form.value.jurisdiction || undefined,
      description: form.value.description || undefined
    }

    const response = await api.post('/dossiers/', payload)
    const newDossierId = response.data.id

    // Redirection vers le détail du nouveau dossier
    router.push(`/dossiers/${newDossierId}`)
  } catch (err) {
    if (err.response?.data) {
      errors.value = err.response.data
    } else {
      errors.value.general = 'Erreur lors de la création du dossier.'
    }
    console.error('Erreur création dossier', err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <!-- En-tête -->
    <div class="d-flex align-center mb-6">
      <v-icon size="40" color="indigo-darken-4" class="mr-3">mdi-folder-plus</v-icon>
      <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
        Créer un nouveau dossier
      </h1>
    </div>

    <v-card elevation="6" class="pa-6">
      <v-form @submit.prevent="submit">
        <v-row>
          <!-- Titre -->
          <v-col cols="12" md="8">
            <v-text-field
              v-model="form.title"
              label="Titre du dossier *"
              prepend-inner-icon="mdi-text"
              variant="outlined"
              :error-messages="errors.title"
              required
            />
          </v-col>

          <!-- Catégorie -->
          <v-col cols="12" md="4">
            <v-select
              v-model="form.category"
              :items="categories"
              label="Catégorie *"
              prepend-inner-icon="mdi-tag"
              variant="outlined"
              :error-messages="errors.category"
              required
            />
          </v-col>

          <!-- Client -->
          <v-col cols="12" md="6">
            <v-autocomplete
              v-model="form.client"
              :items="filteredClients"
              item-title="display_name"
              item-value="id"
              label="Client *"
              prepend-inner-icon="mdi-account"
              variant="outlined"
              :search-input.sync="clientSearch"
              :error-messages="errors.client"
              clearable
              required
            >
              <template v-slot:item="{ item, props }">
                <v-list-item v-bind="props">
                  <v-list-item-title>{{ item.display_name }}</v-list-item-title>
                  <v-list-item-subtitle v-if="item.nif || item.rccm">
                    {{ item.nif || item.rccm }}
                  </v-list-item-subtitle>
                </v-list-item>
              </template>
            </v-autocomplete>
          </v-col>

          <!-- Délai critique -->
          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.critical_deadline"
              label="Délai critique (audience, formalité...)"
              type="date"
              prepend-inner-icon="mdi-calendar-alert"
              variant="outlined"
              :error-messages="errors.critical_deadline"
            />
          </v-col>

          <!-- Responsable -->
          <v-col cols="12" md="6">
            <v-select
              v-model="form.responsible"
              :items="users"
              item-title="full_name"
              item-value="id"
              label="Responsable du dossier"
              prepend-inner-icon="mdi-account-tie"
              variant="outlined"
              :error-messages="errors.responsible"
            />
          </v-col>

          <!-- Collaborateurs assignés -->
          <v-col cols="12" md="6">
            <v-select
              v-model="form.assigned_users"
              :items="users.filter(u => u.id !== form.responsible)"
              item-title="full_name"
              item-value="id"
              label="Collaborateurs assignés"
              prepend-inner-icon="mdi-account-group"
              variant="outlined"
              multiple
              chips
              closable-chips
            />
          </v-col>

          <!-- Opposant & Juridiction -->
          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.opponent"
              label="Partie adverse / Opposant"
              prepend-inner-icon="mdi-scale-balance"
              variant="outlined"
            />
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.jurisdiction"
              label="Juridiction / Tribunal / Office"
              prepend-inner-icon="mdi-bank"
              variant="outlined"
            />
          </v-col>

          <!-- Notes internes -->
          <v-col cols="12">
            <v-textarea
              v-model="form.description"
              label="Résumé / Notes internes (confidentielles)"
              prepend-inner-icon="mdi-note-text"
              variant="outlined"
              rows="4"
              auto-grow
            />
          </v-col>
        </v-row>

        <!-- Erreur générale -->
        <v-alert v-if="errors.general" type="error" class="mb-6">
          {{ errors.general }}
        </v-alert>

        <!-- Actions -->
        <div class="d-flex justify-end mt-6">
          <v-btn
            variant="text"
            @click="router.push('/dossiers')"
            class="mr-4"
          >
            Annuler
          </v-btn>

          <v-btn
            color="#1A237E"
            size="large"
            type="submit"
            :loading="loading"
            :disabled="!form.title || !form.category || !form.client"
            class="text-white"
          >
            <v-icon left>mdi-check</v-icon>
            Créer le dossier
          </v-btn>
        </div>
      </v-form>
    </v-card>
  </div>
</template>