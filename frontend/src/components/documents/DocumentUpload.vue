<template>
  <v-card elevation="2" class="document-upload-card rounded-lg">
    <!-- En-tête -->
    <v-card-title class="bg-indigo-darken-4 text-white d-flex align-center py-4">
      <v-icon start size="28">mdi-cloud-upload</v-icon>
      <span class="text-h6">Transmission de document</span>
    </v-card-title>

    <v-card-text class="pa-6">
      <v-form ref="uploadForm" v-model="formValid">
        <!-- Zone de drop -->
        <div
          :class="[
            'drop-zone',
            { 'drop-zone-active': isDragging },
            { 'drop-zone-error': hasError }
          ]"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
          @drop.prevent="handleDrop"
          @click="!selectedFile && $refs.fileInput.click()"
        >
          <!-- État : Aucun fichier -->
          <div v-if="!selectedFile && !validationState.isValidating" class="text-center py-8">
            <v-icon 
              size="80" 
              :color="isDragging ? 'indigo' : 'grey-lighten-1'"
              class="mb-4"
            >
              mdi-file-upload-outline
            </v-icon>
            <div class="text-h6 text-grey-darken-2 mb-2">
              {{ isDragging ? 'Déposez le fichier ici' : 'Glissez un document ici' }}
            </div>
            <div class="text-caption text-grey">
              ou cliquez pour parcourir vos fichiers
            </div>
            <div class="text-caption text-grey mt-2">
              {{ acceptedFormats }}
            </div>
          </div>

          <!-- État : Validation en cours -->
          <div v-else-if="validationState.isValidating" class="text-center py-8">
            <v-progress-circular
              indeterminate
              size="64"
              color="indigo"
              class="mb-4"
            />
            <div class="text-subtitle-1">Analyse du fichier...</div>
          </div>

          <!-- État : Fichier sélectionné -->
          <div v-else-if="selectedFile" class="py-4">
            <v-card variant="outlined" class="pa-4">
              <div class="d-flex align-center">
                <!-- Icône de fichier -->
                <v-avatar
                  size="60"
                  :color="getFileIconColor(fileInfo?.extension)"
                  class="mr-4"
                >
                  <v-icon size="32" color="white">
                    {{ getFileIcon(fileInfo?.extension) }}
                  </v-icon>
                </v-avatar>

                <!-- Infos fichier -->
                <div class="flex-grow-1">
                  <div class="text-subtitle-1 font-weight-bold text-truncate">
                    {{ selectedFile.name }}
                  </div>
                  <div class="text-caption text-grey">
                    {{ fileInfo?.sizeFormatted }} • {{ fileInfo?.extension?.toUpperCase() }}
                  </div>
                  
                  <!-- Métadonnées sécurité -->
                  <div class="d-flex gap-2 mt-2">
                    <v-chip
                      size="x-small"
                      :color="fileInfo?.isValid ? 'success' : 'error'"
                      variant="tonal"
                    >
                      <v-icon start size="14">
                        {{ fileInfo?.isValid ? 'mdi-check-circle' : 'mdi-alert-circle' }}
                      </v-icon>
                      {{ fileInfo?.isValid ? 'Valide' : 'Invalide' }}
                    </v-chip>
                    
                    <v-chip size="x-small" color="blue-grey" variant="tonal">
                      <v-icon start size="14">mdi-file-code</v-icon>
                      {{ fileInfo?.mimeType }}
                    </v-chip>
                  </div>
                </div>

                <!-- Bouton supprimer -->
                <v-btn
                  icon="mdi-close"
                  variant="text"
                  color="error"
                  size="small"
                  @click.stop="clearFile"
                />
              </div>

              <!-- Prévisualisation image -->
              <v-expand-transition>
                <div v-if="imagePreview" class="mt-4">
                  <v-img
                    :src="imagePreview"
                    max-height="200"
                    class="rounded"
                    cover
                  />
                </div>
              </v-expand-transition>
            </v-card>
          </div>

          <!-- Input file caché -->
          <input
            ref="fileInput"
            type="file"
            hidden
            :accept="acceptedFormats"
            @change="handleFileSelect($event.target.files[0])"
          />
        </div>

        <!-- Erreurs de validation -->
        <v-expand-transition>
          <v-alert
            v-if="validationState.errors.length > 0"
            type="error"
            variant="tonal"
            closable
            class="mt-4"
            @click:close="validationState.errors = []"
          >
            <div class="text-subtitle-2 font-weight-bold mb-2">
              ⚠️ Problèmes détectés :
            </div>
            <ul class="pl-4 mb-0">
              <li v-for="(error, index) in validationState.errors" :key="index" class="text-caption">
                {{ error }}
              </li>
            </ul>
          </v-alert>
        </v-expand-transition>

        <!-- Formulaire métadonnées -->
        <v-expand-transition>
          <div v-if="selectedFile && fileInfo?.isValid" class="mt-6">
            <v-divider class="mb-6" />
            
            <h3 class="text-h6 font-weight-bold mb-4 text-indigo-darken-4">
              Métadonnées du document
            </h3>

            <v-row>
              <!-- Titre -->
              <v-col cols="12">
                <v-text-field
                  v-model="form.title"
                  label="Titre du document *"
                  variant="outlined"
                  density="comfortable"
                  :rules="[rules.required, rules.maxLength(200)]"
                  counter="200"
                  prepend-inner-icon="mdi-format-title"
                  placeholder="Ex: Contrat de bail - Immeuble Akanda"
                  hint="Titre descriptif pour identifier le document"
                  persistent-hint
                />
              </v-col>

              <!-- Description -->
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
                  placeholder="Notes complémentaires, contexte, références..."
                />
              </v-col>

              <!-- Niveau de sensibilité -->
              <v-col cols="12" md="6">
                <v-select
                  v-model="form.sensitivity"
                  :items="sensitivityLevels"
                  label="Niveau de confidentialité *"
                  variant="outlined"
                  density="comfortable"
                  :rules="[rules.required]"
                  prepend-inner-icon="mdi-shield-lock"
                >
                  <template v-slot:item="{ item, props }">
                    <v-list-item v-bind="props">
                      <template v-slot:prepend>
                        <v-icon :color="item.raw.color">{{ item.raw.icon }}</v-icon>
                      </template>
                    </v-list-item>
                  </template>
                  
                  <template v-slot:selection="{ item }">
                    <v-icon :color="item.raw.color" start>{{ item.raw.icon }}</v-icon>
                    {{ item.title }}
                  </template>
                </v-select>
              </v-col>

              <!-- Dossier (optionnel) -->
              <v-col cols="12" md="6">
                <v-autocomplete
                  v-model="form.folder"
                  :items="availableFolders"
                  item-title="name"
                  item-value="id"
                  label="Ranger dans un dossier"
                  variant="outlined"
                  density="comfortable"
                  clearable
                  prepend-inner-icon="mdi-folder"
                  hint="Laisser vide pour la racine du dossier"
                  persistent-hint
                  no-data-text="Aucun sous-dossier disponible"
                />
              </v-col>
            </v-row>
          </div>
        </v-expand-transition>

        <!-- Barre de progression upload -->
        <v-expand-transition>
          <div v-if="isUploading" class="mt-6">
            <div class="d-flex align-center mb-2">
              <span class="text-subtitle-2 font-weight-bold">Envoi en cours...</span>
              <v-spacer />
              <span class="text-caption text-grey">{{ uploadProgress }}%</span>
            </div>
            <v-progress-linear
              :model-value="uploadProgress"
              height="8"
              color="indigo"
              striped
              rounded
            />
            <div class="text-caption text-grey mt-1 text-center">
              Transmission sécurisée vers le serveur du cabinet
            </div>
          </div>
        </v-expand-transition>
      </v-form>
    </v-card-text>

    <!-- Actions -->
    <v-card-actions class="px-6 pb-6">
      <v-spacer />
      <v-btn
        variant="text"
        @click="$emit('cancel')"
        :disabled="isUploading"
      >
        Annuler
      </v-btn>
      <v-btn
        color="indigo-darken-4"
        variant="elevated"
        prepend-icon="mdi-upload"
        :loading="isUploading"
        :disabled="!formValid || !selectedFile || !fileInfo?.isValid || validationState.errors.length > 0"
        @click="handleUpload"
      >
        Transmettre le document
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useDocumentStore } from '@/stores/document'

