<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/plugins/axios'
import { useAuthStore } from '@/stores/auth'
import DocumentUpload from '@/components/dossier/DocumentUpload.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// États réactifs
const dossier = ref({ status: 'OUVERT', title: '' })
const folders = ref([])
const documents = ref([])
const selectedFolderId = ref([]) // Vuetify 3 utilise un tableau pour la sélection
const loading = ref(true)
const tab = ref('info')

// Déterminer si nous sommes en mode création
const isCreateMode = computed(() => route.params.id === 'create')

// Récupérer le dossier sélectionné à partir de son ID
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
    loading.value = false // On arrête le chargement immédiatement en mode création
  }
})

const fetchDossierDetail = async () => {
  const id = route.params.id
  if (!id || id === 'create') return // Sécurité supplémentaire

  loading.value = true
  try {
    // Appels parallèles optimisés
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

// Rafraîchir les documents quand on change de dossier dans l'arbre
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

const handleUploaded = (newDoc) => {
  // On ajoute le nouveau document en haut de la liste localement
  documents.value.unshift(newDoc)
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
  // Utilisation de l'endpoint download sécurisé que nous avons créé au Backend
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

      <v-btn color="indigo-darken-4" variant="outlined" prepend-icon="mdi-arrow-left" @click="router.push('/dossiers')">
        Retour à la liste
      </v-btn>
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
              </v-list>
            </v-card>
          </v-col>

          <v-col cols="12" md="8">
            <DocumentUpload
              v-if="!isCreateMode"
              :dossier-id="dossier.id"
              :folder-id="selectedFolder?.id || null"
              @uploaded="handleUploaded"
              class="mb-6"
            />

            <v-data-table
              :headers="[
                { title: 'Document', key: 'title' },
                { title: 'Taille', key: 'file_size_formatted' },
                { title: 'Date', key: 'uploaded_at' },
                { title: 'Actions', key: 'actions', align: 'end' }
              ]"
              :items="documents"
              class="border rounded"
            >
              <template v-slot:item.uploaded_at="{ value }">
                {{ new Date(value).toLocaleDateString('fr-GA') }}
              </template>
              <template v-slot:item.actions="{ item }">
                <v-btn icon="mdi-download" variant="text" color="indigo" @click="downloadDocument(item)"></v-btn>
              </template>
            </v-data-table>
          </v-col>
        </v-row>
      </v-window-item>
    </v-window>
  </div>
</template>