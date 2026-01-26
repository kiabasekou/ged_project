<template>
  <v-container fluid class="pa-6">
    <!-- Loading -->
    <v-row v-if="loading" justify="center" class="py-12">
      <v-progress-circular indeterminate size="64" color="indigo" />
    </v-row>

    <!-- Erreur 404 -->
    <v-row v-else-if="error404" justify="center">
      <v-col cols="12" md="8" class="text-center">
        <v-icon size="120" color="grey-lighten-2" class="mb-6">
          mdi-folder-remove-outline
        </v-icon>
        <h1 class="text-h4 font-weight-bold mb-4">Dossier introuvable</h1>
        <p class="text-grey mb-6">
          Le dossier demandé n'existe pas ou a été supprimé.
        </p>
        <v-btn
          color="indigo-darken-4"
          prepend-icon="mdi-arrow-left"
          @click="router.push({ name: 'DossierList' })"
        >
          Retour à la liste
        </v-btn>
      </v-col>
    </v-row>

    <!-- Contenu principal -->
    <div v-else>
      <!-- En-tête -->
      <v-row class="mb-6">
        <v-col cols="12">
          <div class="d-flex align-center mb-4">
            <v-btn
              icon="mdi-arrow-left"
              variant="text"
              @click="router.back()"
              class="mr-4"
            />
            <div class="flex-grow-1">
              <div class="d-flex align-center gap-3 mb-2">
                <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
                  {{ dossier.title || 'Chargement...' }}
                </h1>
                <v-chip
                  v-if="dossier.status"
                  :color="getStatusColor(dossier.status)"
                  size="small"
                >
                  {{ getStatusLabel(dossier.status) }}
                </v-chip>
              </div>
              <div class="text-subtitle-1 text-grey-darken-1">
                <v-icon size="18" class="mr-1">mdi-folder-key</v-icon>
                {{ dossier.reference_code || '...' }}
              </div>
            </div>
            <v-btn
              color="indigo-darken-4"
              prepend-icon="mdi-upload"
              @click="showUploadDialog = true"
            >
              Ajouter un document
            </v-btn>
          </div>
        </v-col>
      </v-row>

      <!-- Tabs -->
      <v-tabs v-model="tab" color="indigo-darken-4" class="mb-6">
        <v-tab value="info">
          <v-icon start>mdi-information</v-icon>
          Informations
        </v-tab>
        <v-tab value="documents">
          <v-icon start>mdi-file-document-multiple</v-icon>
          Documents ({{ documents.length }})
        </v-tab>
        <v-tab value="events">
          <v-icon start>mdi-calendar</v-icon>
          Événements
        </v-tab>
      </v-tabs>

      <!-- Contenu des tabs -->
      <v-window v-model="tab">
        <!-- Tab Informations -->
        <v-window-item value="info">
          <v-row>
            <v-col cols="12" md="8">
              <v-card elevation="2">
                <v-card-title class="bg-grey-lighten-4">
                  <v-icon start>mdi-card-account-details</v-icon>
                  Détails du dossier
                </v-card-title>
                <v-card-text class="pa-6">
                  <v-list density="comfortable">
                    <v-list-item v-if="dossier.client_info" prepend-icon="mdi-account-circle">
                      <v-list-item-title>Client</v-list-item-title>
                      <v-list-item-subtitle>
                        {{ dossier.client_info.display_name }}
                      </v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="dossier.category" prepend-icon="mdi-scale-balance">
                      <v-list-item-title>Catégorie</v-list-item-title>
                      <v-list-item-subtitle>{{ getCategoryLabel(dossier.category) }}</v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="dossier.responsible_info" prepend-icon="mdi-account-tie">
                      <v-list-item-title>Avocat responsable</v-list-item-title>
                      <v-list-item-subtitle>{{ dossier.responsible_info.full_name }}</v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="dossier.jurisdiction" prepend-icon="mdi-gavel">
                      <v-list-item-title>Juridiction</v-list-item-title>
                      <v-list-item-subtitle>{{ dossier.jurisdiction }}</v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="dossier.opening_date" prepend-icon="mdi-calendar-start">
                      <v-list-item-title>Date d'ouverture</v-list-item-title>
                      <v-list-item-subtitle>{{ formatDate(dossier.opening_date) }}</v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="dossier.critical_deadline" prepend-icon="mdi-calendar-alert">
                      <v-list-item-title>Délai critique</v-list-item-title>
                      <v-list-item-subtitle>
                        {{ formatDate(dossier.critical_deadline) }}
                        <v-chip
                          v-if="isOverdue"
                          size="x-small"
                          color="error"
                          class="ml-2"
                        >
                          DÉPASSÉ
                        </v-chip>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>

                  <v-divider class="my-4" v-if="dossier.notes" />

                  <div v-if="dossier.notes">
                    <h4 class="text-subtitle-2 font-weight-bold mb-2">
                      <v-icon start size="20">mdi-note-text</v-icon>
                      Notes internes
                    </h4>
                    <p class="text-body-2 text-grey-darken-1">
                      {{ dossier.notes }}
                    </p>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" md="4">
              <v-card elevation="2" class="mb-4">
                <v-card-title class="bg-grey-lighten-4">
                  <v-icon start>mdi-chart-box</v-icon>
                  Statistiques
                </v-card-title>
                <v-card-text>
                  <v-list density="compact">
                    <v-list-item>
                      <template v-slot:prepend>
                        <v-icon color="blue">mdi-file-document</v-icon>
                      </template>
                      <v-list-item-title>{{ documents.length }} documents</v-list-item-title>
                    </v-list-item>
                    <v-list-item>
                      <template v-slot:prepend>
                        <v-icon color="orange">mdi-folder</v-icon>
                      </template>
                      <v-list-item-title>{{ folders.length }} dossiers</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>

              <v-card elevation="2">
                <v-card-title class="bg-grey-lighten-4">
                  <v-icon start>mdi-cog</v-icon>
                  Actions
                </v-card-title>
                <v-card-text>
                  <v-btn
                    block
                    variant="outlined"
                    color="indigo"
                    prepend-icon="mdi-pencil"
                    class="mb-2"
                    @click="editDossier"
                  >
                    Modifier
                  </v-btn>
                  <v-btn
                    block
                    variant="outlined"
                    color="success"
                    prepend-icon="mdi-check"
                    class="mb-2"
                    @click="closeDossier"
                    v-if="dossier.status !== 'CLOTURE'"
                  >
                    Clôturer
                  </v-btn>
                  <v-btn
                    block
                    variant="outlined"
                    color="error"
                    prepend-icon="mdi-delete"
                    @click="deleteDossier"
                  >
                    Supprimer
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-window-item>

        <!-- Tab Documents -->
        <v-window-item value="documents">
          <v-row>
            <!-- Arborescence -->
            <v-col cols="12" md="3" v-if="folders.length > 0">
              <v-card elevation="2">
                <v-card-title class="bg-grey-lighten-4 text-subtitle-1">
                  <v-icon start>mdi-folder-tree</v-icon>
                  Arborescence
                </v-card-title>
                <v-card-text class="pa-2">
                  <v-treeview
                    v-model:selected="selectedFolderId"
                    :items="folders"
                    item-value="id"
                    item-title="name"
                    selectable
                    return-object
                    density="compact"
                    open-all
                  >
                    <template v-slot:prepend="{ item }">
                      <v-icon :color="item.id === selectedFolderId[0] ? 'indigo' : 'grey'">
                        mdi-folder
                      </v-icon>
                    </template>
                  </v-treeview>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Liste documents -->
            <v-col cols="12" :md="folders.length > 0 ? 9 : 12">
              <v-card elevation="2">
                <v-card-title class="bg-grey-lighten-4">
                  <v-icon start>mdi-file-document-multiple</v-icon>
                  Documents {{ selectedFolder ? `- ${selectedFolder.name}` : '' }}
                  <v-spacer />
                  <v-btn
                    size="small"
                    color="indigo"
                    prepend-icon="mdi-plus"
                    @click="showUploadDialog = true"
                  >
                    Ajouter
                  </v-btn>
                </v-card-title>

                <v-card-text v-if="loadingDocuments" class="text-center py-12">
                  <v-progress-circular indeterminate color="indigo" />
                </v-card-text>

                <v-card-text v-else-if="documents.length === 0" class="text-center py-12">
                  <v-icon size="80" color="grey-lighten-2" class="mb-4">
                    mdi-file-document-remove-outline
                  </v-icon>
                  <div class="text-h6 text-grey mb-4">Aucun document</div>
                  <v-btn
                    color="indigo-darken-4"
                    prepend-icon="mdi-upload"
                    @click="showUploadDialog = true"
                  >
                    Transmettre un document
                  </v-btn>
                </v-card-text>

                <v-list v-else>
                  <v-list-item
                    v-for="doc in documents"
                    :key="doc.id"
                    :to="{ name: 'DocumentDetail', params: { id: doc.id } }"
                    border
                  >
                    <template v-slot:prepend>
                      <v-avatar :color="getFileIconColor(doc.file_extension)">
                        <v-icon color="white">{{ getFileIcon(doc.file_extension) }}</v-icon>
                      </v-avatar>
                    </template>

                    <v-list-item-title class="font-weight-bold">
                      {{ doc.title }}
                    </v-list-item-title>
                    <v-list-item-subtitle>
                      {{ formatFileSize(doc.file_size) }} • {{ formatDate(doc.uploaded_at) }}
                    </v-list-item-subtitle>

                    <template v-slot:append>
                      <v-chip
                        size="small"
                        :color="getSensitivityColor(doc.sensitivity)"
                        variant="tonal"
                      >
                        {{ getSensitivityLabel(doc.sensitivity) }}
                      </v-chip>
                    </template>
                  </v-list-item>
                </v-list>
              </v-card>
            </v-col>
          </v-row>
        </v-window-item>

        <!-- Tab Événements -->
        <v-window-item value="events">
          <v-card elevation="2">
            <v-card-title class="bg-grey-lighten-4">
              <v-icon start>mdi-calendar</v-icon>
              Événements liés au dossier
            </v-card-title>
            <v-card-text class="text-center py-12 text-grey">
              <v-icon size="80" class="mb-4">mdi-calendar-blank</v-icon>
              <div>Fonctionnalité à venir</div>
            </v-card-text>
          </v-card>
        </v-window-item>
      </v-window>
    </div>

    <!-- Dialog Upload Document -->
    <v-dialog v-model="showUploadDialog" max-width="900" persistent>
      <DocumentUpload
        v-if="dossier.id"
        :dossier-id="dossier.id"
        :folder-id="selectedFolderId[0]"
        :available-folders="folders"
        @success="handleUploaded"
        @cancel="showUploadDialog = false"
      />
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/plugins/axios'
import DocumentUpload from '@/components/documents/DocumentUpload.vue'

