<template>
  <v-container fluid class="pa-6">
    <v-row v-if="loading">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate color="indigo" size="64" />
      </v-col>
    </v-row>

    <template v-else-if="document">
      <!-- En-tête -->
      <v-row class="mb-6">
        <v-col cols="12">
          <div class="d-flex align-center mb-4">
            <v-btn
              icon
              variant="text"
              @click="$router.back()"
              class="mr-4"
            >
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
            <div class="flex-grow-1">
              <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
                {{ document.title }}
              </h1>
              <div class="d-flex align-center gap-2 mt-2">
                <v-chip size="small" variant="outlined">
                  {{ document.original_filename }}
                </v-chip>
                <v-chip
                  size="small"
                  :color="getSensitivityColor(document.sensitivity)"
                  variant="tonal"
                >
                  <v-icon start size="small">
                    {{ getSensitivityIcon(document.sensitivity) }}
                  </v-icon>
                  {{ getSensitivityLabel(document.sensitivity) }}
                </v-chip>
                <v-chip size="small" variant="tonal">
                  Version {{ document.version }}
                </v-chip>
              </div>
            </div>

            <!-- Actions principales -->
            <div class="d-flex gap-2">
              <v-btn
                color="indigo"
                prepend-icon="mdi-download"
                @click="downloadDocument"
              >
                Télécharger
              </v-btn>
              <v-menu>
                <template v-slot:activator="{ props }">
                  <v-btn
                    icon="mdi-dots-vertical"
                    variant="text"
                    v-bind="props"
                  />
                </template>
                <v-list density="compact">
                  <v-list-item
                    prepend-icon="mdi-file-upload"
                    @click="uploadNewVersion"
                  >
                    Nouvelle version
                  </v-list-item>
                  <v-list-item
                    prepend-icon="mdi-pencil"
                    @click="editDocument"
                  >
                    Modifier les métadonnées
                  </v-list-item>
                  <v-divider />
                  <v-list-item
                    prepend-icon="mdi-delete"
                    class="text-error"
                    @click="confirmDelete"
                  >
                    Supprimer
                  </v-list-item>
                </v-list>
              </v-menu>
            </div>
          </div>
        </v-col>
      </v-row>

      <!-- Contenu principal -->
      <v-row>
        <!-- Colonne gauche - Aperçu -->
        <v-col cols="12" md="8">
          <!-- Prévisualisation -->
          <v-card elevation="2" class="mb-6">
            <v-card-title class="bg-grey-lighten-4">
              <v-icon start>mdi-file-eye</v-icon>
              Aperçu
            </v-card-title>
            <v-card-text class="pa-8">
              <div class="document-preview-large">
                <v-icon size="128" :color="getFileIconColor(document.file_extension)">
                  {{ getFileIcon(document.file_extension) }}
                </v-icon>
                <div class="mt-4 text-center">
                  <div class="text-h6">{{ document.file_extension?.toUpperCase() }}</div>
                  <div class="text-caption text-grey">{{ document.file_size_human }}</div>
                </div>
              </div>
            </v-card-text>
          </v-card>

          <!-- Description -->
          <v-card elevation="2" class="mb-6" v-if="document.description">
            <v-card-title class="bg-grey-lighten-4">
              <v-icon start>mdi-text</v-icon>
              Description
            </v-card-title>
            <v-card-text class="pa-6">
              <p class="text-body-1">{{ document.description }}</p>
            </v-card-text>
          </v-card>

          <!-- Historique des versions -->
          <v-card elevation="2">
            <v-card-title class="bg-grey-lighten-4">
              <v-icon start>mdi-history</v-icon>
              Historique des versions ({{ versions.length }})
              <v-spacer />
              <v-btn
                variant="text"
                size="small"
                prepend-icon="mdi-refresh"
                @click="loadVersionHistory"
                :loading="loadingVersions"
              >
                Actualiser
              </v-btn>
            </v-card-title>
            <v-card-text class="pa-0">
              <v-list>
                <v-list-item
                  v-for="version in versions"
                  :key="version.id"
                  :class="{ 'bg-blue-lighten-5': version.id === document.id }"
                >
                  <template v-slot:prepend>
                    <v-avatar :color="version.id === document.id ? 'indigo' : 'grey-lighten-2'">
                      <span class="text-caption font-weight-bold">
                        v{{ version.version }}
                      </span>
                    </v-avatar>
                  </template>

                  <v-list-item-title>
                    <span class="font-weight-medium">
                      Version {{ version.version }}
                    </span>
                    <v-chip
                      v-if="version.id === document.id"
                      size="x-small"
                      color="success"
                      variant="tonal"
                      class="ml-2"
                    >
                      Actuelle
                    </v-chip>
                  </v-list-item-title>

                  <v-list-item-subtitle>
                    {{ formatDate(version.uploaded_at) }} par {{ version.uploaded_by_name }}
                  </v-list-item-subtitle>

                  <template v-slot:append>
                    <div class="d-flex gap-1">
                      <v-chip size="x-small" variant="outlined">
                        {{ version.file_size_human }}
                      </v-chip>
                      <v-btn
                        icon="mdi-download"
                        size="small"
                        variant="text"
                        @click="downloadVersion(version)"
                      />
                    </div>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Colonne droite - Informations -->
        <v-col cols="12" md="4">
          <!-- Informations générales -->
          <v-card elevation="2" class="mb-6">
            <v-card-title class="bg-grey-lighten-4">
              <v-icon start>mdi-information</v-icon>
              Informations
            </v-card-title>
            <v-card-text class="pa-0">
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title class="text-caption text-grey">
                    Dossier lié
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip
                      size="small"
                      variant="outlined"
                      :to="{ name: 'DossierDetail', params: { id: document.dossier } }"
                    >
                      Voir le dossier
                    </v-chip>
                  </v-list-item-subtitle>
                </v-list-item>

                <v-divider />

                <v-list-item v-if="document.folder_path">
                  <v-list-item-title class="text-caption text-grey">
                    Dossier (arborescence)
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    <v-icon size="small">mdi-folder</v-icon>
                    {{ document.folder_path }}
                  </v-list-item-subtitle>
                </v-list-item>

                <v-divider />

                <v-list-item>
                  <v-list-item-title class="text-caption text-grey">
                    Type MIME
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ document.mime_type }}
                  </v-list-item-subtitle>
                </v-list-item>

                <v-divider />

                <v-list-item>
                  <v-list-item-title class="text-caption text-grey">
                    Taille du fichier
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ document.file_size_human }} ({{ document.file_size.toLocaleString() }} octets)
                  </v-list-item-subtitle>
                </v-list-item>

                <v-divider />

                <v-list-item>
                  <v-list-item-title class="text-caption text-grey">
                    Hash SHA-256
                  </v-list-item-title>
                  <v-list-item-subtitle class="text-caption font-mono">
                    {{ document.file_hash?.substring(0, 16) }}...
                    <v-btn
                      icon="mdi-content-copy"
                      size="x-small"
                      variant="text"
                      @click="copyToClipboard(document.file_hash)"
                    />
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

          <!-- Sécurité -->
          <v-card elevation="2" class="mb-6">
            <v-card-title class="bg-grey-lighten-4">
              <v-icon start>mdi-shield-lock</v-icon>
              Sécurité
            </v-card-title>
            <v-card-text class="pa-4">
              <v-alert
                :type="document.integrity_verified ? 'success' : 'warning'"
                variant="tonal"
                density="compact"
                class="mb-3"
              >
                <template v-slot:prepend>
                  <v-icon>
                    {{ document.integrity_verified ? 'mdi-check-circle' : 'mdi-alert' }}
                  </v-icon>
                </template>
                <div class="text-caption">
                  {{ document.integrity_verified ? 'Intégrité vérifiée' : 'Vérification requise' }}
                </div>
              </v-alert>

              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title class="text-caption">
                    <v-icon size="small" color="success">mdi-lock</v-icon>
                    Chiffrement AES-256
                  </v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title class="text-caption">
                    <v-icon size="small" color="success">mdi-shield-check</v-icon>
                    Stockage immutable
                  </v-list-item-title>
                </v-list-item>
                <v-list-item v-if="document.retention_until">
                  <v-list-item-title class="text-caption">
                    <v-icon size="small">mdi-calendar-clock</v-icon>
                    Conservation jusqu'au {{ formatDate(document.retention_until) }}
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

          <!-- Métadonnées -->
          <v-card elevation="2">
            <v-card-title class="bg-grey-lighten-4">
              <v-icon start>mdi-clock-outline</v-icon>
              Métadonnées
            </v-card-title>
            <v-card-text class="pa-0">
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title class="text-caption text-grey">
                    Uploadé le
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ formatDate(document.uploaded_at) }}
                  </v-list-item-subtitle>
                </v-list-item>

                <v-divider />

                <v-list-item>
                  <v-list-item-title class="text-caption text-grey">
                    Par
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ document.uploaded_by_name }}
                  </v-list-item-subtitle>
                </v-list-item>

                <v-divider />

                <v-list-item v-if="document.updated_at !== document.uploaded_at">
                  <v-list-item-title class="text-caption text-grey">
                    Dernière modification
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ formatDate(document.updated_at) }}
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDocumentStore } from '@/stores/document'

