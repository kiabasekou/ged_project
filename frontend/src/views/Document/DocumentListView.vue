<template>
  <v-container fluid class="pa-6">
    <!-- En-tête -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center">
          <div>
            <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
              Documents
            </h1>
            <p class="text-subtitle-1 text-grey-darken-1 mt-1">
              {{ totalDocuments }} document{{ totalDocuments > 1 ? 's' : '' }}
            </p>
          </div>
          <v-btn
            color="indigo"
            prepend-icon="mdi-plus"
            :to="{ name: 'DocumentUpload' }"
          >
            Nouveau document
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Filtres et recherche -->
    <v-card elevation="1" class="mb-6">
      <v-card-text>
        <v-row>
          <!-- Recherche -->
          <v-col cols="12" md="4">
            <v-text-field
              v-model="filters.search"
              prepend-inner-icon="mdi-magnify"
              label="Rechercher un document..."
              variant="outlined"
              density="compact"
              clearable
              hide-details
              @update:model-value="debouncedSearch"
            />
          </v-col>

          <!-- Dossier -->
          <v-col cols="12" md="3">
            <v-autocomplete
              v-model="filters.dossier"
              :items="dossiers"
              item-title="display_name"
              item-value="id"
              label="Dossier"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              prepend-inner-icon="mdi-folder"
              @update:model-value="loadDocuments"
            />
          </v-col>

          <!-- Sensibilité -->
          <v-col cols="12" md="2">
            <v-select
              v-model="filters.sensitivity"
              :items="sensitivityOptions"
              label="Sensibilité"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              @update:model-value="loadDocuments"
            />
          </v-col>

          <!-- Extension -->
          <v-col cols="12" md="2">
            <v-select
              v-model="filters.extension"
              :items="extensionOptions"
              label="Type de fichier"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              @update:model-value="loadDocuments"
            />
          </v-col>

          <!-- Actions rapides -->
          <v-col cols="12" md="1" class="d-flex align-center">
            <v-btn
              icon="mdi-refresh"
              variant="text"
              @click="loadDocuments"
              :loading="loading"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Liste des documents -->
    <v-card elevation="2">
      <!-- Toolbar -->
      <v-toolbar color="grey-lighten-4" density="compact">
        <v-toolbar-title class="text-subtitle-2">
          {{ documents.length }} résultat{{ documents.length > 1 ? 's' : '' }}
        </v-toolbar-title>
        <v-spacer />
        <v-btn-toggle v-model="viewMode" mandatory density="compact">
          <v-btn value="list" icon="mdi-view-list" size="small" />
          <v-btn value="grid" icon="mdi-view-grid" size="small" />
        </v-btn-toggle>
      </v-toolbar>

      <!-- Vue Liste -->
      <v-data-table
        v-if="viewMode === 'list'"
        :headers="headers"
        :items="documents"
        :loading="loading"
        :items-per-page="20"
        class="elevation-0"
      >
        <!-- Titre avec icône -->
        <template v-slot:item.title="{ item }">
          <div class="d-flex align-center">
            <v-icon :color="getFileIconColor(item.file_extension)" class="mr-2">
              {{ getFileIcon(item.file_extension) }}
            </v-icon>
            <div>
              <div class="font-weight-medium">{{ item.title }}</div>
              <div class="text-caption text-grey">
                {{ item.original_filename }}
              </div>
            </div>
          </div>
        </template>

        <!-- Dossier -->
        <template v-slot:item.dossier="{ item }">
          <v-chip
            size="small"
            variant="outlined"
            :to="{ name: 'DossierDetail', params: { id: item.dossier } }"
          >
            {{ getDossierName(item.dossier) }}
          </v-chip>
        </template>

        <!-- Sensibilité -->
        <template v-slot:item.sensitivity="{ item }">
          <v-chip
            size="small"
            :color="getSensitivityColor(item.sensitivity)"
            variant="tonal"
          >
            <v-icon start size="small">
              {{ getSensitivityIcon(item.sensitivity) }}
            </v-icon>
            {{ getSensitivityLabel(item.sensitivity) }}
          </v-chip>
        </template>

        <!-- Taille -->
        <template v-slot:item.file_size_human="{ item }">
          <span class="text-caption">{{ item.file_size_human }}</span>
        </template>

        <!-- Date -->
        <template v-slot:item.uploaded_at="{ item }">
          <div class="text-caption">
            {{ formatDate(item.uploaded_at) }}
          </div>
        </template>

        <!-- Actions -->
        <template v-slot:item.actions="{ item }">
          <div class="d-flex gap-1">
            <v-btn
              icon="mdi-eye"
              size="small"
              variant="text"
              :to="{ name: 'DocumentDetail', params: { id: item.id } }"
            />
            <v-btn
              icon="mdi-download"
              size="small"
              variant="text"
              @click="downloadDocument(item)"
            />
            <v-menu>
              <template v-slot:activator="{ props }">
                <v-btn
                  icon="mdi-dots-vertical"
                  size="small"
                  variant="text"
                  v-bind="props"
                />
              </template>
              <v-list density="compact">
                <v-list-item
                  prepend-icon="mdi-file-upload"
                  @click="openVersionDialog(item)"
                >
                  Nouvelle version
                </v-list-item>
                <v-list-item
                  prepend-icon="mdi-history"
                  @click="viewHistory(item)"
                >
                  Historique
                </v-list-item>
                <v-divider />
                <v-list-item
                  prepend-icon="mdi-delete"
                  class="text-error"
                  @click="deleteDocument(item)"
                >
                  Supprimer
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </template>
      </v-data-table>

      <!-- Vue Grille -->
      <v-container v-else-if="viewMode === 'grid'" fluid class="pa-4">
        <v-row>
          <v-col
            v-for="doc in documents"
            :key="doc.id"
            cols="12"
            sm="6"
            md="4"
            lg="3"
          >
            <v-card
              elevation="1"
              hover
              @click="$router.push({ name: 'DocumentDetail', params: { id: doc.id } })"
              class="document-card"
            >
              <!-- Preview / Icône -->
              <div class="document-preview">
                <v-icon size="64" :color="getFileIconColor(doc.file_extension)">
                  {{ getFileIcon(doc.file_extension) }}
                </v-icon>
              </div>

              <v-card-text>
                <div class="text-subtitle-2 text-truncate mb-1">
                  {{ doc.title }}
                </div>
                <div class="text-caption text-grey text-truncate">
                  {{ doc.original_filename }}
                </div>
                
                <div class="d-flex justify-space-between align-center mt-3">
                  <v-chip size="x-small" variant="tonal">
                    {{ doc.file_size_human }}
                  </v-chip>
                  <v-chip
                    size="x-small"
                    :color="getSensitivityColor(doc.sensitivity)"
                    variant="tonal"
                  >
                    {{ getSensitivityLabel(doc.sensitivity) }}
                  </v-chip>
                </div>
              </v-card-text>

              <v-card-actions>
                <v-spacer />
                <v-btn
                  icon="mdi-download"
                  size="small"
                  variant="text"
                  @click.stop="downloadDocument(doc)"
                />
                <v-btn
                  icon="mdi-dots-vertical"
                  size="small"
                  variant="text"
                  @click.stop
                />
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>

        <!-- État vide -->
        <v-row v-if="!loading && documents.length === 0">
          <v-col cols="12" class="text-center py-12">
            <v-icon size="64" color="grey">mdi-file-document-outline</v-icon>
            <p class="text-h6 text-grey mt-4">Aucun document trouvé</p>
          </v-col>
        </v-row>
      </v-container>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDocumentStore } from '@/stores/document'
