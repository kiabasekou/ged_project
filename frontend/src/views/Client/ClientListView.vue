<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useClientStore } from '@/stores/client'
import debounce from 'lodash/debounce'

const router = useRouter()
const clientStore = useClientStore()

// === FILTRES UTILISATEUR ===
const searchQuery = ref<string>('')
const selectedType = ref<'PHYSIQUE' | 'MORALE' | null>(null)

// === ÉTATS ===
const loading = ref<boolean>(true)
const error = ref<string | null>(null)

// Debounce pour la recherche (annulable proprement)
const debouncedSearch = debounce((query: string) => {
  clientStore.setFilters({ search: query.trim() || undefined, page: 1 })
  clientStore.fetchList()
}, 400)

// Nettoyage du debounce à la destruction du composant
onBeforeUnmount(() => {
  debouncedSearch.cancel()
})

// === WATCHERS ===
watch(searchQuery, (newQuery) => {
  debouncedSearch(newQuery)
})

watch(selectedType, (newType) => {
  clientStore.setFilters({ 
    client_type: newType || undefined, 
    page: 1 
  })
  clientStore.fetchList()
})

// === ACTIONS ===
const refreshData = async (): Promise<void> => {
  loading.value = true
  error.value = null

  try {
    await Promise.all([
      clientStore.fetchList(),
      clientStore.fetchStats()
    ])
  } catch (err: any) {
    console.error('Erreur chargement clients', err)
    error.value = 'Impossible de charger la liste des clients.'
  } finally {
    loading.value = false
  }
}

const navigateToDetail = (id: number | string): void => {
  if (!id) {
    console.warn('Tentative de navigation vers un client sans ID')
    return
  }
  router.push({ name: 'ClientDetail', params: { id } })
}

const navigateToCreate = (): void => {
  router.push({ name: 'ClientCreate' })
}

// === CYCLE DE VIE ===
onMounted(() => {
  refreshData()
})

// === COMPUTED (Cartes de statistiques) ===
const statsCards = computed(() => [
  { label: 'Total', value: clientStore.stats.total ?? 0, icon: 'mdi-account-group', color: 'indigo-darken-4' },
  { label: 'Personnes physiques', value: clientStore.stats.physiques ?? 0, icon: 'mdi-account', color: 'blue-darken-2' },
  { label: 'Personnes morales', value: clientStore.stats.moraux ?? 0, icon: 'mdi-domain', color: 'amber-darken-3' },
  { label: 'Clients actifs', value: clientStore.stats.actifs ?? 0, icon: 'mdi-check-circle', color: 'green-darken-2' }
])
</script>

