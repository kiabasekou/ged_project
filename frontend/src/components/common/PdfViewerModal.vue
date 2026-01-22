<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as pdfjsLib from 'pdfjs-dist/build/pdf'
import pdfjsWorker from 'pdfjs-dist/build/pdf.worker.entry'

// Configuration PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  pdfUrl: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: 'Prévisualisation du document'
  }
})

const emit = defineEmits(['update:modelValue'])

const canvasRef = ref(null)
const loading = ref(true)
const error = ref('')
const numPages = ref(0)
const currentPage = ref(1)
const scale = ref(1.3)
const pdfDoc = ref(null)

const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

watch(isOpen, async (newVal) => {
  if (newVal && props.pdfUrl) {
    await loadPdf()
  } else {
    cleanup()
  }
})

const loadPdf = async () => {
  loading.value = true
  error.value = ''
  try {
    const loadingTask = pdfjsLib.getDocument({
      url: props.pdfUrl,
      cMapUrl: 'https://unpkg.com/pdfjs-dist@3.11.174/cmaps/',
      cMapPacked: true,
    })

    pdfDoc.value = await loadingTask.promise
    numPages.value = pdfDoc.value.numPages
    await renderPage(currentPage.value)
  } catch (err) {
    console.error('Erreur chargement PDF', err)
    error.value = 'Impossible de charger le document PDF.'
  } finally {
    loading.value = false
  }
}

const renderPage = async (pageNum) => {
  if (!pdfDoc.value || !canvasRef.value) return

  try {
    const page = await pdfDoc.value.getPage(pageNum)
    const viewport = page.getViewport({ scale: scale.value })

    const canvas = canvasRef.value
    const context = canvas.getContext('2d')
    canvas.height = viewport.height
    canvas.width = viewport.width

    const renderContext = {
      canvasContext: context,
      viewport: viewport
    }

    await page.render(renderContext).promise
  } catch (err) {
    console.error('Erreur rendu page', err)
  }
}

watch(currentPage, (newPage) => {
  if (newPage >= 1 && newPage <= numPages.value) {
    renderPage(newPage)
  }
})

watch(scale, () => {
  renderPage(currentPage.value)
})

const zoomIn = () => {
  scale.value = Math.min(scale.value + 0.2, 3)
}

const zoomOut = () => {
  scale.value = Math.max(scale.value - 0.2, 0.8)
}

const close = () => {
  isOpen.value = false
  cleanup()
}

const cleanup = () => {
  if (pdfDoc.value) {
    pdfDoc.value.destroy()
    pdfDoc.value = null
  }
  currentPage.value = 1
  scale.value = 1.3
}

onUnmounted(() => {
  cleanup()
})
</script>

<template>
  <v-dialog
    v-model="isOpen"
    fullscreen
    transition="dialog-bottom-transition"
    scrollable
  >
    <v-card class="d-flex flex-column">
      <!-- Toolbar -->
      <v-app-bar color="indigo-darken-4" dark elevation="4">
        <v-btn icon @click="close">
          <v-icon>mdi-close</v-icon>
        </v-btn>

        <v-toolbar-title class="text-h6 font-weight-bold">
          {{ title }}
        </v-toolbar-title>

        <v-spacer />

        <!-- Contrôles PDF -->
        <v-btn icon @click="zoomOut" :disabled="scale <= 0.8">
          <v-icon>mdi-magnify-minus-outline</v-icon>
        </v-btn>

        <span class="mx-3 text-white">
          {{ Math.round(scale * 100) }}%
        </span>

        <v-btn icon @click="zoomIn" :disabled="scale >= 3">
          <v-icon>mdi-magnify-plus-outline</v-icon>
        </v-btn>

        <v-divider vertical class="mx-4" color="amber" />

        <span class="text-caption mr-4">
          Page {{ currentPage }} / {{ numPages }}
        </span>

        <v-btn
          icon
          :disabled="currentPage <= 1"
          @click="currentPage--"
        >
          <v-icon>mdi-chevron-left</v-icon>
        </v-btn>

        <v-btn
          icon
          :disabled="currentPage >= numPages"
          @click="currentPage++"
        >
          <v-icon>mdi-chevron-right</v-icon>
        </v-btn>

        <v-divider vertical class="mx-4" color="amber" />

        <v-btn icon @click="window.print()">
          <v-icon>mdi-printer</v-icon>
        </v-btn>
      </v-app-bar>

      <!-- Contenu -->
      <v-card-text class="pa-0 flex-grow-1 bg-grey-lighten-3">
        <div class="d-flex justify-center align-center fill-height">
          <!-- Loading -->
          <div v-if="loading" class="text-center py-12">
            <v-progress-circular indeterminate size="80" color="indigo-darken-4" />
            <p class="mt-6 text-h6">Chargement du document...</p>
          </div>

          <!-- Erreur -->
          <v-alert v-else-if="error" type="error" class="mx-auto" width="500">
            {{ error }}
          </v-alert>

          <!-- PDF Canvas -->
          <div v-else class="pdf-container">
            <canvas ref="canvasRef" />
          </div>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.pdf-container {
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  background: white;
  max-width: 100%;
  overflow: auto;
}
</style>