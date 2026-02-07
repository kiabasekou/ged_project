<script setup>
import { onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDossierStore } from '@/stores/dossier'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'

// Import ApexCharts (une seule fois ici)
import VueApexCharts from 'vue3-apexcharts'

// Stores
const authStore = useAuthStore()
const dossierStore = useDossierStore()

// États dérivés
const loading = computed(() => dossierStore.loadingStats || dossierStore.loadingList)
const error = computed(() => dossierStore.error || null)

const stats = computed(() => dossierStore.stats || {})
const recentDossiers = computed(() => dossierStore.list || [])

// Données pour le graphique circulaire
const chartData = computed(() => {
  const categories = stats.value.par_categorie || {}
  return {
    series: Object.values(categories),
    labels: Object.keys(categories).map(key =>
      key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    )
  }
})

// Chargement des données
onMounted(async () => {
  await Promise.all([
    dossierStore.fetchStats(),
    dossierStore.fetchRecent(8)
  ])
})

// Formatage de date localisé (Gabon = français)
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return format(new Date(dateString), 'dd MMM yyyy', { locale: fr })
}
</script>

<template>
  <v-container fluid class="pa-6">
    <!-- En-tête -->
    <div class="d-flex align-center mb-8">
      <v-icon size="48" color="indigo-darken-4" class="mr-4">mdi-view-dashboard</v-icon>
      <div>
        <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
          Tableau de bord
        </h1>
        <p class="text-subtitle-1 text-grey-darken-1 mt-1 mb-0">
          Vue d'ensemble du cabinet — Suivi des dossiers et performances
        </p>
      </div>
    </div>

    <!-- Erreur -->
    <v-alert
      v-if="error"
      type="error"
      variant="tonal"
      class="mb-6"
      closable
      @click:close="dossierStore.clearError?.() || (error = null)"
    >
      {{ error }}
    </v-alert>

    <!-- Chargement avec skeletons -->
    <div v-if="loading">
      <v-row class="mb-8">
        <v-col v-for="n in 4" :key="n" cols="12" sm="6" md="3">
          <v-skeleton-loader type="card" height="180" class="rounded-lg" />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" lg="8">
          <v-skeleton-loader type="table" height="400" class="rounded-lg" />
        </v-col>
        <v-col cols="12" lg="4">
          <v-skeleton-loader type="list-item-two-line@5" height="400" class="rounded-lg" />
        </v-col>
      </v-row>
    </div>

    <!-- Contenu principal -->
    <div v-else>
      <!-- Cartes statistiques -->
      <v-row class="mb-10">
        <v-col cols="12" sm="6" md="3">
          <v-card elevation="4" class="pa-5 text-center rounded-xl" style="border-top: 6px solid #1A237E">
            <v-icon size="56" color="indigo-darken-4" class="mb-3">mdi-folder-multiple</v-icon>
            <div class="text-h3 font-weight-bold text-indigo-darken-4">{{ stats.total || 0 }}</div>
            <div class="text-subtitle-1 text-grey-darken-2">Dossiers totaux</div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card elevation="4" class="pa-5 text-center rounded-xl" style="border-top: 6px solid #455A64">
            <v-icon size="56" color="blue-grey-darken-1" class="mb-3">mdi-folder-clock</v-icon>
            <div class="text-h3 font-weight-bold text-blue-grey-darken-1">{{ stats.ouverts || 0 }}</div>
            <div class="text-subtitle-1 text-grey-darken-2">En cours</div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card elevation="4" class="pa-5 text-center rounded-xl" style="border-top: 6px solid #B71C1C">
            <v-icon size="56" color="red-darken-4" class="mb-3">mdi-alert-circle</v-icon>
            <div class="text-h3 font-weight-bold text-red-darken-4">{{ stats.en_retard || 0 }}</div>
            <div class="text-subtitle-1 text-grey-darken-2">En retard</div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card elevation="4" class="pa-5 text-center rounded-xl" style="border-top: 6px solid #2E7D32">
            <v-icon size="56" color="green-darken-2" class="mb-3">mdi-check-circle</v-icon>
            <div class="text-h3 font-weight-bold text-green-darken-2">{{ stats.clotures || 0 }}</div>
            <div class="text-subtitle-1 text-grey-darken-2">Clôturés</div>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <!-- Dossiers récents -->
        <v-col cols="12" lg="8">
          <v-card elevation="4" rounded="lg">
            <v-card-title class="bg-indigo-darken-4 text-white py-4">
              <v-icon start color="white">mdi-history</v-icon>
              <span class="text-h6 font-weight-bold">Dossiers récemment mis à jour</span>
            </v-card-title>
            <v-data-table
              :headers="[
                { title: 'Référence', key: 'reference_code', width: '140' },
                { title: 'Intitulé du dossier', key: 'title' },
                { title: 'Statut', key: 'status', align: 'center', width: '120' },
                { title: 'Ouvert le', key: 'opening_date', align: 'end', width: '140' }
              ]"
              :items="recentDossiers"
              density="comfortable"
              hover
              class="elevation-1"
            >
              <template #item.status="{ item }">
                <v-chip
                  :color="item.status === 'OUVERT' ? 'info' : item.status === 'CLOTURE' ? 'success' : 'warning'"
                  size="small"
                  variant="flat"
                  class="font-weight-bold text-uppercase"
                >
                  {{ item.status === 'CLOTURE' ? 'Clôturé' : item.status }}
                </v-chip>
              </template>
              <template #item.opening_date="{ item }">
                {{ formatDate(item.opening_date) }}
              </template>
            </v-data-table>
          </v-card>
        </v-col>

        <!-- Répartition par domaine (Pie Chart) -->
        <v-col cols="12" lg="4">
          <v-card elevation="4" rounded="lg" class="fill-height d-flex flex-column">
            <v-card-title class="bg-grey-darken-3 text-white py-4">
              <v-icon start color="white">mdi-chart-pie</v-icon>
              <span class="text-h6 font-weight-bold">Répartition par domaine</span>
            </v-card-title>

            <v-card-text class="flex-grow-1 pa-0">
              <apexchart
                v-if="chartData.series.length > 0 && chartData.series.some(v => v > 0)"
                type="pie"
                height="350"
                :options="{
                  chart: { type: 'pie' },
                  labels: chartData.labels,
                  colors: ['#1A237E', '#3949AB', '#5C6BC0', '#7986CB', '#9FA8DA', '#C5CAE9'],
                  legend: { position: 'bottom', labels: { colors: '#424242' } },
                  dataLabels: { enabled: true, style: { fontSize: '14px', fontWeight: 'bold' } },
                  tooltip: { y: { formatter: val => val + ' dossier(s)' } },
                  noData: { text: 'Aucune donnée disponible', style: { color: '#666' } }
                }"
                :series="chartData.series"
              />
              <div v-else class="d-flex flex-column align-center justify-center fill-height pa-8">
                <v-icon size="80" color="grey-lighten-2" class="mb-4">mdi-chart-pie-off</v-icon>
                <p class="text-grey-darken-1 text-subtitle-1">Aucune catégorie enregistrée</p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Message de bienvenue -->
      <v-alert
        v-if="authStore.user"
        border="start"
        colored-border
        color="indigo-darken-4"
        elevation="4"
        class="mt-10"
        prominent
      >
        <div class="d-flex align-center justify-space-between flex-wrap gap-6">
          <div>
            <div class="text-h6 font-weight-bold text-indigo-darken-4">
              Bon retour, Maître {{ authStore.user.first_name }} {{ authStore.user.last_name }}
              <v-chip size="small" color="indigo-darken-4" class="ml-3 text-white">
                {{ authStore.user.role }}
              </v-chip>
            </div>
            <div class="mt-3 text-body-1">
              <v-icon
                :color="stats.en_retard > 0 ? 'error' : 'success'"
                size="large"
 class="mr-2"
              >
                {{ stats.en_retard > 0 ? 'mdi-alert' : 'mdi-check-decagram' }}
              </v-icon>
              <span :class="stats.en_retard > 0 ? 'text-error font-weight-bold' : 'text-success'">
                {{ stats.en_retard > 0
                  ? `Attention : ${stats.en_retard} dossier(s) en retard de procédure.`
                  : 'Excellent ! Tous les délais sont respectés.' }}
              </span>
            </div>
          </div>
          <v-avatar size="80">
            <v-img
              :src="`https://ui-avatars.com/api/?name=${authStore.user.first_name}+${authStore.user.last_name}&background=1A237E&color=fff&bold=true`"
              alt="Avatar"
            />
          </v-avatar>
        </div>
      </v-alert>
    </div>
  </v-container>
</template>