// Props & Emits
const props = defineProps({
  dossierId: {
    type: String,
    required: true
  },
  folderId: {
    type: String,
    default: null
  },
  availableFolders: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['success', 'cancel'])

// Store
const documentStore = useDocumentStore()

// Refs
const uploadForm = ref(null)
const fileInput = ref(null)
const selectedFile = ref(null)
const formValid = ref(false)
const isDragging = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const imagePreview = ref(null)
const fileInfo = ref(null)

// État de validation
const validationState = reactive({
  isValidating: false,
  errors: []
})

// Formulaire
const form = reactive({
  title: '',
  description: '',
  sensitivity: 'NORMAL',
  folder: props.folderId
})

// Configuration validation
const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50 MB
const ALLOWED_EXTENSIONS = [
  'pdf', 'doc', 'docx', 'xls', 'xlsx', 
  'jpg', 'jpeg', 'png', 'txt', 'odt', 'ods'
]
const ALLOWED_MIME_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'image/jpeg',
  'image/png',
  'text/plain',
  'application/vnd.oasis.opendocument.text',
  'application/vnd.oasis.opendocument.spreadsheet'
]

// Computed
const acceptedFormats = computed(() => 
  'PDF, Word, Excel, Images (JPG, PNG) - Max 50 MB'
)

