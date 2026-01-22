<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useClientStore } from '@/stores/client'
import api from '@/plugins/axios'

const route = useRoute()
const router = useRouter()
const clientStore = useClientStore()

// On initialise à null pour éviter que le template ne lise des propriétés d'un objet vide
const client = ref(null)
const dossiers = ref([])
const loading = ref(true)
const actionLoading = ref(false)

onMounted(async () => {
  await loadClientDetail()
})

const loadClientDetail = async () => {
  const id = route.params.id
  
  // GARDE-FOU : Empêche l'appel API si l'ID est invalide
  if (!id || id === 'undefined' || id === 'create') {
    loading.value = false
    // Si c'est "undefined", on redirige car c'est une erreur de navigation
    if (id === 'undefined') router.push('/clients')
    return
  }

  loading.value = true
  try {
    // 1. Récupération via le store (qui est maintenant protégé)
    await clientStore.fetchDetail(id)
    client.value = clientStore.current

    // 2. Chargement des dossiers associés
    // On ne le fait que si le client a été trouvé
    if (client.value) {
      const res = await api.get('/dossiers/', { params: { client: id } })
      dossiers.value = res.data.results || res.data
    }
  } catch (err) {
    console.error('Erreur chargement client', err)
    // Optionnel : redirection si 404
    if (err.response?.status === 404) router.push('/clients')
  } finally {
    loading.value = false
  }
}

const grantConsent = async () => {
  if (!client.value?.id) return
  
  actionLoading.value = true
  try {
    await clientStore.grantConsent(client.value.id)
    // On met à jour l'état local pour un feedback immédiat
    client.value.consent_given = true
  } catch (err) {
    console.error('Erreur consentement', err)
  } finally {
    actionLoading.value = false
  }
}

// Helper pour le nom d'affichage
const clientDisplayName = computed(() => {
  if (!client.value) return 'Client'
  return client.value.display_name || `${client.value.last_name} ${client.value.first_name}`
})
</script>

<template>
  <div v-if="loading" class="text-center my-12">
    <v-progress-circular indeterminate size="80" color="indigo-darken-4" />
    <p class="mt-4 text-grey">Chargement des données du cabinet...</p>
  </div>

  <div v-else-if="client">
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
          {{ clientDisplayName }}
        </h1>
        <v-chip 
          :color="client.client_type === 'PHYSIQUE' ? 'blue' : 'amber-darken-2'" 
          class="mt-2"
          label
        >
          <v-icon start>
            {{ client.client_type === 'PHYSIQUE' ? 'mdi-account' : 'mdi-domain' }}
          </v-icon>
          {{ client.client_type === 'PHYSIQUE' ? 'Personne physique' : 'Personne morale' }}
        </v-chip>
      </div>
      <v-btn
        color="indigo-darken-4"
        variant="outlined"
        prepend-icon="mdi-arrow-left"
        @click="router.push('/clients')"
      >
        Retour à la liste
      </v-btn>
    </div>

    <v-row>
      <v-col cols="12" md="6">
        <v-card elevation="2" border>
          <v-card-title class="bg-indigo-darken-4 text-white py-3">
            Fiche d'identité
          </v-card-title>
          <v-card-text class="pt-6">
            <div class="mb-4">
              <span class="text-caption text-grey">Coordonnées</span>
              <p class="text-body-1"><v-icon size="small" class="mr-2">mdi-email</v-icon> {{ client.email || 'Non renseigné' }}</p>
              <p class="text-body-1"><v-icon size="small" class="mr-2">mdi-phone</v-icon> {{ client.phone_primary || 'Non renseigné' }}</p>
            </div>
            
            <v-divider class="mb-4"></v-divider>

            <div class="mb-4">
              <span class="text-caption text-grey">Identification Légale</span>
              <p v-if="client.nif"><strong>NIF :</strong> {{ client.nif }}</p>
              <p v-if="client.rccm"><strong>RCCM :</strong> {{ client.rccm }}</p>
              <p><strong>Adresse :</strong> {{ client.full_address || 'Libreville, Gabon' }}</p>
            </div>

            <v-alert
              v-if="!client.consent_given"
              type="warning"
              variant="tonal"
              density="compact"
              class="mt-4"
            >
              Consentement RGPD manquant
              <template v-slot:append>
                <v-btn 
                  size="small" 
                  color="warning" 
                  :loading="actionLoading" 
                  @click="grantConsent"
                >
                  Régulariser
                </v-btn>
              </template>
            </v-alert>
            <v-chip v-else color="success" prepend-icon="mdi-check-circle" class="mt-4">
              Consentement accordé
            </v-chip>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card elevation="2" border>
          <v-card-title class="bg-grey-lighten-3 text-indigo-darken-4 py-3">
            Procédures liées ({{ dossiers.length }})
          </v-card-title>
          <v-list v-if="dossiers.length > 0">
            <v-list-item
              v-for="d in dossiers"
              :key="d.id"
              :to="`/dossiers/${d.id}`"
              link
              border="bottom"
            >
              <template v-slot:prepend>
                <v-icon color="indigo">mdi-folder-text</v-icon>
              </template>
              <v-list-item-title class="font-weight-bold">{{ d.reference_code }}</v-list-item-title>
              <v-list-item-subtitle>{{ d.title }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
          <v-card-text v-else class="text-center py-12 text-grey">
            <v-icon size="48">mdi-folder-open-outline</v-icon>
            <p>Aucun dossier enregistré pour ce client.</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>

  <v-alert v-else type="error" class="ma-12">
    Désolé, ce client n'existe pas ou a été archivé.
  </v-alert>
</template>