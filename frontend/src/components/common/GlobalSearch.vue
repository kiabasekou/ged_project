<script setup>
import { ref, watch, computed } from 'vue'
import api from '@/plugins/axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const searchQuery = ref('')
const results = ref([])
const loading = ref(false)
const open = ref(false)

// Débounce simple
let debounceTimer = null

watch(searchQuery, (newVal) => {
  if (newVal.trim().length < 2) {
    results.value = []
    open.value = false
    return
  }

  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    performGlobalSearch(newVal.trim())
  }, 400) // 400ms debounce
})

const performGlobalSearch = async (query) => {
  loading.value = true
  open.value = true
  try {
    // Recherche parallèle sur les 3 endpoints principaux
    const [dossiersRes, clientsRes, documentsRes] = await Promise.all([
      api.get('/dossiers/', { params: { search: query, page_size: 5 } }).catch(() => ({ data: { results: [] } })),
      api.get('/clients/', { params: { search: query, page_size: 5 } }).catch(() => ({ data: { results: [] } })),
      api.get('/documents/', { params: { search: query, page_size: 5 } }).catch(() => ({ data: { results: [] } }))
    ])

    results.value = [
      ...dossiersRes.data.results.map(item => ({ ...item, type: 'dossier', icon: 'mdi-folder-multiple', color: 'indigo' })),
      ...clientsRes.data.results.map(item => ({ ...item, type: 'client', icon: 'mdi-account', color: 'blue' })),
      ...documentsRes.data.results.map(item => ({ ...item, type: 'document', icon: 'mdi-file-document', color: 'grey-darken-1' }))
    ].slice(0, 10) // Limite à 10 résultats max
  } catch (err) {
    console.error('Erreur recherche globale', err)
    results.value = []
  } finally {
    loading.value = false
  }
}

const goToResult = (item) => {
  open.value = false
  searchQuery.value = ''

  if (item.type === 'dossier') {
    router.push(`/dossiers/${item.id}`)
  } else if (item.type === 'client') {
    router.push(`/clients/${item.id}`)
  } else if (item.type === 'document') {
    // Téléchargement direct ou ouverture dans le dossier parent
    if (item.file_url) {
      window.open(item.file_url, '_blank')
    }
  }
}

const closeSearch = () => {
  open.value = false
  searchQuery.value = ''
  results.value = []
}
</script>

<template>
  <v-menu
    v-model="open"
    :close-on-content-click="false"
    location="bottom end"
    offset="10"
    max-width="500"
    min-width="400"
    transition="scale-transition"
  >
    <template v-slot:activator="{ props }">
      <v-text-field
        v-model="searchQuery"
        placeholder="Rechercher un dossier, client ou document..."
        prepend-inner-icon="mdi-magnify"
        variant="outlined"
        density="comfortable"
        hide-details
        clearable
        class="global-search"
        v-bind="props"
        @click:clear="closeSearch"
      />
    </template>

    <v-card elevation="8" class="search-results-card">
      <v-card-text class="pa-0">
        <v-list v-if="loading" class="text-center py-8">
          <v-progress-circular indeterminate color="indigo-darken-4" />
          <p class="mt-4 text-grey-darken-2">Recherche en cours...</p>
        </v-list>

        <v-list v-else-if="results.length === 0 && searchQuery.length >= 2" class="text-center py-8">
          <v-icon size="64" color="grey-lighten-1">mdi-magnify</v-icon>
          <p class="mt-4 text-grey-darken-2">Aucun résultat trouvé</p>
        </v-list>

        <v-list v-else density="compact">
          <v-list-subheader class="font-weight-bold text-indigo-darken-4">
            Résultats ({{ results.length }})
          </v-list-subheader>

          <v-list-item
            v-for="item in results"
            :key="`${item.type}-${item.id}`"
            @click="goToResult(item)"
            class="cursor-pointer"
            active-class="bg-amber-lighten-5"
          >
            <template v-slot:prepend>
              <v-icon :color="item.color" size="32">
                {{ item.icon }}
              </v-icon>
            </template>

            <v-list-item-title class="font-weight-medium">
              <span v-if="item.type === 'dossier'">
                [{{ item.reference_code }}] {{ item.title }}
              </span>
              <span v-else-if="item.type === 'client'">
                {{ item.display_name }}
              </span>
              <span v-else-if="item.type === 'document'">
                {{ item.title }} <small class="text-grey">(v{{ item.version }})</small>
              </span>
            </v-list-item-title>

            <v-list-item-subtitle>
              <v-chip size="x-small" :color="item.color" class="mr-2">
                {{ item.type === 'dossier' ? 'Dossier' : item.type === 'client' ? 'Client' : 'Document' }}
              </v-chip>
              <span v-if="item.client_name" class="text-grey-darken-1">
                {{ item.client_name }}
              </span>
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<style scoped>
.global-search {
  max-width: 500px;
  min-width: 300px;
}

.cursor-pointer {
  cursor: pointer;
}

.search-results-card {
  max-height: 70vh;
  overflow-y: auto;
}
</style>