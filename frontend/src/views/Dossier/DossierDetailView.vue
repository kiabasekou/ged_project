<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/plugins/axios'
import { useAuthStore } from '@/stores/auth'
import DocumentUpload from '@/components/dossier/DocumentUpload.vue' // Assurez-vous que le chemin est bon

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// États réactifs
const dossier = ref({ status: 'OUVERT', title: '' })
const folders = ref([])
const documents = ref([])
const selectedFolderId = ref([]) 
const loading = ref(true)
const tab = ref('info')
const showUploadDialog = ref(false) // <--- NOUVEAU : Contrôle la modale

// Déterminer si nous sommes en mode création
const isCreateMode = computed(() => route.params.id === 'create')

// Récupérer le dossier sélectionné (Computed)
const selectedFolder = computed(() => {
  if (!selectedFolderId.value.length) return null
  const findFolder = (list, id) => {
    for (const f of list) {
      if (f.id === id) return f
      if (f.subfolders) {
        const found = findFolder(f.subfolders, id)
        if (found) return found
      }
    }
    return null
  }
  return findFolder(folders.value, selectedFolderId.value[0])
})

onMounted(async () => {
  if (!isCreateMode.value) {
    await fetchDossierDetail()
  } else {
    loading.value = false
  }
})

const fetchDossierDetail = async () => {
  const id = route.params.id
  if (!id || id === 'create') return

  loading.value = true
  try {
    const [dossierRes, foldersRes, docsRes] = await Promise.all([
      api.get(`/dossiers/${id}/`),
      api.get(`/documents/folders/`, { params: { dossier: id } }),
      api.get('/documents/documents/', { params: { dossier: id, ordering: '-uploaded_at' } })
    ])

    dossier.value = dossierRes.data
    folders.value = foldersRes.data
    documents.value = docsRes.data.results || docsRes.data
  } catch (err) {
    console.error('Erreur chargement dossier:', err)
    if (err.response?.status === 404) router.push('/dossiers')
  } finally {
    loading.value = false
  }
}

// Rafraîchir les documents quand on change de dossier
watch(selectedFolderId, async (newId) => {
  if (isCreateMode.value) return
  
  const params = {
    dossier: route.params.id,
    ordering: '-uploaded_at'
  }
  if (newId.length) params.folder = newId[0]

  try {
    const res = await api.get('/documents/documents/', { params })
    documents.value = res.data.results || res.data
  } catch (err) {
    console.error('Erreur filtrage documents:', err)
  }
})

// Callback après upload réussi
const handleUploaded = (newDoc) => {
  // 1. Ajouter le document à la liste
  documents.value.unshift(newDoc)
  // 2. Fermer la modale
  showUploadDialog.value = false
  // 3. Basculer vers l'onglet documents si on n'y est pas
  tab.value = 'documents'
}

const isOverdue = computed(() => {
  if (!dossier.value.critical_deadline) return false
  return new Date(dossier.value.critical_deadline) < new Date()
})

const getStatusColor = (status) => {
  const colors = { OUVERT: 'indigo', ATTENTE: 'orange', CLOTURE: 'green', ARCHIVE: 'grey-darken-2' }
  return colors[status] || 'blue-grey'
}

const downloadDocument = async (doc) => {
  try {
    window.open(`${api.defaults.baseURL}/documents/documents/${doc.id}/download/`, '_blank')
  } catch (err) {
    console.error('Erreur téléchargement:', err)
  }
}
</script>