const route = useRoute()
const router = useRouter()

// État
const dossier = ref({})
const folders = ref([])
const documents = ref([])
const selectedFolderId = ref([])
const loading = ref(true)
const loadingDocuments = ref(false)
const error404 = ref(false)
const tab = ref('info')
const showUploadDialog = ref(false)

// Computed
const selectedFolder = computed(() => {
  if (!selectedFolderId.value.length) return null
  const findFolder = (list, id) => {
    for (const f of list) {
      if (f.id === id) return f
      if (f.children) {
        const found = findFolder(f.children, id)
        if (found) return found
      }
    }
    return null
  }
  return findFolder(folders.value, selectedFolderId.value[0])
})

const isOverdue = computed(() => {
  if (!dossier.value.critical_deadline) return false
  return new Date(dossier.value.critical_deadline) < new Date()
})

// Méthodes
const fetchDossierDetail = async () => {
  const id = route.params.id
  
  // Validation UUID basique
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
  if (!uuidRegex.test(id)) {
    error404.value = true
    loading.value = false
    return
  }

  loading.value = true
  error404.value = false

  try {
    // Charger le dossier
    const dossierRes = await api.get(`/dossiers/${id}/`)
    dossier.value = dossierRes.data

    // Charger folders et documents en parallèle
    await Promise.all([
      loadFolders(),
      loadDocuments()
    ])

  } catch (err) {
    console.error('Erreur chargement dossier:', err)
    if (err.response?.status === 404) {
      error404.value = true
    }
  } finally {
    loading.value = false
  }
}

