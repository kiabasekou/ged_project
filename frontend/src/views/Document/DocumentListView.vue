<template>
  <v-container fluid class="pa-6">
    <!-- En-tête -->
    <v-row class="mb-6">
      <v-col cols="12" class="d-flex align-center justify-space-between">
        <div class="d-flex align-center">
          <v-icon size="40" color="indigo-darken-4" class="mr-3">
            mdi-file-document-multiple
          </v-icon>
          <div>
            <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
              Documents
            </h1>
            <p class="text-subtitle-1 text-grey-darken-1 mb-0">
              {{ totalDocuments }} document{{ totalDocuments > 1 ? 's' : '' }} dans le cabinet
            </p>
          </div>
        </div>
        <v-btn
          color="indigo-darken-4"
          prepend-icon="mdi-plus"
          size="large"
          elevation="2"
          :to="{ name: 'DocumentUpload' }"
        >
          Nouveau document
        </v-btn>
      </v-col>
    </v-row>

    <!-- Statistiques rapides -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4 text-center border-t-lg" style="border-top: 4px solid #1A237E">
          <v-icon size="40" color="indigo-darken-4" class="mb-2">mdi-file-document</v-icon>
          <div class="text-h5 font-weight-bold">{{ stats.total || 0 }}</div>
          <div class="text-caption text-grey-darken-1">Total documents</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4 text-center border-t-lg" style="border-top: 4px solid #1976D2">
          <v-icon size="40" color="blue" class="mb-2">mdi-clock-outline</v-icon>
          <div class="text-h5 font-weight-bold">{{ stats.recent || 0 }}</div>
          <div class="text-caption text-grey-darken-1">Cette semaine</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4 text-center border-t-lg" style="border-top: 4px solid #F57C00">
          <v-icon size="40" color="orange-darken-2" class="mb-2">mdi-lock</v-icon>
          <div class="text-h5 font-weight-bold">{{ stats.confidential || 0 }}</div>
          <div class="text-caption text-grey-darken-1">Confidentiels</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4 text-center border-t-lg" style="border-top: 4px solid #D32F2F">
          <v-icon size="40" color="red-darken-2" class="mb-2">mdi-alert-decagram</v-icon>
          <div class="text-h5 font-weight-bold">{{ stats.critical || 0 }}</div>
          <div class="text-caption text-grey-darken-1">Secret professionnel</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Barre de filtres et recherche -->
    <v-card elevation="2" class="mb-6">
      <v-card-text>
        <v-row dense>
          <!-- Recherche -->
          <v-col cols="12" md="4">
            <v-text-field
              v-model="filters.search"
              prepend-inner-icon="mdi-magnify"
              label="Rechercher un document..."
              placeholder="Titre, nom de fichier, description..."
              variant="outlined"
              density="compact"
              clearable
              hide-details
              @update:model-value="debouncedSearch"
            />
          </v-col>

          <!-- Dossier -->
          <v-col cols="12" md="2">
            <v-autocomplete
              v-model="filters.dossier"
              :items="dossiers"
              :loading="loadingDossiers"
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
              prepend-inner-icon="mdi-shield-lock"
              @update:model-value="loadDocuments"
            />
          </v-col>

          <!-- Type de fichier -->
          <v-col cols="12" md="2">
            <v-select
              v-model="filters.extension"
              :items="extensionOptions"
              label="Type de fichier"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              prepend-inner-icon="mdi-file-code"
              @update:model-value="loadDocuments"
            />
          </v-col>

          <!-- Actions -->
          <v-col cols="12" md="2" class="d-flex align-center gap-2">
            <v-btn
              icon="mdi-refresh"
              variant="text"
              @click="loadDocuments"
              :loading="loading"
              title="Actualiser"
            />
            <v-btn
              icon="mdi-filter-off"
              variant="text"
              @click="resetFilters"
              title="Réinitialiser les filtres"
            />
            <v-spacer />
            <v-btn-toggle v-model="viewMode" mandatory density="compact" class="ml-auto">
              <v-btn value="list" icon="mdi-view-list" size="small" title="Vue liste" />
              <v-btn value="grid" icon="mdi-view-grid" size="small" title="Vue grille" />
            </v-btn-toggle>
          </v-col>
        </v-row>

        <!-- Filtres avancés (Collapsible) -->
        <v-expand-transition>
          <div v-if="showAdvancedFilters" class="mt-4 pt-4 border-t">
            <v-row dense>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="filters.dateFrom"
                  type="date"
                  label="Date de (depuis)"
                  variant="outlined"
                  density="compact"
                  clearable
                  hide-details
                  prepend-inner-icon="mdi-calendar-start"
                  @update:model-value="loadDocuments"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="filters.dateTo"
                  type="date"
                  label="Date à (jusqu'à)"
                  variant="outlined"
                  density="compact"
                  clearable
                  hide-details
                  prepend-inner-icon="mdi-calendar-end"
                  @update:model-value="loadDocuments"
                />
              </v-col>
              // Dans le template, masquer le filtre si pas d'users disponibles :
              <v-col cols="12" md="3" v-if="users.length > 0">
                <v-autocomplete
                  v-model="filters.uploadedBy"
                  :items="users"
                  :loading="loadingUsers"
                  item-title="full_name"
                  item-value="id"
                  label="Transmis par"
                  variant="outlined"
                  density="compact"
                  clearable
                  hide-details
                  prepend-inner-icon="mdi-account"
                  @update:model-value="loadDocuments"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.ordering"
                  :items="sortOptions"
                  label="Trier par"
                  variant="outlined"
                  density="compact"
                  hide-details
                  prepend-inner-icon="mdi-sort"
                  @update:model-value="loadDocuments"
                />
              </v-col>
            </v-row>
          </div>
        </v-expand-transition>

        <!-- Toggle filtres avancés -->
        <div class="text-center mt-2">
          <v-btn
            variant="text"
            size="small"
            @click="showAdvancedFilters = !showAdvancedFilters"
          >
            {{ showAdvancedFilters ? 'Masquer' : 'Afficher' }} les filtres avancés
            <v-icon end>
              {{ showAdvancedFilters ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
            </v-icon>
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <!-- Sélection multiple -->
    <v-expand-transition>
      <v-card v-if="selected.length > 0" elevation="2" color="indigo-lighten-5" class="mb-4">
        <v-card-text class="d-flex align-center">
          <v-icon color="indigo-darken-4" class="mr-3">mdi-checkbox-marked-multiple</v-icon>
          <span class="font-weight-bold text-indigo-darken-4">
            {{ selected.length }} document{{ selected.length > 1 ? 's' : '' }} sélectionné{{ selected.length > 1 ? 's' : '' }}
          </span>
          <v-spacer />
          <v-btn
            variant="text"
            prepend-icon="mdi-download-multiple"
            @click="downloadMultiple"
            :loading="downloadingMultiple"
          >
            Télécharger
          </v-btn>
          <v-btn
            variant="text"
            color="error"
            prepend-icon="mdi-delete"
            @click="deleteMultiple"
          >
            Supprimer
          </v-btn>
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="selected = []"
          />
        </v-card-text>
      </v-card>
    </v-expand-transition>

    <!-- Liste des documents -->
    <v-card elevation="2">
      <!-- Toolbar -->
      <v-toolbar color="grey-lighten-4" density="compact">
        <v-toolbar-title class="text-subtitle-2">
          {{ documents.length }} résultat{{ documents.length > 1 ? 's' : '' }}
        </v-toolbar-title>
        <v-spacer />
        <v-chip
          v-if="hasActiveFilters"
          size="small"
          color="indigo"
          variant="tonal"
          closable
          @click:close="resetFilters"
        >
          Filtres actifs
        </v-chip>
      </v-toolbar>

      <!-- Vue Liste -->
      <v-data-table
        v-if="viewMode === 'list'"
        v-model="selected"
        :headers="headers"
        :items="documents"
        :loading="loading"
        item-value="id"
        show-select
        :items-per-page="pagination.pageSize"
        hide-default-footer
        class="elevation-0"
      >
        <!-- Titre avec icône -->
        <template v-slot:item.title="{ item }">
          <div class="d-flex align-center">
            <v-avatar
              size="36"
              :color="getFileIconColor(item.file_extension)"
              class="mr-3"
            >
              <v-icon color="white" size="20">
                {{ getFileIcon(item.file_extension) }}
              </v-icon>
            </v-avatar>
            <div>
              <div class="font-weight-medium text-truncate" style="max-width: 300px">
                {{ item.title }}
              </div>
              <div class="text-caption text-grey">
                {{ item.original_filename }}
              </div>
            </div>
          </div>
        </template>

        <!-- Dossier -->
        <template v-slot:item.dossier="{ item }">
          <v-chip
            v-if="item.dossier_info"
            size="small"
            variant="outlined"
            :to="{ name: 'DossierDetail', params: { id: item.dossier } }"
          >
            <v-icon start size="16">mdi-folder</v-icon>
            {{ item.dossier_info.reference_code }}
          </v-chip>
          <span v-else class="text-grey">—</span>
        </template>

        <!-- Sensibilité -->
        <template v-slot:item.sensitivity="{ item }">
          <v-chip
            size="small"
            :color="getSensitivityColor(item.sensitivity)"
            variant="tonal"
          >
            <v-icon start size="16">
              {{ getSensitivityIcon(item.sensitivity) }}
            </v-icon>
            {{ getSensitivityLabel(item.sensitivity) }}
          </v-chip>
        </template>

        <!-- Taille -->
        <template v-slot:item.file_size="{ item }">
          <span class="text-caption">{{ formatFileSize(item.file_size) }}</span>
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
              title="Voir le détail"
            />
            <v-btn
              icon="mdi-download"
              size="small"
              variant="text"
              @click="downloadDocument(item)"
              title="Télécharger"
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
                  @click="openNewVersionDialog(item)"
                >
                  Nouvelle version
                </v-list-item>
                <v-list-item
                  prepend-icon="mdi-history"
                  :to="{ name: 'DocumentDetail', params: { id: item.id }, query: { tab: 'versions' } }"
                >
                  Historique versions
                </v-list-item>
                <v-list-item
                  prepend-icon="mdi-pencil"
                  @click="openEditDialog(item)"
                >
                  Modifier métadonnées
                </v-list-item>
                <v-divider />
                <v-list-item
                  prepend-icon="mdi-delete"
                  class="text-error"
                  @click="confirmDelete(item)"
                >
                  Supprimer
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </template>

        <!-- État vide -->
        <template v-slot:no-data>
          <div class="text-center py-12">
            <v-icon size="80" color="grey-lighten-2" class="mb-4">
              mdi-file-document-remove-outline
            </v-icon>
            <div class="text-h6 text-grey">Aucun document trouvé</div>
            <div class="text-caption text-grey mb-4">
              {{ hasActiveFilters ? 'Essayez de modifier vos critères de recherche' : 'Commencez par transmettre un document' }}
            </div>
            <v-btn
              v-if="!hasActiveFilters"
              color="indigo-darken-4"
              prepend-icon="mdi-plus"
              :to="{ name: 'DocumentUpload' }"
            >
              Nouveau document
            </v-btn>
          </div>
        </template>
      </v-data-table>

      <!-- Vue Grille -->
      <v-container v-else-if="viewMode === 'grid'" fluid class="pa-4">
        <v-row v-if="loading" justify="center" class="py-12">
          <v-progress-circular indeterminate size="64" color="indigo" />
        </v-row>

        <v-row v-else-if="documents.length === 0">
          <v-col cols="12" class="text-center py-12">
            <v-icon size="80" color="grey-lighten-2" class="mb-4">
              mdi-file-document-remove-outline
            </v-icon>
            <div class="text-h6 text-grey">Aucun document trouvé</div>
          </v-col>
        </v-row>

        <v-row v-else>
          <v-col
            v-for="doc in documents"
            :key="doc.id"
            cols="12"
            sm="6"
            md="4"
            lg="3"
          >
            <v-card
              elevation="2"
              hover
              class="document-card h-100"
              @click="$router.push({ name: 'DocumentDetail', params: { id: doc.id } })"
            >
              <!-- Preview / Icône -->
              <div class="document-preview pa-6 text-center bg-grey-lighten-4">
                <v-icon size="64" :color="getFileIconColor(doc.file_extension)">
                  {{ getFileIcon(doc.file_extension) }}
                </v-icon>
              </div>

              <v-card-text>
                <!-- Titre -->
                <div class="text-subtitle-2 font-weight-bold text-truncate mb-2">
                  {{ doc.title }}
                </div>

                <!-- Métadonnées -->
                <div class="d-flex flex-column gap-2">
                  <v-chip
                    size="x-small"
                    :color="getSensitivityColor(doc.sensitivity)"
                    variant="tonal"
                  >
                    <v-icon start size="12">
                      {{ getSensitivityIcon(doc.sensitivity) }}
                    </v-icon>
                    {{ getSensitivityLabel(doc.sensitivity) }}
                  </v-chip>

                  <div class="text-caption text-grey">
                    <v-icon size="14">mdi-weight</v-icon>
                    {{ formatFileSize(doc.file_size) }}
                  </div>

                  <div class="text-caption text-grey">
                    <v-icon size="14">mdi-clock-outline</v-icon>
                    {{ formatDate(doc.uploaded_at) }}
                  </div>
                </div>
              </v-card-text>

              <v-card-actions>
                <v-btn
                  size="small"
                  variant="text"
                  prepend-icon="mdi-download"
                  @click.stop="downloadDocument(doc)"
                >
                  Télécharger
                </v-btn>
                <v-spacer />
                <v-checkbox
                  v-model="selected"
                  :value="doc.id"
                  hide-details
                  density="compact"
                  @click.stop
                />
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <!-- Pagination -->
      <v-divider />
      <div class="d-flex align-center justify-space-between pa-4">
        <div class="text-caption text-grey">
          Affichage {{ ((pagination.page - 1) * pagination.pageSize) + 1 }} 
          à {{ Math.min(pagination.page * pagination.pageSize, totalDocuments) }} 
          sur {{ totalDocuments }}
        </div>

        <v-pagination
          v-model="pagination.page"
          :length="totalPages"
          :total-visible="7"
          @update:model-value="loadDocuments"
          density="compact"
          rounded
        />

        <v-select
          v-model="pagination.pageSize"
          :items="[10, 25, 50, 100]"
          label="Par page"
          variant="outlined"
          density="compact"
          hide-details
          style="max-width: 100px"
          @update:model-value="changePageSize"
        />
      </div>
    </v-card>

    <!-- Dialog Suppression -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6 bg-error text-white py-4">
          <v-icon start color="white">mdi-alert</v-icon>
          Confirmer la suppression
        </v-card-title>
        <v-card-text class="pt-6">
          <p class="text-body-1">
            Êtes-vous sûr de vouloir supprimer {{ deleteTarget?.title }} ?
          </p>
          <v-alert type="warning" variant="tonal" class="mt-4">
            Cette action est irréversible. Le document sera définitivement supprimé.
          </v-alert>
        </v-card-text>
        <v-card-actions class="px-6 pb-6">
          <v-spacer />
          <v-btn variant="text" @click="deleteDialog = false">
            Annuler
          </v-btn>
          <v-btn
            color="error"
            variant="elevated"
            :loading="deleting"
            @click="executeDelete"
          >
            Supprimer définitivement
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDocumentStore } from '@/stores/document'
import { useDossierStore } from '@/stores/dossier'
import api from '@/plugins/axios'
import { debounce } from 'lodash-es'

const router = useRouter()
const documentStore = useDocumentStore()
const dossierStore = useDossierStore()

// État
const documents = ref([])
const dossiers = ref([])
const users = ref([])
const selected = ref([])
const loading = ref(false)
const loadingDossiers = ref(false)
const loadingUsers = ref(false)
const viewMode = ref('list')
const showAdvancedFilters = ref(false)
const deleteDialog = ref(false)
const deleteTarget = ref(null)
const deleting = ref(false)
const downloadingMultiple = ref(false)

// Pagination
const pagination = ref({
  page: 1,
  pageSize: 25
})

const totalDocuments = ref(0)

// Statistiques
const stats = ref({
  total: 0,
  recent: 0,
  confidential: 0,
  critical: 0
})

// Filtres
const filters = ref({
  search: '',
  dossier: null,
  sensitivity: null,
  extension: null,
  dateFrom: null,
  dateTo: null,
  uploadedBy: null,
  ordering: '-uploaded_at'
})

// Computed
const totalPages = computed(() => 
  Math.ceil(totalDocuments.value / pagination.value.pageSize)
)

const hasActiveFilters = computed(() => {
  return filters.value.search ||
         filters.value.dossier ||
         filters.value.sensitivity ||
         filters.value.extension ||
         filters.value.dateFrom ||
         filters.value.dateTo ||
         filters.value.uploadedBy
})

// Options
const headers = [
  { title: 'Document', key: 'title', align: 'start', sortable: false },
  { title: 'Dossier', key: 'dossier', align: 'start', sortable: false },
  { title: 'Sensibilité', key: 'sensitivity', align: 'center', sortable: false },
  { title: 'Taille', key: 'file_size', align: 'end', sortable: false },
  { title: 'Date', key: 'uploaded_at', align: 'start', sortable: false },
  { title: 'Actions', key: 'actions', align: 'end', sortable: false }
]

const sensitivityOptions = [
  { title: 'Normal', value: 'NORMAL' },
  { title: 'Confidentiel', value: 'CONFIDENTIAL' },
  { title: 'Secret professionnel', value: 'CRITICAL' }
]

const extensionOptions = computed(() => {
  const extensions = [...new Set(documents.value.map(d => d.file_extension?.toUpperCase()).filter(Boolean))]
  return extensions.map(ext => ({ title: ext, value: ext.toLowerCase() }))
})

const sortOptions = [
  { title: 'Plus récent', value: '-uploaded_at' },
  { title: 'Plus ancien', value: 'uploaded_at' },
  { title: 'Titre (A-Z)', value: 'title' },
  { title: 'Titre (Z-A)', value: '-title' },
  { title: 'Taille croissante', value: 'file_size' },
  { title: 'Taille décroissante', value: '-file_size' }
]

// Méthodes
const loadDocuments = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      ordering: filters.value.ordering
    }

    if (filters.value.search) params.search = filters.value.search
    if (filters.value.dossier) params.dossier = filters.value.dossier
    if (filters.value.sensitivity) params.sensitivity = filters.value.sensitivity
    if (filters.value.extension) params.file_extension = filters.value.extension
    if (filters.value.dateFrom) params.uploaded_at__gte = filters.value.dateFrom
    if (filters.value.dateTo) params.uploaded_at__lte = filters.value.dateTo
    if (filters.value.uploadedBy) params.uploaded_by = filters.value.uploadedBy

    const response = await api.get('/documents/documents/', { params })
    
    documents.value = response.data.results || []
    totalDocuments.value = response.data.count || 0
    
    // Charger les infos des dossiers
    for (const doc of documents.value) {
      if (doc.dossier && !doc.dossier_info) {
        try {
          const dossierRes = await api.get(`/dossiers/${doc.dossier}/`)
          doc.dossier_info = dossierRes.data
        } catch (err) {
          console.error('Erreur chargement dossier:', err)
        }
      }
    }
  } catch (error) {
    console.error('Erreur chargement documents:', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await api.get('/documents/documents/', { 
      params: { page_size: 1000 } // Charger tous pour stats
    })
    const allDocs = response.data.results || []
    
    stats.value.total = allDocs.length
    
    // Documents de la semaine dernière
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    stats.value.recent = allDocs.filter(d => new Date(d.uploaded_at) > weekAgo).length
    
    // Par sensibilité
    stats.value.confidential = allDocs.filter(d => d.sensitivity === 'CONFIDENTIAL').length
    stats.value.critical = allDocs.filter(d => d.sensitivity === 'CRITICAL').length
  } catch (error) {
    console.error('Erreur chargement stats:', error)
  }
}

