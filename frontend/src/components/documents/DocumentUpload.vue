<template>
  <v-card class="document-upload-card" elevation="2">
    <v-card-title class="d-flex align-center">
      <v-icon left color="primary">mdi-file-upload</v-icon>
      Upload de Document
    </v-card-title>

    <v-card-text>
      <v-form ref="uploadForm" v-model="formValid" @submit.prevent="handleUpload">
        <!-- Zone de drop de fichier -->
        <v-sheet
          class="drop-zone"
          :class="{ 'drop-zone-active': isDragging, 'drop-zone-error': hasError }"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
          @drop.prevent="handleDrop"
          outlined
        >
          <v-file-input
            ref="fileInput"
            v-model="selectedFile"
            :accept="acceptedFormats"
            :rules="fileRules"
            :loading="validationState.isValidating"
            prepend-icon="mdi-paperclip"
            label="Sélectionnez un fichier ou glissez-le ici"
            show-size
            clearable
            @change="handleFileSelect"
            @click:clear="clearFile"
          >
            <template v-slot:selection="{ text }">
              <v-chip
                color="primary"
                label
                small
              >
                <v-icon left small>mdi-file-document</v-icon>
                {{ text }}
              </v-chip>
            </template>
          </v-file-input>

          <!-- Aperçu du fichier si image -->
          <v-expand-transition>
            <div v-if="imagePreview" class="mt-4">
              <v-img
                :src="imagePreview"
                max-height="200"
                contain
                class="rounded"
              />
            </div>
          </v-expand-transition>
        </v-sheet>

        <!-- Informations du fichier -->
        <v-expand-transition>
          <v-alert
            v-if="fileInfo"
            type="info"
            dense
            text
            class="mt-4"
          >
            <div class="d-flex justify-space-between">
              <span><strong>Nom:</strong> {{ fileInfo.name }}</span>
              <span><strong>Taille:</strong> {{ fileInfo.sizeFormatted }}</span>
              <span><strong>Type:</strong> {{ fileInfo.extension }}</span>
            </div>
          </v-alert>
        </v-expand-transition>

        <!-- Erreurs de validation -->
        <v-expand-transition>
          <v-alert
            v-if="validationState.errors.length > 0"
            type="error"
            dense
            dismissible
            class="mt-4"
          >
            <strong>Erreurs de validation:</strong>
            <ul class="mt-2">
              <li v-for="(error, index) in validationState.errors" :key="index">
                {{ error }}
              </li>
            </ul>
          </v-alert>
        </v-expand-transition>

        <v-divider class="my-4" />

        <!-- Formulaire de métadonnées -->
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="form.title"
              :rules="[rules.required, rules.maxLength(300)]"
              label="Titre du document *"
              prepend-icon="mdi-format-title"
              counter="300"
              required
            />
          </v-col>

          <v-col cols="12">
            <v-textarea
              v-model="form.description"
              label="Description (optionnel)"
              prepend-icon="mdi-text"
              rows="3"
              counter="1000"
              :rules="[rules.maxLength(1000)]"
            />
          </v-col>

          <v-col cols="12" md="6">
            <v-select
              v-model="form.sensitivity"
              :items="sensitivityLevels"
              :rules="[rules.required]"
              label="Niveau de sensibilité *"
              prepend-icon="mdi-shield-lock"
              required
            >
              <template v-slot:item="{ item }">
                <v-list-item-content>
                  <v-list-item-title>{{ item.text }}</v-list-item-title>
                  <v-list-item-subtitle>{{ item.description }}</v-list-item-subtitle>
                </v-list-item-content>
              </template>
            </v-select>
          </v-col>

          <v-col cols="12" md="6">
            <v-autocomplete
              v-model="form.folder"
              :items="availableFolders"
              item-text="full_path"
              item-value="id"
              label="Sous-dossier (optionnel)"
              prepend-icon="mdi-folder"
              clearable
            />
          </v-col>
        </v-row>

        <!-- Barre de progression -->
        <v-expand-transition>
          <div v-if="uploadProgress > 0 && uploadProgress < 100">
            <v-progress-linear
              :value="uploadProgress"
              color="primary"
              height="25"
              striped
            >
              <template v-slot:default>
                <strong>{{ Math.ceil(uploadProgress) }}%</strong>
              </template>
            </v-progress-linear>
          </div>
        </v-expand-transition>
      </v-form>
    </v-card-text>

    <v-card-actions>
      <v-spacer />
      <v-btn
        text
        @click="$emit('cancel')"
        :disabled="isUploading"
      >
        Annuler
      </v-btn>
      <v-btn
        color="primary"
        :loading="isUploading"
        :disabled="!formValid || !selectedFile || validationState.errors.length > 0"
        @click="handleUpload"
      >
        <v-icon left>mdi-upload</v-icon>
        Uploader
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { ref, reactive, computed, watch } from 'vue'
import { 
  FileValidator, 
  generateImagePreview, 
  ALLOWED_EXTENSIONS 
} from '@/utils/fileValidators'
import { useDocumentStore } from '@/stores/document'