import { useDossierStore } from '@/stores/dossier'
import { debounce } from 'lodash-es'

const router = useRouter()
const documentStore = useDocumentStore()
const dossierStore = useDossierStore()

// État
const loading = ref(false)
const documents = ref([])
const dossiers = ref([])
const totalDocuments = ref(0)
const viewMode = ref('list')

const filters = reactive({
  search: '',
  dossier: null,
  sensitivity: null,
  extension: null
})

// Options
const sensitivityOptions = [
  { title: 'Normal', value: 'NORMAL' },
  { title: 'Confidentiel', value: 'CONFIDENTIAL' },
  { title: 'Secret/Critique', value: 'CRITICAL' }
]

const extensionOptions = [
  { title: 'PDF', value: 'pdf' },
  { title: 'Word', value: 'docx' },
  { title: 'Excel', value: 'xlsx' },
  { title: 'Image', value: 'jpg' }
]

// Headers pour la table
const headers = [
  { title: 'Document', key: 'title', sortable: true },
  { title: 'Dossier', key: 'dossier', sortable: false },
  { title: 'Sensibilité', key: 'sensitivity', sortable: true },
  { title: 'Taille', key: 'file_size_human', sortable: false },
  { title: 'Date', key: 'uploaded_at', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
]

// Méthodes
const loadDocuments = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.search) params.search = filters.search
    if (filters.dossier) params.dossier = filters.dossier
    if (filters.sensitivity) params.sensitivity = filters.sensitivity
    if (filters.extension) params.file_extension = filters.extension

    const response = await documentStore.fetchDocuments(params)
    documents.value = response.results || response
    totalDocuments.value = response.count || documents.value.length
  } catch (error) {
    console.error('Erreur chargement documents:', error)
  } finally {
    loading.value = false
  }
}