const loadDossiers = async () => {
  loadingDossiers.value = true
  try {
    const response = await api.get('/dossiers/', {
      params: { page_size: 100, ordering: '-opening_date' }
    })
    dossiers.value = (response.data.results || []).map(d => ({
      id: d.id,
      display_name: `${d.reference_code} - ${d.title}`
    }))
  } catch (error) {
    console.error('Erreur chargement dossiers:', error)
  } finally {
    loadingDossiers.value = false
  }
}

const loadUsers = async () => {
  loadingUsers.value = true
  try {
    // Option 1 : Utiliser l'utilisateur connecté uniquement
    const response = await api.get('/users/me/')
    users.value = [response.data]
  } catch (error) {
    console.error('Erreur chargement utilisateurs:', error)
    // En cas d'erreur, désactiver le filtre utilisateur
    users.value = []
  } finally {
    loadingUsers.value = false
  }
}

const debouncedSearch = debounce(() => {
  pagination.value.page = 1
  loadDocuments()
}, 500)

const resetFilters = () => {
  filters.value = {
    search: '',
    dossier: null,
    sensitivity: null,
    extension: null,
    dateFrom: null,
    dateTo: null,
    uploadedBy: null,
    ordering: '-uploaded_at'
  }
  pagination.value.page = 1
  loadDocuments()
}