const loadFolders = async () => {
  try {
    const response = await api.get('/documents/folders/', {
      params: { dossier: dossier.value.id }
    })
    folders.value = response.data || []
  } catch (err) {
    console.error('Erreur chargement folders:', err)
    folders.value = []
  }
}

const loadDocuments = async () => {
  loadingDocuments.value = true
  try {
    const params = {
      dossier: dossier.value.id,
      ordering: '-uploaded_at'
    }
    
    if (selectedFolderId.value.length) {
      params.folder = selectedFolderId.value[0]
    }

    const response = await api.get('/documents/documents/', { params })
    documents.value = response.data.results || response.data || []
  } catch (err) {
    console.error('Erreur chargement documents:', err)
    documents.value = []
  } finally {
    loadingDocuments.value = false
  }
}

const handleUploaded = (newDoc) => {
  documents.value.unshift(newDoc)
  showUploadDialog.value = false
}

const editDossier = () => {
  // TODO: Implémenter édition
  console.log('Éditer dossier')
}

const closeDossier = async () => {
  if (!confirm('Clôturer ce dossier ?')) return
  
  try {
    await api.patch(`/dossiers/${dossier.value.id}/`, { status: 'CLOTURE' })
    dossier.value.status = 'CLOTURE'
  } catch (err) {
    console.error('Erreur clôture:', err)
    alert('Erreur lors de la clôture')
  }
}