const route = useRoute()
const router = useRouter()
const documentStore = useDocumentStore()

// État
const loading = ref(true)
const loadingVersions = ref(false)
const document = ref(null)
const versions = ref([])

// Méthodes
const loadDocument = async () => {
  loading.value = true
  try {
    document.value = await documentStore.fetchDocument(route.params.id)
    await loadVersionHistory()
  } catch (error) {
    console.error('Erreur chargement document:', error)
    router.push({ name: 'DocumentList' })
  } finally {
    loading.value = false
  }
}

const loadVersionHistory = async () => {
  loadingVersions.value = true
  try {
    const response = await documentStore.fetchVersionHistory(route.params.id)
    versions.value = response.history || []
  } catch (error) {
    console.error('Erreur chargement versions:', error)
  } finally {
    loadingVersions.value = false
  }
}

const downloadDocument = () => {
  const url = `${import.meta.env.VITE_API_BASE_URL}/documents/documents/${document.value.id}/download/`
  window.open(url, '_blank')
}

const downloadVersion = (version) => {
  const url = `${import.meta.env.VITE_API_BASE_URL}/documents/documents/${version.id}/download/`
  window.open(url, '_blank')
}

const uploadNewVersion = () => {
  // TODO: Ouvrir dialog upload nouvelle version
  console.log('Upload nouvelle version')
}

const editDocument = () => {
  // TODO: Ouvrir dialog édition métadonnées
  console.log('Édition métadonnées')
}

const confirmDelete = () => {
  // TODO: Confirmation et suppression
  console.log('Suppression document')
}

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text)
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
    png: 'mdi-file-image'
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
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Chargement initial
onMounted(() => {
  loadDocument()
})
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}

.document-preview-large {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
}

.document-preview-large v-icon {
  color: white;
}

.font-mono {
  font-family: 'Courier New', monospace;
}
</style>