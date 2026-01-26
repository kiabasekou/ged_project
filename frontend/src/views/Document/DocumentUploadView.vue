<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col cols="12">
        <!-- En-tête -->
        <div class="d-flex align-center mb-6">
          <v-btn
            icon
            variant="text"
            @click="$router.back()"
            class="mr-4"
          >
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
          <div>
            <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
              Ajouter un document
            </h1>
            <p class="text-subtitle-1 text-grey-darken-1 mt-1">
              Dossier : {{ dossier?.reference_code }} - {{ dossier?.title }}
            </p>
          </div>
        </div>

        <!-- Formulaire d'upload -->
        <v-card elevation="3" class="rounded-lg">
          <v-card-text class="pa-8">
            <v-form ref="uploadForm" @submit.prevent="handleUpload">
              <v-row>
                <!-- Zone de drop -->
                <v-col cols="12">
                  <div
                    class="drop-zone"
                    :class="{ 
                      'drop-zone-active': isDragging,
                      'drop-zone-error': errors.length > 0 
                    }"
                    @dragover.prevent="handleDragOver"
                    @dragleave.prevent="handleDragLeave"
                    @drop.prevent="handleDrop"
                  >
                    <v-file-input
                      v-model="selectedFile"
                      :loading="isUploading"
                      accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.txt"
                      prepend-icon="mdi-paperclip"
                      label="Sélectionnez un fichier ou glissez-le ici"
                      show-size
                      clearable
                      variant="outlined"
                      density="comfortable"
                      @change="handleFileSelect"
                      @click:clear="clearFile"
                    >
                      <template v-slot:prepend>
                        <v-icon color="indigo">mdi-cloud-upload</v-icon>
                      </template>
                    </v-file-input>

                    <!-- Aperçu image -->
                    <v-expand-transition>
                      <div v-if="imagePreview" class="mt-4">
                        <v-img
                          :src="imagePreview"
                          max-height="300"
                          contain
                          class="rounded border"
                        />
                      </div>
                    </v-expand-transition>

                    <!-- Info fichier -->
                    <v-expand-transition>
                      <v-alert
                        v-if="fileInfo"
                        type="info"
                        variant="tonal"
                        density="compact"
                        class="mt-4"
                      >
                        <div class="d-flex justify-space-between">
                          <span><strong>Type:</strong> {{ fileInfo.extension }}</span>
                          <span><strong>Taille:</strong> {{ fileInfo.sizeFormatted }}</span>
                        </div>
                      </v-alert>
                    </v-expand-transition>
                  </div>
                </v-col>

                <!-- Métadonnées -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.title"
                    label="Titre du document *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required, rules.maxLength(200)]"
                    counter="200"
                    prepend-inner-icon="mdi-format-title"
                  />
                </v-col>

                <v-col cols="12" md="6">
                  <v-select
                    v-model="form.sensitivity"
                    :items="sensitivityLevels"
                    label="Niveau de sensibilité *"
                    variant="outlined"
                    density="comfortable"
                    prepend-inner-icon="mdi-shield-lock"
                  />
                </v-col>

                <v-col cols="12">
                  <v-textarea
                    v-model="form.description"
                    label="Description / Notes"
                    variant="outlined"
                    density="comfortable"
                    rows="3"
                    :rules="[rules.maxLength(1000)]"
                    counter="1000"
                    prepend-inner-icon="mdi-text"
                  />
                </v-col>

                <!-- Dossier (optionnel) -->
                <v-col cols="12" md="6">
                  <v-select
                    v-model="form.folder"
                    :items="availableFolders"
                    item-title="name"
                    item-value="id"
                    label="Ranger dans un dossier (optionnel)"
                    variant="outlined"
                    density="comfortable"
                    clearable
                    prepend-inner-icon="mdi-folder"
                  />
                </v-col>

                <!-- Version (si modification) -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.version_notes"
                    label="Notes de version (optionnel)"
                    variant="outlined"
                    density="comfortable"
                    prepend-inner-icon="mdi-file-document-edit"
                  />
                </v-col>
              </v-row>

              <!-- Messages d'erreur -->
              <v-expand-transition>
                <v-alert
                  v-if="errors.length > 0"
                  type="error"
                  variant="tonal"
                  class="mt-4"
                >
                  <ul class="mb-0">
                    <li v-for="(error, i) in errors" :key="i">{{ error }}</li>
                  </ul>
                </v-alert>
              </v-expand-transition>

              <!-- Barre de progression -->
              <v-expand-transition>
                <div v-if="isUploading" class="mt-4">
                  <v-progress-linear
                    :model-value="uploadProgress"
                    color="indigo"
                    height="25"
                    striped
                  >
                    <template v-slot:default="{ value }">
                      <strong>{{ Math.ceil(value) }}%</strong>
                    </template>
                  </v-progress-linear>
                  <p class="text-center text-caption mt-2">
                    Chiffrement et upload en cours...
                  </p>
                </div>
              </v-expand-transition>

              <!-- Actions -->
              <div class="d-flex justify-end gap-3 mt-6">
                <v-btn
                  variant="outlined"
                  color="grey"
                  @click="$router.back()"
                  :disabled="isUploading"
                >
                  <v-icon start>mdi-close</v-icon>
                  Annuler
                </v-btn>
                <v-btn
                  type="submit"
                  color="indigo"
                  :loading="isUploading"
                  :disabled="!selectedFile || errors.length > 0"
                >
                  <v-icon start>mdi-upload</v-icon>
                  Uploader le document
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- Instructions -->
        <v-card elevation="1" class="mt-6 bg-blue-grey-lighten-5">
          <v-card-text>
            <h3 class="text-subtitle-1 font-weight-bold mb-2">
              <v-icon start color="info">mdi-information</v-icon>
              Formats acceptés
            </h3>
            <v-chip-group>
              <v-chip size="small" label>PDF</v-chip>
              <v-chip size="small" label>Word (.doc, .docx)</v-chip>
              <v-chip size="small" label>Excel (.xls, .xlsx)</v-chip>
              <v-chip size="small" label>Images (.jpg, .png)</v-chip>
              <v-chip size="small" label>Texte (.txt)</v-chip>
            </v-chip-group>
            <p class="text-caption mt-2 mb-0">
              <v-icon size="small" color="success">mdi-lock</v-icon>
              Tous les documents sont automatiquement chiffrés (AES-256) avant stockage.
            </p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDocumentStore } from '@/stores/document'