const changePageSize = () => {
  pagination.value.page = 1
  loadDocuments()
}

const downloadDocument = (doc) => {
  const url = `${import.meta.env.VITE_API_BASE_URL}/documents/documents/${doc.id}/download/`
  window.open(url, '_blank')
}

const downloadMultiple = async () => {
  downloadingMultiple.value = true
  try {
    // TODO: Implémenter téléchargement ZIP multiple côté backend
    for (const id of selected.value) {
      const doc = documents.value.find(d => d.id === id)
      if (doc) {
        downloadDocument(doc)
        await new Promise(resolve => setTimeout(resolve, 500))
      }
    }
  } finally {
    downloadingMultiple.value = false
    selected.value = []
  }
}

const confirmDelete = (doc) => {
  deleteTarget.value = doc
  deleteDialog.value = true
}

const executeDelete = async () => {
  if (!deleteTarget.value) return
  
  deleting.value = true
  try {
    await api.delete(`/documents/documents/${deleteTarget.value.id}/`)
    documents.value = documents.value.filter(d => d.id !== deleteTarget.value.id)
    totalDocuments.value--
    deleteDialog.value = false
    deleteTarget.value = null
  } catch (error) {
    console.error('Erreur suppression:', error)
    alert('Erreur lors de la suppression du document')
  } finally {
    deleting.value = false
  }
}