const deleteDossier = async () => {
  if (!confirm('Supprimer définitivement ce dossier ?')) return
  
  try {
    await api.delete(`/dossiers/${dossier.value.id}/`)
    router.push({ name: 'DossierList' })
  } catch (err) {
    console.error('Erreur suppression:', err)
    alert('Erreur lors de la suppression')
  }
}

// Utilitaires
const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  }).format(new Date(dateString))
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 octet'
  const k = 1024
  const sizes = ['octets', 'Ko', 'Mo', 'Go']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const getFileIcon = (ext) => {
  const icons = {
    pdf: 'mdi-file-pdf-box',
    doc: 'mdi-file-word',
    docx: 'mdi-file-word',
    xls: 'mdi-file-excel',
    xlsx: 'mdi-file-excel',
    jpg: 'mdi-file-image',
    jpeg: 'mdi-file-image',
    png: 'mdi-file-image'
  }
  return icons[ext?.toLowerCase()] || 'mdi-file'
}

const getFileIconColor = (ext) => {
  const colors = {
    pdf: 'red',
    doc: 'blue',
    docx: 'blue',
    xls: 'green',
    xlsx: 'green',
    jpg: 'orange',
    jpeg: 'orange',
    png: 'orange'
  }
  return colors[ext?.toLowerCase()] || 'grey'
}

const getStatusColor = (status) => {
  const colors = {
    OUVERT: 'success',
    ATTENTE: 'warning',
    SUSPENDU: 'orange',
    CLOTURE: 'grey',
    ARCHIVE: 'grey-darken-2'
  }
  return colors[status] || 'grey'
}

const getStatusLabel = (status) => {
  const labels = {
    OUVERT: 'Ouvert',
    ATTENTE: 'En attente',
    SUSPENDU: 'Suspendu',
    CLOTURE: 'Clôturé',
    ARCHIVE: 'Archivé'
  }
  return labels[status] || status
}

const getCategoryLabel = (category) => {
  const labels = {
    CONTENTIEUX: 'Contentieux',
    CONSEIL: 'Conseil',
    RECOUVREMENT: 'Recouvrement',
    TRAVAIL: 'Droit du travail',
    IMMOBILIER: 'Immobilier',
    SUCCESSION: 'Succession',
    MARIAGE: 'Mariage',
    DONATION: 'Donation',
    SOCIETE: 'Société',
    FAMILLE: 'Famille',
    COMMERCIAL: 'Commercial',
    AUTRE: 'Autre'
  }
  return labels[category] || category
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

// Watch changement dossier sélectionné
watch(selectedFolderId, () => {
  if (dossier.value.id) {
    loadDocuments()
  }
})

// Lifecycle
onMounted(async () => {
  await fetchDossierDetail()
})
</script>

<style scoped>
.gap-3 {
  gap: 12px;
}
</style>