import { useDossierStore } from '@/stores/dossier'

const route = useRoute()
const router = useRouter()
const documentStore = useDocumentStore()
const dossierStore = useDossierStore()

// Données
const dossierId = route.params.dossierId || route.query.dossier
const dossier = ref(null)
const uploadForm = ref(null)
const selectedFile = ref(null)
const isDragging = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const imagePreview = ref(null)
const fileInfo = ref(null)
const errors = ref([])

const form = reactive({
  title: '',
  description: '',
  sensitivity: 'NORMAL',
  folder: null,
  version_notes: ''
})

// Options
const sensitivityLevels = [
  { title: 'Normal', value: 'NORMAL' },
  { title: 'Confidentiel', value: 'CONFIDENTIAL' },
  { title: 'Secret / Critique', value: 'CRITICAL' }
]

const availableFolders = ref([])

// Règles de validation
const rules = {
  required: v => !!v || 'Ce champ est requis',
  maxLength: max => v => !v || v.length <= max || `Maximum ${max} caractères`
}

// Méthodes
const handleFileSelect = async (file) => {
  if (!file) return

  errors.value = []
  
  // Validation taille (max 50MB)
  const maxSize = 50 * 1024 * 1024
  if (file.size > maxSize) {
    errors.value.push('Le fichier ne doit pas dépasser 50 Mo')
    selectedFile.value = null
    return
  }

  // Info fichier
  fileInfo.value = {
    name: file.name,
    size: file.size,
    sizeFormatted: formatFileSize(file.size),
    extension: file.name.split('.').pop().toUpperCase(),
    type: file.type
  }

  // Titre automatique (nom sans extension)
  if (!form.title) {
    form.title = file.name.replace(/\.[^/.]+$/, '')
  }

  // Aperçu image
  if (file.type.startsWith('image/')) {
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  } else {
    imagePreview.value = null
  }
}

const clearFile = () => {
  selectedFile.value = null
  imagePreview.value = null
  fileInfo.value = null
  errors.value = []
}

const handleDragOver = () => {
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

const handleDrop = (e) => {
  isDragging.value = false
  const files = e.dataTransfer.files
  if (files.length > 0) {
    selectedFile.value = files[0]
    handleFileSelect(files[0])
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 octet'
  const k = 1024
  const sizes = ['octets', 'Ko', 'Mo', 'Go']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const handleUpload = async () => {
  if (!uploadForm.value.validate() || !selectedFile.value) return

  isUploading.value = true
  uploadProgress.value = 0
  errors.value = []

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('dossier', dossierId)
    formData.append('title', form.title)
    formData.append('description', form.description)
    formData.append('sensitivity', form.sensitivity)
    
    if (form.folder) {
      formData.append('folder', form.folder)
    }
    
    if (form.version_notes) {
      formData.append('version_notes', form.version_notes)
    }

    // Upload avec progression
    await documentStore.uploadDocument(
      formData,
      (progressEvent) => {
        uploadProgress.value = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        )
      }
    )

    // Succès
    router.push({ 
      name: 'DossierDetail', 
      params: { id: dossierId },
      query: { tab: 'documents' }
    })
  } catch (error) {
    console.error('Erreur upload:', error)
    errors.value = [
      error.response?.data?.detail || 
      'Erreur lors de l\'upload du document'
    ]
  } finally {
    isUploading.value = false
  }
}

// Chargement initial
onMounted(async () => {
  if (dossierId) {
    dossier.value = await dossierStore.fetchDossier(dossierId)
    // Charger les dossiers disponibles
    availableFolders.value = await dossierStore.fetchFolders(dossierId)
  }
})
</script>

<style scoped>
.drop-zone {
  border: 2px dashed #ccc;
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
  background-color: #fafafa;
  cursor: pointer;
}

.drop-zone:hover {
  background-color: #f5f5f5;
  border-color: #1976d2;
}

.drop-zone-active {
  border-color: #1976d2;
  background-color: #e3f2fd;
  transform: scale(1.01);
}

.drop-zone-error {
  border-color: #f44336;
  background-color: #ffebee;
}

.gap-3 {
  gap: 12px;
}
</style>