export default {
  name: 'DocumentUpload',
  
  props: {
    dossierId: {
      type: String,
      required: true
    },
    folderId: {
      type: String,
      default: null
    }
  },

  emits: ['success', 'cancel'],

  setup(props, { emit }) {
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
      sensitivity: 'internal',
      folder: props.folderId
    })

    // Règles de validation
    const rules = {
      required: (v) => !!v || 'Ce champ est requis',
      maxLength: (max) => (v) => !v || v.length <= max || `Maximum ${max} caractères`
    }

    const fileRules = [
      (v) => !!v || 'Un fichier est requis',
      (v) => {
        if (!v) return true
        return validationState.errors.length === 0 || 'Fichier invalide'
      }
    ]

    // Computed
    const acceptedFormats = computed(() => ALLOWED_EXTENSIONS.join(','))

    const hasError = computed(() => validationState.errors.length > 0)

    const sensitivityLevels = [
      { 
        value: 'public', 
        text: 'Public',
        description: 'Accessible à tous'
      },
      { 
        value: 'internal', 
        text: 'Usage Interne',
        description: 'Réservé au cabinet'
      },
      { 
        value: 'confidential', 
        text: 'Confidentiel',
        description: 'Accès restreint'
      },
      { 
        value: 'secret', 
        text: 'Secret Professionnel',
        description: 'Haute confidentialité'
      }
    ]

    const availableFolders = computed(() => {
      // À implémenter: récupérer les folders du store
      return documentStore.getFoldersByDossier(props.dossierId) || []
    })

    // Méthodes
    const handleFileSelect = async (file) => {
      if (!file) {
        clearFile()
        return
      }

      selectedFile.value = file
      await validateFile(file)
    }

    const validateFile = async (file) => {
      validationState.isValidating = true
      validationState.errors = []
      imagePreview.value = null
      fileInfo.value = null

      try {
        const validator = new FileValidator(file)
        const result = await validator.validate()

        if (!result.valid) {
          validationState.errors = result.errors
          return false
        }

        // Récupérer les infos du fichier
        fileInfo.value = validator.getFileInfo()

        // Générer l'aperçu si image
        const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        if (imageExtensions.includes(fileInfo.value.extension)) {
          try {
            imagePreview.value = await generateImagePreview(file)
          } catch (error) {
            console.warn('Impossible de générer l\'aperçu:', error)
          }
        }

        // Pré-remplir le titre si vide
        if (!form.title) {
          form.title = file.name.substring(0, file.name.lastIndexOf('.'))
        }

        return true
      } catch (error) {
        validationState.errors.push(`Erreur de validation: ${error.message}`)
        return false
      } finally {
        validationState.isValidating = false
      }
    }

    const clearFile = () => {
      selectedFile.value = null
      imagePreview.value = null
      fileInfo.value = null
      validationState.errors = []
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
      if (!uploadForm.value.validate() || !selectedFile.value) {
        return
      }

      isUploading.value = true
      uploadProgress.value = 0

      try {
        const formData = new FormData()
        formData.append('file', selectedFile.value)
        formData.append('dossier', props.dossierId)
        formData.append('title', form.title)
        formData.append('description', form.description)
        formData.append('sensitivity', form.sensitivity)
        
        if (form.folder) {
          formData.append('folder', form.folder)
        }

        // Upload avec progression
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
        
        // Reset du formulaire
        clearFile()
        uploadForm.value.reset()
        uploadProgress.value = 0

      } catch (error) {
        console.error('Erreur upload:', error)
        validationState.errors = [
          error.response?.data?.detail || 
          'Erreur lors de l\'upload du document'
        ]
      } finally {
        isUploading.value = false
      }
    }

    return {
      // Refs
      uploadForm,
      fileInput,
      selectedFile,
      formValid,
      isDragging,
      isUploading,
      uploadProgress,
      imagePreview,
      fileInfo,
      validationState,
      form,
      
      // Computed
      acceptedFormats,
      hasError,
      sensitivityLevels,
      availableFolders,
      
      // Rules
      rules,
      fileRules,
      
      // Methods
      handleFileSelect,
      clearFile,
      handleDragOver,
      handleDragLeave,
      handleDrop,
      handleUpload
    }
  }
}
</script>

<style scoped>
.document-upload-card {
  max-width: 900px;
  margin: 0 auto;
}

.drop-zone {
  padding: 20px;
  border: 2px dashed #ccc;
  border-radius: 8px;
  transition: all 0.3s ease;
  background-color: #fafafa;
}

.drop-zone-active {
  border-color: #1976d2;
  background-color: #e3f2fd;
  transform: scale(1.02);
}

.drop-zone-error {
  border-color: #f44336;
  background-color: #ffebee;
}

.drop-zone:hover {
  background-color: #f5f5f5;
}
</style>