const hasError = computed(() => validationState.errors.length > 0)

const sensitivityLevels = computed(() => [
  { 
    title: 'Normal', 
    value: 'NORMAL', 
    icon: 'mdi-shield-check-outline',
    color: 'green',
    description: 'Accessible à tous les collaborateurs du dossier'
  },
  { 
    title: 'Confidentiel', 
    value: 'CONFIDENTIAL', 
    icon: 'mdi-lock',
    color: 'orange',
    description: 'Réservé à l\'avocat responsable et secrétariat'
  },
  { 
    title: 'Secret professionnel', 
    value: 'CRITICAL', 
    icon: 'mdi-alert-decagram',
    color: 'red',
    description: 'Accès strictement limité à l\'avocat responsable'
  }
])

// Règles de validation
const rules = {
  required: v => !!v || 'Ce champ est requis',
  maxLength: max => v => !v || v.length <= max || `Maximum ${max} caractères`
}

// Méthodes de validation
const validateFile = async (file) => {
  validationState.isValidating = true
  validationState.errors = []
  
  try {
    // 1. Vérification taille
    if (file.size > MAX_FILE_SIZE) {
      validationState.errors.push(
        `Fichier trop volumineux : ${formatFileSize(file.size)} (max ${formatFileSize(MAX_FILE_SIZE)})`
      )
    }
    
    // 2. Vérification extension
    const extension = file.name.split('.').pop().toLowerCase()
    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      validationState.errors.push(
        `Extension non autorisée : .${extension}`
      )
    }
    
    // 3. Vérification type MIME
    if (!ALLOWED_MIME_TYPES.includes(file.type)) {
      validationState.errors.push(
        `Type de fichier non supporté : ${file.type}`
      )
    }
    
    // 4. Vérification nom fichier (caractères spéciaux)
    const invalidChars = /[<>:"/\\|?*\x00-\x1F]/g
    if (invalidChars.test(file.name)) {
      validationState.errors.push(
        'Le nom du fichier contient des caractères invalides'
      )
    }
    
    // 5. Construction des métadonnées
    fileInfo.value = {
      name: file.name,
      size: file.size,
      sizeFormatted: formatFileSize(file.size),
      extension: extension,
      mimeType: file.type,
      isValid: validationState.errors.length === 0,
      lastModified: new Date(file.lastModified).toLocaleString('fr-FR')
    }
    
    // 6. Prévisualisation pour les images
    if (file.type.startsWith('image/') && validationState.errors.length === 0) {
      await generateImagePreview(file)
    }
    
    // 7. Pré-remplir le titre
    if (validationState.errors.length === 0) {
      form.title = file.name.split('.').slice(0, -1).join('.')
    }
    
    return validationState.errors.length === 0
    
  } catch (error) {
    validationState.errors.push(`Erreur de validation: ${error.message}`)
    return false
  } finally {
    validationState.isValidating = false
  }
}

