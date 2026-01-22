<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useClientStore } from '@/stores/client'
import debounce from 'lodash/debounce' // Fortement recommandé

const router = useRouter()
const clientStore = useClientStore()

const search = ref('')
const filterType = ref(null)
const loading = ref(true)

onMounted(async () => {
  await refreshAll()
})

const refreshAll = async () => {
  loading.value = true
  try {
    // On lance les deux en parallèle pour la performance
    await Promise.all([
      clientStore.fetchList(),
      clientStore.fetchStats()
    ])
  } finally {
    loading.value = false
  }
}

/**
 * DEBOUNCE : On attend 300ms après la fin de la saisie 
 * pour ne pas saturer le backend et éviter les IDs instables.
 */
const debouncedSearch = debounce((val) => {
  clientStore.fetchList({ search: val, page: 1 })
}, 300)

watch(search, (newVal) => {
  debouncedSearch(newVal)
})

watch(filterType, (newVal) => {
  clientStore.fetchList({ client_type: newVal || undefined, page: 1 })
})

const goToDetail = (id) => {
  // GARDE-FOU CRITIQUE : Empêche la navigation vers /clients/undefined
  if (!id) {
    console.error("Tentative de navigation sans ID valide")
    return
  }
  router.push({ name: 'ClientDetail', params: { id } })
}

const goToCreate = () => {
  router.push({ name: 'ClientCreate' })
}
</script>

<template>
  <div>
    <v-row class="mb-6 align-center">
      <v-col>
        <div class="d-flex align-center">
          <v-icon size="40" color="indigo-darken-4" class="mr-3">mdi-account-tie</v-icon>
          <h1 class="text-h4 font-weight-bold text-indigo-darken-4">Portefeuille Clients</h1>
        </div>
      </v-col>
      <v-col class="text-right">
        <v-btn
          color="amber-darken-2"
          prepend-icon="mdi-plus"
          size="large"
          class="font-weight-bold"
          @click="goToCreate"
        >
          Nouveau client
        </v-btn>
      </v-col>
    </v-row>

    <v-row class="mb-6">
      <v-col v-for="(val, label) in { 
        'Total': clientStore.stats.total, 
        'Physiques': clientStore.stats.physiques, 
        'Moraux': clientStore.stats.moraux, 
        'Actifs': clientStore.stats.actifs 
      }" :key="label" cols="12" sm="6" md="3">
        <v-card elevation="2" border>
          <v-card-text class="text-center">
            <div class="text-h4 font-weight-black text-indigo-darken-4">{{ val }}</div>
            <div class="text-overline">{{ label }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-card class="mb-6" border>
      <v-card-text>
        <v-row dense>
          <v-col cols="12" md="8">
            <v-text-field
              v-model="search"
              label="Rechercher un client..."
              placeholder="Nom, Société, NIF..."
              prepend-inner-icon="mdi-magnify"
              variant="solo"
              flat
              hide-details
              clearable
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="filterType"
              :items="[
                {title: 'Tous les types', value: null},
                {title: 'Personne Physique', value: 'PHYSIQUE'},
                {title: 'Personne Morale', value: 'MORALE'}
              ]"
              label="Filtrer par type"
              variant="solo"
              flat
              hide-details
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-data-table
      :headers="[
        { title: 'Client', key: 'display_name', align: 'start' },
        { title: 'Type', key: 'client_type' },
        { title: 'Identifiant (NIF/RCCM)', key: 'nif_rccm' },
        { title: 'Contact', key: 'phone_primary' },
        { title: 'Dossiers', key: 'dossier_count', align: 'center' },
        { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
      ]"
      :items="clientStore.list"
      :loading="loading"
      hover
      class="border rounded-lg"
    >
      <template v-slot:item.display_name="{ item }">
        <span class="font-weight-bold text-indigo-darken-4">{{ item.display_name }}</span>
      </template>

      <template v-slot:item.client_type="{ item }">
        <v-chip size="small" :color="item.client_type === 'PHYSIQUE' ? 'blue' : 'amber-darken-3'">
          {{ item.client_type }}
        </v-chip>
      </template>

      <template v-slot:item.nif_rccm="{ item }">
        <code class="text-caption">{{ item.nif || item.rccm || '---' }}</code>
      </template>

      <template v-slot:item.actions="{ item }">
        <v-btn 
          icon="mdi-eye-arrow-right" 
          variant="text" 
          color="indigo-darken-4"
          @click="goToDetail(item.id)"
        ></v-btn>
      </template>
    </v-data-table>
  </div>
</template>