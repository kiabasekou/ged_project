<script setup>
import { ref, onMounted, shallowRef } from 'vue' 
import { useRouter } from 'vue-router'
import api from '@/plugins/axios'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import listPlugin from '@fullcalendar/list'

const router = useRouter()
const isReady = ref(false) 
const loading = ref(false) 

// --- 1. FONCTIONS (Hoisting respecté) ---

const handleEventClick = (info) => {
  const dossierId = info.event.id
  if (dossierId) {
    router.push(`/dossiers/${dossierId}`)
  }
}

const handleDateClick = (info) => {
  console.log('Date cliquée :', info.dateStr)
}

const loadEvents = async () => {
  loading.value = true
  try {
    // ⚠️ CORRECTION URL : Vérifiez si votre backend utilise /agenda/ ou /events/
    // Vos logs montrent un 404 sur /api/events/calendar/
    const response = await api.get('/agenda/calendar/')
    
    // CORRECTION RÉACTIVITÉ : Avec shallowRef, on doit remplacer l'objet .value
    calendarOptions.value = {
      ...calendarOptions.value,
      events: response.data
    }
  } catch (err) {
    console.error('Erreur chargement agenda:', err)
  } finally {
    loading.value = false
  }
}

// --- 2. CONFIGURATION ---

const calendarOptions = shallowRef({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
  },
  locale: 'fr',
  buttonText: {
    today: "Aujourd'hui",
    month: 'Mois',
    week: 'Semaine',
    day: 'Jour',
    list: 'Liste'
  },
  events: [],
  eventClick: handleEventClick,
  dateClick: handleDateClick,
  height: 'auto',
  editable: false,
  selectable: true,
  dayMaxEvents: 3,
  eventTimeFormat: {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  }
})

// --- 3. CYCLE DE VIE ---

onMounted(async () => {
  await loadEvents()
  isReady.value = true 
})
</script>

<template>
  <div v-if="isReady">
    <div class="d-flex align-center mb-6">
      <v-icon size="40" color="indigo-darken-4" class="mr-3">mdi-calendar-alert</v-icon>
      <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
        Agenda du cabinet
      </h1>
    </div>

    <v-card elevation="6">
      <v-card-text class="pa-0">
        <FullCalendar :options="calendarOptions" />
      </v-card-text>

      <v-card-actions class="pa-4 bg-grey-lighten-4">
        <v-chip color="indigo-darken-4" class="mr-4">
          <v-icon start size="small" class="mr-1">mdi-folder</v-icon>
          Délai dossier
        </v-chip>
        <v-chip color="red-darken-2">
          <v-icon start size="small" class="mr-1">mdi-alert</v-icon>
          Délai dépassé
        </v-chip>

        <v-spacer />

        <v-btn
          color="indigo-darken-4"
          prepend-icon="mdi-refresh"
          :loading="loading"
          @click="loadEvents"
        >
          Actualiser
        </v-btn>
      </v-card-actions>
    </v-card>

    <div class="d-md-none mt-6 text-center">
      <p class="text-caption text-grey-darken-2">
        Cliquez sur un événement pour ouvrir le dossier
      </p>
    </div>
  </div>

  <v-container v-else class="fill-height">
    <v-row justify="center" align="center">
      <v-progress-circular indeterminate color="primary" size="64" />
    </v-row>
  </v-container>
</template>

<style scoped>
:deep(.fc-button-primary) {
  background-color: #1A237E !important;
  border-color: #1A237E !important;
}

:deep(.fc-button-primary:hover) {
  background-color: #0D113F !important;
}

:deep(.fc-button-active) {
  background-color: #FFD700 !important;
  color: #1A237E !important;
}
</style>