const deleteMultiple = async () => {
  if (!confirm(`Supprimer définitivement ${selected.value.length} document(s) ?`)) return
  
  try {
    await Promise.all(
      selected.value.map(id => api.delete(`/documents/documents/${id}/`))
    )
    await loadDocuments()
    selected.value = []
  } catch (error) {
    console.error('Erreur suppression multiple:', error)
    alert('Erreur lors de la suppression des documents')
  }
}

const openNewVersionDialog = (doc) => {
  // TODO: Implémenter dialog nouvelle version
  console.log('Nouvelle version:', doc)
}

const openEditDialog = (doc) => {
  // TODO: Implémenter dialog édition métadonnées
  console.log('Éditer:', doc)
}

// Utilitaires
const formatFileSize = (bytes) => {
  if (!bytes) return '0 octet'
  const k = 1024
  const sizes = ['octets', 'Ko', 'Mo', 'Go']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const getFileIcon = (extension) => {
  const icons = {
    pdf: 'mdi-file-pdf-box',
    doc: 'mdi-file-word',
    docx: 'mdi-file-word',
    xls: 'mdi-file-excel',
    xlsx: 'mdi-file-excel',
    jpg: 'mdi-file-image',
    jpeg: 'mdi-file-image',
    png: 'mdi-file-image',
    txt: 'mdi-file-document',
    odt: 'mdi-file-document',
    ods: 'mdi-file-excel'
  }
  return icons[extension?.toLowerCase()] || 'mdi-file'
}

const getFileIconColor = (extension) => {
  const colors = {
    pdf: 'red',
    doc: 'blue',
    docx: 'blue',
    xls: 'green',
    xlsx: 'green',
    jpg: 'orange',
    jpeg: 'orange',
    png: 'orange',
    txt: 'grey',
    odt: 'indigo',
    ods: 'teal'
  }
  return colors[extension?.toLowerCase()] || 'grey'
}

const getSensitivityIcon = (sensitivity) => {
  const icons = {
    NORMAL: 'mdi-shield-check-outline',
    CONFIDENTIAL: 'mdi-lock',
    CRITICAL: 'mdi-alert-decagram'
  }
  return icons[sensitivity] || 'mdi-shield'
}

const getSensitivityColor = (sensitivity) => {
  const colors = {
    NORMAL: 'green',
    CONFIDENTIAL: 'orange',
    CRITICAL: 'red'
  }
  return colors[sensitivity] || 'grey'
}

const getSensitivityLabel = (sensitivity) => {
  const labels = {
    NORMAL: 'Normal',
    CONFIDENTIAL: 'Confidentiel',
    CRITICAL: 'Secret'
  }
  return labels[sensitivity] || sensitivity
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadDocuments(),
    loadStats(),
    loadDossiers(),
    loadUsers()
  ])
})
</script>

<style scoped>
.border-t-lg {
  border-top-width: 4px !important;
}

.gap-1 {
  gap: 4px;
}

.gap-2 {
  gap: 8px;
}

.document-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.document-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
}

.document-preview {
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.h-100 {
  height: 100%;
}
</style>