const generateImagePreview = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = (e) => {
      imagePreview.value = e.target.result
      resolve()
    }
    
    reader.onerror = () => {
      reject(new Error('Erreur lecture fichier'))
    }
    
    reader.readAsDataURL(file)
  })
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 octet'
  const k = 1024
  const sizes = ['octets', 'Ko', 'Mo', 'Go']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

// Gestion fichiers
const handleFileSelect = async (file) => {
  if (!file) return
  
  selectedFile.value = file
  await validateFile(file)
}

const clearFile = () => {
  selectedFile.value = null
  imagePreview.value = null
  fileInfo.value = null
  validationState.errors = []
  form.title = ''
  form.description = ''
  form.sensitivity = 'NORMAL'
  
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// Drag & Drop
const handleDragOver = () => {
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

const handleDrop = async (e) => {
  isDragging.value = false
  const files = e.dataTransfer.files
  
  if (files.length > 0) {
    await handleFileSelect(files[0])
  }
}

// Upload
const handleUpload = async () => {
  // Validation finale du formulaire
  const { valid } = await uploadForm.value.validate()
  if (!valid || !selectedFile.value) {
    return
  }
  
  isUploading.value = true
  uploadProgress.value = 0
  
  try {
    // Construction FormData
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('dossier', props.dossierId)
    formData.append('title', form.title)
    formData.append('description', form.description)
    formData.append('sensitivity', form.sensitivity)
    
    if (form.folder) {
      formData.append('folder', form.folder)
    }
    
    // Upload avec suivi progression
    const document = await documentStore.uploadDocument(
      formData,
      (progressEvent) => {
        uploadProgress.value = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        )
      }
    )
    
    // Succès
    emit('success', document)
    
    // Reset complet
    clearFile()
    if (uploadForm.value) {
      uploadForm.value.reset()
    }
    uploadProgress.value = 0
    
  } catch (error) {
    console.error('Erreur upload:', error)
    
    // Gestion erreurs backend
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error ||
                        'Erreur lors de la transmission du document'
    
    validationState.errors = [errorMessage]
    
    // Erreurs spécifiques
    if (error.response?.status === 413) {
      validationState.errors = ['Le fichier est trop volumineux pour le serveur']
    } else if (error.response?.status === 415) {
      validationState.errors = ['Type de fichier non supporté par le serveur']
    }
    
  } finally {
    isUploading.value = false
  }
}

// Utilitaires icônes
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
</script>

<style scoped>
.document-upload-card {
  max-width: 900px;
  margin: 0 auto;
}

.drop-zone {
  border: 3px dashed #e0e0e0;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background-color: #fafafa;
  cursor: pointer;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-zone:hover {
  background-color: #f5f5f5;
  border-color: #bdbdbd;
}

.drop-zone-active {
  border-color: #1A237E;
  background-color: #E8EAF6;
  transform: scale(1.02);
  box-shadow: 0 4px 20px rgba(26, 35, 126, 0.15);
}

.drop-zone-error {
  border-color: #f44336;
  background-color: #ffebee;
}

.gap-2 {
  gap: 8px;
}
</style>