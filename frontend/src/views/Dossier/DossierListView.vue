<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/plugins/axios'
import { useDossierStore } from '@/stores/dossier' // <-- importer ton store Pinia

const router = useRouter()
const dossierStore = useDossierStore()

const dossiers = ref([])
const loading = ref(true)
const search = ref('')
const filters = ref({
  status: '',
  category: '',
  responsible: '',
  en_retard: false
})

const pagination = ref({
  page: 1,
  page_size: 15,
  total: 0
})

const headers = [
  { title: 'Référence', key: 'reference_code', align: 'start' },
  { title: 'Titre', key: 'title' },
  { title: 'Client', key: 'client_name' },
  { title: 'Responsable', key: 'responsible_name' },
  { title: 'Catégorie', key: 'category' },
  { title: 'Statut', key: 'status' },
  { title: 'Délai critique', key: 'critical_deadline' },
  { title: 'Actions', key: 'actions', sortable: false }
]

onMounted(async () => {
  await fetchDossiers()
})

const fetchDossiers = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.page_size,
      search: search.value || undefined,
      ordering: '-opening_date',
    }

    if (filters.value.status) params.status = filters.value.status
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.responsible) params.responsible = filters.value.responsible
    if (filters.value.en_retard) params.critical_deadline__lt = new Date().toISOString().split('T')[0]

    // Exemple : utilisation du store si tu veux centraliser
    // await dossierStore.fetchList(params)
    // dossiers.value = dossierStore.items
    // pagination.value.total = dossierStore.total

    // Sinon appel direct API
    const response = await api.get('/dossiers/', { params })
    dossiers.value = response.data.results ?? response.data
    pagination.value.total = response.data.count ?? dossiers.value.length
  } catch (err) {
    console.error('Erreur chargement dossiers', err)
  } finally {
    loading.value = false
  }
}

const goToDetail = (id) => {
  router.push(`/dossiers/${id}`)
}

const goToCreate = () => {
  router.push('/dossiers/create')
}

const getStatusColor = (status) => {
  switch (status) {
    case 'OUVERT': return 'indigo'
    case 'ATTENTE': return 'orange'
    case 'CLOTURE': return 'green'
    case 'ARCHIVE': return 'grey'
    default: return 'blue-grey-darken-1'
  }
}

const isOverdue = (deadline) => {
  if (!deadline) return false
  return new Date(deadline) < new Date()
}
</script>

<template>
  <div>
    <!-- En-tête -->
    <div class="d-flex align-center justify-space-between mb-6">
      <div class="d-flex align-center">
        <v-icon size="40" color="indigo-darken-4" class="mr-3">mdi-folder-multiple</v-icon>
        <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
          Dossiers du cabinet
        </h1>
      </div>
      <v-btn
        color="#FFD700"
        prepend-icon="mdi-plus"
        size="large"
        class="text-indigo-darken-4 font-weight-bold"
        @click="goToCreate"
      >
        Nouveau dossier
      </v-btn>
    </div>

    <!-- Filtres et recherche -->
    <v-card class="mb-6" elevation="2">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search"
              label="Rechercher (réf, titre, client...)"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              clearable
              @update:model-value="fetchDossiers"
            />
          </v-col>
          <v-col cols="12" sm="6" md="2">
            <v-select
              v-model="filters.status"
              :items="['', 'OUVERT', 'ATTENTE', 'CLOTURE', 'ARCHIVE']"
              label="Statut"
              variant="outlined"
              clearable
              @update:model-value="fetchDossiers"
            />
          </v-col>
          <v-col cols="12" sm="6" md="2">
            <v-select
              v-model="filters.category"
              :items="['', 'CONTENTIEUX', 'IMMOBILIER', 'SUCCESSION', 'FAMILLE', 'COMMERCIAL', 'SOCIETE']"
              label="Catégorie"
              variant="outlined"
              clearable
              @update:model-value="fetchDossiers"
            />
          </v-col>
          <v-col cols="12" sm="6" md="2">
            <v-checkbox
              v-model="filters.en_retard"
              label="En retard uniquement"
              color="red-darken-2"
              @update:model-value="fetchDossiers"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Tableau des dossiers -->
    <v-data-table
      v-model:page="pagination.page"
      :headers="headers"
      :items="dossiers"
      :items-per-page="pagination.page_size"
      :items-length="pagination.total"
      :loading="loading"
      loading-text="Chargement des dossiers..."
      class="elevation-3"
      hover
      @update:page="fetchDossiers"
    >
      <template v-slot:item.reference_code="{ item }">
        <strong class="text-indigo-darken-3">{{ item.reference_code }}</strong>
      </template>

      <template v-slot:item.status="{ item }">
        <v-chip :color="getStatusColor(item.status)" small>
          {{ item.status }}
        </v-chip>
      </template>

      <template v-slot:item.critical_deadline="{ item }">
        <span :class="{ 'red--text font-weight-bold': isOverdue(item.critical_deadline) }">
          {{ item.critical_deadline ? new Date(item.critical_deadline).toLocaleDateString('fr-FR') : '-' }}
        </span>
        <v-icon v-if="isOverdue(item.critical_deadline)" small color="red" class="ml-1">
          mdi-alert
        </v-icon>
      </template>

      <template v-slot:item.actions="{ item }">
        <v-btn
          icon
          small
          color="indigo"
          @click="goToDetail(item.id)"
          title="Voir le détail"
        >
          <v-icon>mdi-eye</v-icon>
        </v-btn>
      </template>

      <template v-slot:no-data>
        <v-alert type="info" outlined class="my-8 text-center">
          Aucun dossier trouvé. Créez le premier !
        </v-alert>
      </template>
    </v-data-table>
  </div>
</template>