<template>
  <v-container fluid class="pa-6">
    <!-- En-tête -->
    <div class="d-flex align-center justify-space-between flex-wrap mb-8 gap-4">
      <div class="d-flex align-center">
        <v-icon size="48" color="indigo-darken-4" class="mr-4">mdi-account-tie</v-icon>
        <div>
          <h1 class="text-h4 font-weight-black text-indigo-darken-4">
            Portefeuille Clients
          </h1>
          <p class="text-subtitle-1 text-grey-darken-2 mt-1 mb-0">
            Gestion complète des clients du cabinet
          </p>
        </div>
      </div>

      <v-btn
        color="indigo-darken-4"
        size="large"
        prepend-icon="mdi-plus-thick"
        class="font-weight-bold text-white"
        elevation="4"
        @click="navigateToCreate"
      >
        Nouveau client
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
        <v-btn variant="text" @click="refreshData">Réessayer</v-btn>
      </template>
    </v-alert>

    <!-- Cartes statistiques -->
    <v-row class="mb-10">
      <v-col v-for="stat in statsCards" :key="stat.label" cols="12" sm="6" md="3">
        <v-card
          elevation="8"
          class="text-center pa-6 rounded-xl transition-all hover:shadow-xl"
          :style="{ borderTop: `6px solid var(--v-${stat.color}-base)` }"
        >
          <v-icon :color="stat.color" size="56" class="mb-4">{{ stat.icon }}</v-icon>
          <div class="text-h3 font-weight-black" :class="`${stat.color}--text`">
            {{ stat.value }}
          </div>
          <div class="text-overline text-grey-darken-2 font-weight-medium">
            {{ stat.label }}
          </div>
        </v-card>
      </v-col>
  </v-row>

    <!-- Filtres -->
    <v-card elevation="4" rounded="lg" class="mb-8">
      <v-card-text class="pa-6">
        <v-row align="center" dense>
          <!-- Recherche -->
          <v-col cols="12" md="8">
            <v-text-field
              v-model="searchQuery"
              label="Rechercher un client"
              placeholder="Nom, société, NIF, RCCM, téléphone..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="comfortable"
              clearable
              hide-details
              :disabled="loading"
              autofocus
              aria-label="Recherche de clients"
            />
          </v-col>

          <!-- Filtre par type -->
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedType"
              :items="[
                { title: 'Tous les types', value: null },
                { title: 'Personne physique', value: 'PHYSIQUE' },
                { title: 'Personne morale', value: 'MORALE' }
              ]"
              label="Type de client"
              variant="outlined"
              density="comfortable"
              hide-details
              clearable
              prepend-inner-icon="mdi-filter"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Tableau des clients -->
    <v-card elevation="6" rounded="lg">
      <v-data-table
        :headers="[
          { title: 'Client', key: 'display_name', align: 'start' },
          { title: 'Type', key: 'client_type', align: 'center', width: '140' },
          { title: 'Identifiant fiscal', key: 'identifier', align: 'center', width: '160' },
          { title: 'Contact principal', key: 'phone_primary', width: '160' },
          { title: 'Dossiers actifs', key: 'dossier_count', align: 'center', width: '120' },
          { title: 'Actions', key: 'actions', sortable: false, align: 'end', width: '100' }
        ]"
        :items="clientStore.list"
        :loading="loading"
        :items-per-page="-1"
        hover
        class="elevation-1"
        density="comfortable"
      >
        <!-- Nom du client -->
        <template #item.display_name="{ item }">
          <div class="font-weight-bold text-indigo-darken-4">
            {{ item.display_name }}
          </div>
        </template>

        <!-- Type -->
        <template #item.client_type="{ item }">
          <v-chip
            size="small"
            :color="item.client_type === 'PHYSIQUE' ? 'blue-darken-1' : 'amber-darken-3'"
            class="font-weight-bold text-white"
          >
            <v-icon start size="small">
              {{ item.client_type === 'PHYSIQUE' ? 'mdi-account' : 'mdi-domain' }}
            </v-icon>
            {{ item.client_type === 'PHYSIQUE' ? 'Physique' : 'Morale' }}
          </v-chip>
        </template>

        <!-- Identifiant -->
        <template #item.identifier="{ item }">
          <code class="text-caption font-weight-medium">
            {{ item.nif || item.rccm || '—' }}
          </code>
        </template>

        <!-- Contact -->
        <template #item.phone_primary="{ item }">
          <span class="text-grey-darken-1">
            {{ item.phone_primary || 'Non renseigné' }}
          </span>
        </template>

        <!-- Nombre de dossiers -->
        <template #item.dossier_count="{ item }">
          <v-chip color="indigo" size="small" variant="flat">
            {{ item.dossier_count ?? 0 }}
          </v-chip>
        </template>

        <!-- Actions -->
        <template #item.actions="{ item }">
          <v-btn
            icon="mdi-arrow-right-bold"
            variant="text"
            color="indigo-darken-4"
            size="small"
            @click="navigateToDetail(item.id)"
            title="Voir le détail du client"
            aria-label="Voir le détail du client"
          />
        </template>

        <!-- État vide -->
        <template #no-data>
          <div class="text-center py-12">
            <v-icon size="80" color="grey-lighten-1" class="mb-4">mdi-account-off</v-icon>
            <p class="text-h6 text-grey-darken-1">Aucun client trouvé</p>
            <p v-if="searchQuery || selectedType" class="text-body-2 text-grey">
              Essayez de modifier vos filtres.
            </p>
          </div>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<style scoped>
.transition-all {
  transition: all 0.3s ease;
}

.hover\\:shadow-xl:hover {
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15) !important;
}
</style>