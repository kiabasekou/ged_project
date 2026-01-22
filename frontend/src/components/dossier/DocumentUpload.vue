<script setup>
import { ref } from 'vue'
import api from '@/plugins/axios'

const props = defineProps({
  dossierId: { type: [Number, String], required: true },
  folderId: { type: [Number, String], default: null }
})

const emit = defineEmits(['uploaded'])

// Refs pour le DOM et l'état
const fileInput = ref(null)
const dragOver = ref(false)
const uploading = ref(false)
const files = ref([])

// Options de sensibilité (Aligné sur le Backend)
const sensitivityOptions = [
  { title: 'Normal', value: 'NORMAL', icon: 'mdi-shield-check-outline' },
  { title: 'Confidentiel', value: 'CONFIDENTIAL', icon: 'mdi-lock' },
  { title: 'Secret/Critique', value: 'CRITICAL', icon: 'mdi-alert-decagram' }
]

const acceptedTypes = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.png', '.txt']

const addFiles = (fileList) => {
  const newFiles = Array.from(fileList).filter(file => {
    const ext = '.' + file.name.split('.').pop().toLowerCase()
    return acceptedTypes.includes(ext)
  })

  files.value = [...files.value, ...newFiles.map(file => ({
    file,
    name: file.name,
    size: formatFileSize(file.size),
    progress: 0,
    status: 'pending',
    sensitivity: 'NORMAL' // Valeur par défaut
  }))]
}

const uploadFiles = async () => {
  if (files.value.length === 0) return
  uploading.value = true

  for (const item of files.value.filter(f => f.status === 'pending')) {
    const formData = new FormData()
    formData.append('file', item.file)
    formData.append('title', item.file.name.split('.').slice(0, -1).join('.'))
    formData.append('dossier', props.dossierId)
    formData.append('sensitivity', item.sensitivity) // Ajout crucial
    if (props.folderId) formData.append('folder', props.folderId)

    try {
      item.status = 'uploading'
      const response = await api.post('/documents/documents/', formData, {
        onUploadProgress: (progressEvent) => {
          item.progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        }
      })
      item.status = 'success'
      emit('uploaded', response.data)
    } catch (err) {
      item.status = 'error'
      console.error('Erreur upload:', err)
    }
  }
  uploading.value = false
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 octet'
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + ['octets', 'Ko', 'Mo', 'Go'][i]
}

const removeFile = (index) => files.value.splice(index, 1)
const reset = () => files.value = []
</script>

<template>
  <v-card elevation="2" class="rounded-lg border-indigo">
    <v-card-title class="bg-indigo-darken-4 text-white d-flex align-center py-3">
      <v-icon start>mdi-cloud-upload</v-icon>
      Transmission de pièces
    </v-card-title>

    <v-card-text class="pa-4">
      <div
        class="drop-zone pa-8 text-center rounded-lg transition-swing"
        :class="{ 'drop-active': dragOver }"
        @dragover.prevent="dragOver = true"
        @dragleave.prevent="dragOver = false"
        @drop.prevent="dragOver = false; addFiles($event.dataTransfer.files)"
        @click="fileInput.click()"
      >
        <v-icon size="48" :color="dragOver ? 'indigo' : 'grey-lighten-1'">
          mdi-file-upload-outline
        </v-icon>
        <div class="text-h6 mt-2">Glisser les documents ici</div>
        <div class="text-caption">PDF, Word, Excel ou Images autorisés</div>
        <input ref="fileInput" type="file" multiple hidden @change="addFiles($event.target.files)" />
      </div>

      <v-list v-if="files.length > 0" class="mt-4 border rounded">
        <v-list-item v-for="(item, index) in files" :key="index" border="bottom">
          <template v-slot:prepend>
            <v-icon :color="item.status === 'success' ? 'success' : 'indigo'">
              {{ item.status === 'success' ? 'mdi-check-decagram' : 'mdi-file-document-outline' }}
            </v-icon>
          </template>

          <v-list-item-title class="font-weight-medium">{{ item.name }}</v-list-item-title>
          <v-list-item-subtitle>{{ item.size }}</v-list-item-subtitle>

          <template v-slot:append>
            <div class="d-flex align-center">
              <v-select
                v-if="item.status === 'pending'"
                v-model="item.sensitivity"
                :items="sensitivityOptions"
                density="compact"
                hide-details
                variant="outlined"
                class="mr-4 sensitivity-select"
                label="Confidentialité"
              ></v-select>
              
              <v-btn icon="mdi-close" variant="text" size="small" @click="removeFile(index)" :disabled="uploading"></v-btn>
            </div>
          </template>

          <v-progress-linear
            v-if="item.status === 'uploading' || item.status === 'success'"
            :model-value="item.progress"
            :color="item.status === 'success' ? 'success' : 'indigo'"
            height="4"
            absolute
            bottom
          ></v-progress-linear>
        </v-list-item>
      </v-list>
    </v-card-text>

    <v-divider></v-divider>

    <v-card-actions class="pa-4">
      <v-btn variant="text" @click="reset" :disabled="uploading">Vider la liste</v-btn>
      <v-spacer></v-spacer>
      <v-btn
        color="indigo-darken-4"
        variant="elevated"
        :loading="uploading"
        :disabled="files.length === 0"
        @click="uploadFiles"
      >
        Lancer l'upload ({{ files.length }})
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped>
.drop-zone {
  border: 2px dashed #e0e0e0;
  cursor: pointer;
  transition: all 0.3s ease;
}
.drop-active {
  border-color: #1A237E;
  background-color: #F5F5F5;
  transform: scale(1.02);
}
.sensitivity-select {
  width: 180px;
}
</style>