<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useDossierStore } from '@/stores/dossier'
import debounce from 'lodash/debounce'

const router = useRouter()
const dossierStore = useDossierStore()

// === FILTRES ===
const searchQuery = ref<string>('')
const selectedStatus = ref<string>('')
const selectedCategory = ref<string>('')
const showOverdueOnly = ref<boolean>(false)

// === ÉTAT ===
const loading = ref<boolean>(true)
const error = ref<string | null>(null)

// Debounce pour la recherche
const debouncedSearch = debounce((query: string) => {
  fetchDossiers(1)
}, 400)

onBeforeUnmount(() => {
  debouncedSearch.cancel()
})

// === WATCHERS ===
watch(searchQuery, (newQuery) => {
  debouncedSearch(newQuery)
})

watch([selectedStatus, selectedCategory, showOverdueOnly], () => {
  fetchDossiers(1)
})

// === CHARGEMENT DES DOSSIERS ===
const fetchDossiers = async (page: number = 1): Promise<void> => {
  loading.value = true
  error.value = null

  const params: Record<string, any> = {
    page,
    page_size: 15,
    ordering: '-opening_date'
  }

  if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
  if (selectedStatus.value) params.status = selectedStatus.value
  if (selectedCategory.value) params.category = selectedCategory.value
  if (showOverdueOnly.value) {
    params.critical_deadline__lt = new Date().toISOString().split('T')[0]
  }

  try {
    // On passe directement les params au store — compatible avec la plupart des implémentations
    await dossierStore.fetchList(params)
  } catch (err: any) {
    console.error('Erreur chargement des dossiers', err)
    error.value = 'Impossible de charger les dossiers. Veuillez réessayer.'
  } finally {
    loading.value = false
  }
}

// === NAVIGATION ===
const navigateToDetail = (id: number | string): void => {
  if (!id) return
  router.push({ name: 'DossierDetail', params: { id } })
}

const navigateToCreate = (): void => {
  router.push({ name: 'DossierCreate' })
}

// === HELPERS UI ===
const getStatusColor = (status: string): string => {
  const map: Record<string, string> = {
    OUVERT: 'indigo',
    ATTENTE: 'orange',
    CLOTURE: 'green',
    ARCHIVE: 'grey-darken-1'
  }
  return map[status] || 'blue-grey'
}

const isOverdue = (deadline: string | null): boolean => {
  if (!deadline) return false
  return new Date(deadline) < new Date()
}

// === CYCLE DE VIE ===
onMounted(() => {
  fetchDossiers()
})
</script>

