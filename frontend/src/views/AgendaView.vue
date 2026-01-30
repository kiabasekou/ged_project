<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/plugins/axios'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import listPlugin from '@fullcalendar/list'
import frLocale from '@fullcalendar/core/locales/fr'

// Import du modal
import EventCreateModal from '@/components/agenda/EventCreateModal.vue'

const router = useRouter()

// États
const isReady = ref(false)
const loading = ref(false)
const error = ref(null)
const events = ref([])

// Référence au modal
const createModal = ref(null)

// Configuration FullCalendar
const calendarOptions = ref({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin],
  initialView: 'dayGridMonth',
  locale: frLocale,
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
  },
  buttonText: {
    today: 'Aujourd’hui',
    month: 'Mois',
    week: 'Semaine',
    day: 'Jour',
    list: 'Liste'
  },
  events: computed(() => events.value),
  height: 'auto',
  editable: false,
  selectable: true,
  selectMirror: true,
  dayMaxEvents: true,
  eventTimeFormat: {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  },
  // === CLIC SUR UN ÉVÉNEMENT ===
  eventClick: (info) => {
    info.jsEvent.preventDefault()
    const dossierId = info.event.extendedProps?.dossier_id || info.event.id
    if (dossierId) {
      router.push(`/dossiers/${dossierId}`)
    }
  },
  // === CLIC SUR UNE DATE → OUVRE LE MODAL ===
  dateClick: (info) => {
    // Ouvre le modal avec la date cliquée
    if (createModal.value) {
      createModal.value.open(info.dateStr)
    }
  },
  // Optionnel : sélection de plage (pour événements multi-jours plus tard)
  select: (info) => {
    if (createModal.value) {
      createModal.value.open(info.startStr)
    }
    // Désélectionne après ouverture
    info.view.calendar.unselect()
  },
  loading: (isLoading) => {
    loading.value = isLoading
  }
})

// Chargement des événements
const loadEvents = async () => {
  if (loading.value) return

  loading.value = true
  error.value = null

  try {
    const response = await api.get('/agenda/calendar/')
    events.value = response.data.map(event => ({
      ...event,
      title: event.title || 'Événement sans titre',
      start: event.start || event.start_date,
      end: event.end || event.end_date,
      allDay: event.all_day || false,
      backgroundColor: event.type === 'DELAI' ? '#1A237E' :
                       event.priority === 'URGENT' ? '#B71C1C' :
                       event.overdue ? '#B71C1C' : '#1976D2',
      borderColor: 'transparent',
      textColor: '#FFFFFF',
      extendedProps: {
        dossier_id: event.dossier_id || event.dossier
      }
    }))
  } catch (err) {
    console.error('Erreur chargement agenda:', err)
    error.value = 'Impossible de charger l\'agenda. Veuillez réessayer.'
  } finally {
    loading.value = false
    isReady.value = true
  }
}

// Ajout d'un nouvel événement créé via le modal
const handleEventCreated = (newEvent) => {
  // Transforme le nouvel événement au to format FullCalendar
  const formattedEvent = {
    ...newEvent,
    title: newEvent.title,
    start: newEvent.start_date + (newEvent.start_time ? `T${newEvent.start_time}` : ''),
    end: newEvent.end_date && newEvent.end_time ? `${newEvent.end_date}T${newEvent.end_time}` : null,
    allDay: newEvent.all_day,
    backgroundColor: newEvent.priority === 'URGENT' ? '#B71C1C' : '#1976D2',
    textColor: '#FFFFFF',
    extendedProps: {
      dossier_id: newEvent.dossier
    }
  }

  // Ajoute directement dans le tableau réactif → mise à jour instantanée
  events.value = [...events.value, formattedEvent]
}

// Cycle de vie
onMounted(() => {
  loadEvents()
})
</script>

<template>
  <v-container fluid class="pa-6">
    <!-- En-tête -->
    <div class="d-flex align-center justify-space-between mb-8">
      <div class="d-flex align-center">
        <v-icon size="48" color="indigo-darken-4" class="mr-4">mdi-calendar-month-outline</v-icon>
        <div>
          <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
            Agenda du cabinet
          </h1>
          <p class="text-subtitle-1 text-grey-darken-1 mt-1 mb-0">
            Suivi des délais, audiences et événements importants
          </p>
        </div>
      </div>

      <v-btn
        color="indigo-darken-4"
        prepend-icon="mdi-plus"
        size="large"
        elevation="2"
        @click="createModal?.open()"
      >
        Nouvel événement
      </v-btn>
    </div>

    <!-- Erreur -->
    <v-alert
      v-if="error"
      type="error"
      variant="tonal"
      class="mb-6"
      closable
      @click:close="error = null"
    >
      {{ error }}
    </v-alert>

    <!-- Calendrier -->
    <v-card elevation="8" rounded="lg" class="overflow-hidden">
      <v-card-text class="pa-0">
        <FullCalendar :options="calendarOptions" class="custom-calendar" />
      </v-card-text>

      <!-- Légende -->
      <v-card-actions class="pa-6 bg-grey-lighten-5">
        <div class="d-flex flex-wrap gap-4 align-center">
          <v-chip color="indigo-darken-4" label>
            <v-icon start size="small">mdi-folder-clock</v-icon>
            Délai dossier
          </v-chip>
          <v-chip color="red-darken-4" label>
            <v-icon start size="small">mdi-alert</v-icon>
            Délai dépassé ou urgent
          </v-chip>
          <v-chip color="blue-darken-1" label>
            <v-icon start size="small">mdi-calendar-account</v-icon>
            Rendez-vous / Audience
          </v-chip>

          <v-spacer />

          <div class="text-caption text-medium-emphasis d-none d-md-flex align-center gap-2">
            <v-icon small>mdi-gesture-tap</v-icon>
            <span>Cliquez sur une date pour créer un événement</span>
          </div>

          <v-btn
            color="indigo-darken-4"
            prepend-icon="mdi-refresh"
            :loading="loading"
            @click="loadEvents"
            variant="text"
          >
            Actualiser
          </v-btn>
        </div>
      </v-card-actions>
    </v-card>

    <!-- Info mobile -->
    <div class="d-md-none mt-6 text-center">
      <p class="text-caption text-grey-darken-2">
        <v-icon small class="mr-1">mdi-gesture-tap</v-icon>
        Appuyez sur une date pour ajouter un événement
      </p>
    </div>

    <!-- MODAL DE CRÉATION -->
    <EventCreateModal
      ref="createModal"
      @created="handleEventCreated"
      @close="() => {}"
    />
  </v-container>
</template>

<style scoped>
/* Même style que précédemment */
:deep(.fc-button-primary) {
  background-color: #1A237E !important;
  border: none !important;
  text-transform: none;
  font-weight: 500;
}

:deep(.fc-button-primary:hover) {
  background-color: #0D113F !important;
}

:deep(.fc-button-primary.fc-button-active) {
  background-color: #3949AB !important;
  color: white !important;
}

:deep(.fc-toolbar-title) {
  font-size: 1.5rem !important;
  font-weight: 600;
  color: #1A237E;
}

:deep(.fc-daygrid-event) {
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 0.85rem;
  font-weight: 500;
}

:deep(.fc-event-title) {
  white-space: normal;
}

:deep(.fc-daygrid-event:hover) {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

@media (max-width: 600px) {
  :deep(.fc-toolbar.fc-header-toolbar) {
    flex-direction: column;
    gap: 8px;
  }
}
</style>