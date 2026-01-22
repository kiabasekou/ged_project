<script setup>
import { onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDossierStore } from '@/stores/dossier'

const authStore = useAuthStore()
const dossierStore = useDossierStore()

onMounted(async () => {
  // Appels parallèles pour optimiser le temps de réponse au cabinet
  await Promise.all([
    dossierStore.fetchStats(),
    dossierStore.fetchRecent(8)
  ])
})

// --- Accès réactif aux données du store (CORRECTIONS) ---

// Les statistiques globales
const stats = computed(() => dossierStore.stats)

// Correction : On pointe vers 'list' qui contient les dossiers récents après fetchRecent
const recentDossiers = computed(() => dossierStore.list)

// Correction : On considère que ça charge si les stats OU la liste sont en cours
const loading = computed(() => dossierStore.loadingStats || dossierStore.loadingList)

// Calcul pour la répartition des catégories (Sécurisé)
const chartData = computed(() => {
  const categories = stats.value.par_categorie || {}
  return Object.keys(categories).map(key => ({
    name: key,
    value: categories[key]
  }))
})
</script>

<template>
  <v-container fluid>
    <div class="d-flex align-center mb-6">
      <v-icon size="40" color="primary" class="mr-3">mdi-view-dashboard</v-icon>
      <h1 class="text-h4 font-weight-bold text-primary">Tableau de bord</h1>
    </div>

    <v-row v-if="loading" class="my-12">
      <v-col cols="12" class="text-center">
        <v-progress-circular indeterminate size="64" color="primary" />
        <p class="mt-4 text-h6 text-grey-darken-1">Analyse des dossiers du cabinet...</p>
      </v-col>
    </v-row>

    <div v-else>
      <v-row class="mb-8">
        <v-col cols="12" sm="6" md="3">
          <v-card elevation="2" class="pa-4 text-center" border="t-lg" style="border-top-color: #1A237E !important">
            <v-icon size="48" color="primary" class="mb-3">mdi-folder-multiple</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.total }}</div>
            <div class="text-subtitle-1 text-grey-darken-1">Dossiers totaux</div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card elevation="2" class="pa-4 text-center" border="t-lg" style="border-top-color: #455A64 !important">
            <v-icon size="48" color="secondary" class="mb-3">mdi-folder-clock</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.ouverts }}</div>
            <div class="text-subtitle-1 text-grey-darken-1">En cours</div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card elevation="2" class="pa-4 text-center" border="t-lg" style="border-top-color: #B71C1C !important">
            <v-icon size="48" color="error" class="mb-3">mdi-alert-circle</v-icon>
            <div class="text-h4 font-weight-bold text-error">{{ stats.en_retard }}</div>
            <div class="text-subtitle-1 text-grey-darken-1">En retard</div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card elevation="2" class="pa-4 text-center" border="t-lg" style="border-top-color: #2E7D32 !important">
            <v-icon size="48" color="success" class="mb-3">mdi-check-circle</v-icon>
            <div class="text-h4 font-weight-bold text-success">{{ stats.clotures }}</div>
            <div class="text-subtitle-1 text-grey-darken-1">Clôturés</div>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" lg="8">
          <v-card elevation="2">
            <v-card-title class="bg-primary text-white d-flex align-center py-4">
              <v-icon left class="mr-2">mdi-history</v-icon>
              Dossiers récemment mis à jour
            </v-card-title>
            
            <v-data-table
              :headers="[
                { title: 'Référence', key: 'reference_code' },
                { title: 'Titre', key: 'title' },
                { title: 'Statut', key: 'status', align: 'center' },
                { title: 'Ouverture', key: 'opening_date', align: 'end' },
              ]"
              :items="recentDossiers"
              density="comfortable"
              hover
            >
              <template v-slot:item.status="{ value }">
                <v-chip
                  :color="value === 'OUVERT' ? 'info' : value === 'CLOTURE' ? 'success' : 'warning'"
                  size="small"
                  variant="flat"
                  class="font-weight-bold"
                >
                  {{ value }}
                </v-chip>
              </template>
              <template v-slot:item.opening_date="{ value }">
                {{ value ? new Date(value).toLocaleDateString('fr-GA') : '-' }}
              </template>
            </v-data-table>
          </v-card>
        </v-col>

        <v-col cols="12" lg="4">
          <v-card elevation="2" class="fill-height">
            <v-card-title class="bg-grey-darken-3 text-white py-4">
              <v-icon left class="mr-2">mdi-chart-arc</v-icon>
              Répartition juridique
            </v-card-title>
            <v-list v-if="chartData.length > 0">
              <v-list-item v-for="cat in chartData" :key="cat.name" border="bottom">
                <template v-slot:prepend>
                  <v-icon color="indigo-lighten-1">mdi-label-variant</v-icon>
                </template>
                <v-list-item-title class="font-weight-medium">{{ cat.name }}</v-list-item-title>
                <template v-slot:append>
                  <v-chip size="small" variant="outlined" color="primary">{{ cat.value }}</v-chip>
                </template>
              </v-list-item>
            </v-list>
            <v-card-text v-else class="text-center py-12">
              <v-icon size="64" color="grey-lighten-2" class="mb-4">mdi-database-off</v-icon>
              <p class="text-grey">Aucun dossier catégorisé.</p>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-alert
        v-if="authStore.user"
        border="start"
        colored-border
        color="primary"
        elevation="2"
        class="mt-8 bg-white"
      >
        <div class="text-h6">
          Bienvenue, {{ authStore.user.first_name }} {{ authStore.user.last_name }} 
          <span class="text-subtitle-2 text-grey-darken-1 ml-2">({{ authStore.user.role }})</span>
        </div>
        <div class="mt-1">
          <v-icon size="small" :color="stats.en_retard > 0 ? 'error' : 'success'" class="mr-1">
            {{ stats.en_retard > 0 ? 'mdi-alert' : 'mdi-check-decagram' }}
          </v-icon>
          <span v-if="stats.en_retard > 0" class="text-error font-weight-bold">
            Attention : {{ stats.en_retard }} dossiers ont dépassé leur date limite de traitement.
          </span>
          <span v-else class="text-success font-weight-medium">
            Tous les délais de procédure sont respectés.
          </span>
        </div>
      </v-alert>
    </div>
  </v-container>
</template>