const debouncedSearch = debounce(() => {
  loadDocuments()
}, 500)

const loadDossiers = async () => {
  try {
    const response = await dossierStore.fetchDossiers({ limit: 100 })
    dossiers.value = response.results.map(d => ({
      id: d.id,
      display_name: `${d.reference_code} - ${d.title}`
    }))
  } catch (error) {
    console.error('Erreur chargement dossiers:', error)
  }
}

const downloadDocument = async (doc) => {
  const url = `${import.meta.env.VITE_API_BASE_URL}/documents/documents/${doc.id}/download/`
  window.open(url, '_blank')
}

const getDossierName = (dossierId) => {
  const dossier = dossiers.value.find(d => d.id === dossierId)
  return dossier?.display_name || 'N/A'
}

const getFileIcon = (extension) => {
  const icons = {
    pdf: 'mdi-file-pdf-box',
    doc: 'mdi-file-word',
    docx: 'mdi-file-word',
    xls: 'mdi-file-excel',
    xlsx: 'mdi-file-excel',
    ppt: 'mdi-file-powerpoint',
    pptx: 'mdi-file-powerpoint',
    jpg: 'mdi-file-image',
    jpeg: 'mdi-file-image',
    png: 'mdi-file-image',
    txt: 'mdi-file-document-outline',
    zip: 'mdi-folder-zip'
  }
  return icons[extension?.toLowerCase()] || 'mdi-file-document'
}

const getFileIconColor = (extension) => {
  const colors = {
    pdf: 'red',
    doc: 'blue',
    docx: 'blue',
    xls: 'green',
    xlsx: 'green',
    jpg: 'purple',
    jpeg: 'purple',
    png: 'purple'
  }
  return colors[extension?.toLowerCase()] || 'grey'
}

const getSensitivityColor = (sensitivity) => {
  const colors = {
    NORMAL: 'blue-grey',
    CONFIDENTIAL: 'orange',
    CRITICAL: 'red'
  }
  return colors[sensitivity] || 'grey'
}

const getSensitivityIcon = (sensitivity) => {
  const icons = {
    NORMAL: 'mdi-shield-check',
    CONFIDENTIAL: 'mdi-lock',
    CRITICAL: 'mdi-alert-decagram'
  }
  return icons[sensitivity] || 'mdi-shield'
}

const getSensitivityLabel = (sensitivity) => {
  const labels = {
    NORMAL: 'Normal',
    CONFIDENTIAL: 'Confidentiel',
    CRITICAL: 'Critique'
  }
  return labels[sensitivity] || sensitivity
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Chargement initial
onMounted(() => {
  loadDocuments()
  loadDossiers()
})
</script>

<style scoped>
.gap-1 {
  gap: 4px;
}

.document-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.document-card:hover {
  transform: translateY(-4px);
}

.document-preview {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 150px;
}

.document-preview v-icon {
  color: white;
}
</style>