<template>
  <div v-if="loading" class="text-center my-12">
    <v-progress-circular indeterminate size="80" color="indigo-darken-4" />
    <p class="mt-4 text-h6">Préparation du dossier...</p>
  </div>

  <div v-else>
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
          <v-icon class="mr-2">mdi-folder-account</v-icon>
          {{ isCreateMode ? 'Nouveau Dossier' : `${dossier.reference_code} — ${dossier.title}` }}
        </h1>
        <div class="mt-2" v-if="!isCreateMode">
          <v-chip :color="getStatusColor(dossier.status)" class="mr-3" label>
            {{ dossier.status }}
          </v-chip>
          <v-chip v-if="isOverdue" color="red" label>
            <v-icon start>mdi-alert</v-icon>
            Délai dépassé
          </v-chip>
        </div>
      </div>

      <div class="d-flex gap-2">
        <v-btn 
            color="indigo-darken-4" 
            variant="outlined" 
            prepend-icon="mdi-arrow-left" 
            @click="router.push('/dossiers')"
            class="mr-2"
        >
            Retour
        </v-btn>
        
        <v-btn
          color="indigo"
          prepend-icon="mdi-file-plus"
          @click="showUploadDialog = true"
          :disabled="isCreateMode"
        >
          Ajouter un document
        </v-btn>
      </div>
    </div>

    <v-tabs v-model="tab" color="indigo-darken-4" align-tabs="start">
      <v-tab value="info">Informations</v-tab>
      <v-tab value="documents" :disabled="isCreateMode">
        Documents
        <v-chip size="x-small" class="ml-2" color="indigo">{{ documents.length }}</v-chip>
      </v-tab>
    </v-tabs>

    <v-window v-model="tab" class="mt-6">
      <v-window-item value="info">
        <v-row>
          <v-col cols="12" md="8">
            <v-card border>
              <v-card-title>Détails juridiques</v-card-title>
              <v-card-text>
                <p v-if="isCreateMode" class="text-grey">Veuillez d'abord enregistrer le dossier pour gérer les documents.</p>
                <div v-else>
                   <p><strong>Description :</strong> {{ dossier.description || 'Aucune description' }}</p>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

      <v-window-item value="documents">
        <v-row>
          <v-col cols="12" md="4">
            <v-card border height="100%">
              <v-list v-model:opened="selectedFolderId" select-strategy="single-leaf" mandatory>
                <v-list-subheader class="bg-indigo-lighten-5 text-indigo-darken-4 font-weight-bold">
                  STRUCTURE DU DOSSIER
                </v-list-subheader>
                
                <v-list-item
                  v-for="folder in folders"
                  :key="folder.id"
                  :value="folder.id"
                  @click="selectedFolderId = [folder.id]"
                  :prepend-icon="selectedFolderId.includes(folder.id) ? 'mdi-folder-open' : 'mdi-folder'"
                  :title="folder.name"
                  :active="selectedFolderId.includes(folder.id)"
                ></v-list-item>
                
                <v-list-item v-if="folders.length === 0" class="text-grey text-center font-italic">
                    Dossier racine
                </v-list-item>
              </v-list>
            </v-card>
          </v-col>

          <v-col cols="12" md="8">
            <v-data-table
              :headers="[
                { title: 'Document', key: 'title' },
                { title: 'Taille', key: 'file_size_formatted' },
                { title: 'Date', key: 'uploaded_at' },
                { title: 'Actions', key: 'actions', align: 'end' }
              ]"
              :items="documents"
              class="border rounded"
              hover
            >
              <template v-slot:item.uploaded_at="{ value }">
                {{ new Date(value).toLocaleDateString('fr-GA') }}
              </template>
              <template v-slot:item.actions="{ item }">
                <v-btn icon="mdi-download" variant="text" size="small" color="indigo" @click="downloadDocument(item)"></v-btn>
              </template>
              <template v-slot:no-data>
                <div class="text-center py-4">
                    <v-icon size="40" color="grey-lighten-2">mdi-file-hidden</v-icon>
                    <p class="text-grey mt-2">Aucun document dans ce répertoire</p>
                </div>
              </template>
            </v-data-table>
          </v-col>
        </v-row>
      </v-window-item>
    </v-window>

    <v-dialog v-model="showUploadDialog" max-width="600px">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center bg-indigo text-white">
            <span>Uploader un document</span>
            <v-btn icon="mdi-close" variant="text" @click="showUploadDialog = false"></v-btn>
        </v-card-title>
        <v-btn 
          :to="{ name: 'EventCreate', query: { dossier_id: dossier.id } }"
          prepend-icon="mdi-calendar-plus"
        >
          Ajouter au calendrier
        </v-btn>
        
        <v-card-text class="pt-4">
            <v-alert v-if="selectedFolder" type="info" variant="tonal" density="compact" class="mb-4">
                Destination : <strong>{{ selectedFolder.name }}</strong>
            </v-alert>
            <v-alert v-else type="warning" variant="tonal" density="compact" class="mb-4">
                Destination : <strong>Racine du dossier</strong>
            </v-alert>

            <DocumentUpload
                v-if="!isCreateMode"
                :dossier-id="dossier.id"
                :folder-id="selectedFolder?.id || null"
                @uploaded="handleUploaded"
            />
        </v-card-text>
      </v-card>
    </v-dialog>

  </div>
</template>