<template>
  <v-container fluid class="pa-6">
    <!-- En-tête -->
    <div class="d-flex align-center justify-space-between flex-wrap mb-8 gap-4">
      <div class="d-flex align-center">
        <v-icon size="48" color="indigo-darken-4" class="mr-4">mdi-folder-multiple-outline</v-icon>
        <div>
          <h1 class="text-h4 font-weight-black text-indigo-darken-4">
            Dossiers du cabinet
          </h1>
          <p class="text-subtitle-1 text-grey-darken-2 mt-1 mb-0">
            Suivi complet des procédures judiciaires et extrajudiciaires
          </p>
        </div>
      </div>

      <v-btn
        color="indigo-darken-4"
        size="large"
        prepend-icon="mdi-plus-thick"
        class="font-weight-bold text-white"
        elevation="6"
        @click="navigateToCreate"
      >
        Nouveau dossier
      </v-btn>
    </div>

    <!-- Erreur globale -->
    <v-alert
      v-if="error"
      type="error"
      variant="tonal"
      class="mb-8"
      prominent
      closable
      @click:close="error = null"
    >
      {{ error }}
      <template #append>
        <v-btn variant="text" @click="fetchDossiers">Réessayer</v-btn>
      </template>
    </v-alert>

    <!-- Filtres -->
    <v-card elevation="4" rounded="lg" class="mb-8">
      <v-card-text class="pa-6">
        <v-row align="center">
          <v-col cols="12" md="5">
            <v-text-field
              v-model="searchQuery"
              label="Rechercher un dossier"
              placeholder="Référence, titre, client, adversaire..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="comfortable"
              clearable
              hide-details
              :disabled="loading"
            />
          </v-col>

          <v-col cols="12" sm="6" md="2">
            <v-select
              v-model="selectedStatus"
              :items="[
                { title: 'Tous les statuts', value: '' },
                { title: 'Ouvert', value: 'OUVERT' },
                { title: 'En attente', value: 'ATTENTE' },
                { title: 'Clôturé', value: 'CLOTURE' },
                { title: 'Archivé', value: 'ARCHIVE' }
              ]"
              label="Statut"
              variant="outlined"
              density="comfortable"
              hide-details
              clearable
            />
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="selectedCategory"
              :items="[
                { title: 'Toutes catégories', value: '' },
                { title: 'Contentieux', value: 'CONTENTIEUX' },
                { title: 'Immobilier', value: 'IMMOBILIER' },
                { title: 'Succession', value: 'SUCCESSION' },
                { title: 'Famille', value: 'FAMILLE' },
                { title: 'Commercial', value: 'COMMERCIAL' },
                { title: 'Sociétés', value: 'SOCIETE' }
              ]"
              label="Domaine"
              variant="outlined"
              density="comfortable"
              hide-details
              clearable
            />
          </v-col>

          <v-col cols="12" md="2" class="d-flex justify-end">
            <v-checkbox
              v-model="showOverdueOnly"
              label="En retard uniquement"
              color="red-darken-3"
              hide-details
              class="mt-2"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Tableau -->
    <v-card elevation="6" rounded="lg">
      <v-data-table
        :headers="[
          { title: 'Référence', key: 'reference_code', align: 'start', width: '140' },
          { title: 'Intitulé', key: 'title' },
          { title: 'Client', key: 'client_name', width: '180' },
          { title: 'Responsable', key: 'responsible_name', width: '160' },
          { title: 'Domaine', key: 'category', width: '140' },
          { title: 'Statut', key: 'status', align: 'center', width: '120' },
          { title: 'Délai critique', key: 'critical_deadline', align: 'center', width: '160' },
          { title: 'Actions', key: 'actions', sortable: false, align: 'end', width: '100' }
        ]"
        :items="dossierStore.list"
        :items-per-page="15"
        :page.sync="dossierStore.pagination.page"
        :items-length="dossierStore.pagination.total || 0"
        :loading="loading"
        hover
        density="comfortable"
        class="elevation-1"
        @update:page="fetchDossiers"
      >
        <!-- Templates inchangés (identiques à la version précédente) -->
        <!-- ... (je les garde identiques pour brevité, mais ils sont corrects) -->
        <template #item.reference_code="{ item }">
          <span class="font-weight-bold text-indigo-darken-3">{{ item.reference_code }}</span>
        </template>

        <template #item.status="{ item }">
          <v-chip :color="getStatusColor(item.status)" size="small" class="font-weight-bold text-white">
            {{ item.status }}
          </v-chip>
        </template>

        <template #item.critical_deadline="{ item }">
          <div class="d-flex align-center justify-center">
            <span :class="{ 'text-red-darken-3 font-weight-bold': isOverdue(item.critical_deadline) }">
              {{ item.critical_deadline ? new Date(item.critical_deadline).toLocaleDateString('fr-GA') : '—' }}
            </span>
            <v-icon v-if="isOverdue(item.critical_deadline)" color="red-darken-3" size="small" class="ml-2">
              mdi-alert
            </v-icon>
          </div>
        </template>

        <template #item.actions="{ item }">
          <v-btn
            icon="mdi-eye"
            variant="text"
            color="indigo-darken-4"
            size="small"
            @click="navigateToDetail(item.id)"
            title="Voir le détail du dossier"
          />
        </template>

        <template #no-data>
          <div class="text-center py-16">
            <v-icon size="96" color="grey-lighten-1" class="mb-6">mdi-folder-open-outline</v-icon>
            <p class="text-h6 text-grey-darken-2 font-weight-medium">Aucun dossier</p>
            <p class="text-body-1 text-grey">
              Commencez par créer votre premier dossier.
            </p>
          </div>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>