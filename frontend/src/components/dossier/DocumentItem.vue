<script setup>
import { ref } from 'vue'
import PdfViewerModal from '@/components/common/PdfViewerModal.vue'

const props = defineProps({
  document: {
    type: Object,
    required: true
  }
})

// Déstructuration pour utiliser directement "document" dans le template
const { document } = props

const previewModal = ref(false)
const selectedDoc = ref(null)

const download = () => {
  if (document.file_url) {
    window.open(document.file_url, '_blank')
  }
}
</script>

<template>
  <v-list-item class="px-0" density="compact">
    <template v-slot:prepend>
      <v-icon
        size="40"
        color="indigo-darken-2"
        class="mr-4"
      >
        {{ document.file_extension === 'pdf' ? 'mdi-file-pdf-box' : 'mdi-file-document' }}
      </v-icon>
    </template>

    <v-list-item-title class="font-weight-medium">
      {{ document.title }}
      <span class="text-caption text-grey-darken-1 ml-2">v{{ document.version }}</span>
    </v-list-item-title>

    <v-list-item-subtitle>
      <div>{{ document.file_size_formatted || 'Taille inconnue' }}</div>
      <div>
        Par {{ document.uploaded_by_name || 'Inconnu' }}
        le {{ new Date(document.uploaded_at).toLocaleDateString('fr-FR') }}
      </div>
    </v-list-item-subtitle>

    <template v-slot:append>
      <v-btn
        icon
        size="small"
        color="indigo"
        @click.stop="download"
        title="Télécharger"
      >
        <v-icon>mdi-download</v-icon>
      </v-btn>

      <v-btn
        icon
        size="small"
        color="grey"
        title="Informations"
        class="ml-2"
      >
        <v-icon>mdi-information-outline</v-icon>
      </v-btn>

      <v-btn
        icon
        size="small"
        color="indigo"
        @click.stop="previewModal = true; selectedDoc = document"
        title="Prévisualiser"
      >
        <v-icon>mdi-eye-outline</v-icon>
      </v-btn>

      <PdfViewerModal
        v-model="previewModal"
        :pdf-url="selectedDoc?.file_url"
        :title="selectedDoc?.title"
      />
    </template>
  </v-list-item>
</template>