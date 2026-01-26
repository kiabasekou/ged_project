<template>
  <v-container fluid class="pa-6">
    <!-- En-tête -->
    <v-row class="mb-6">
      <v-col cols="12" class="d-flex align-center justify-space-between">
        <div class="d-flex align-center">
          <v-icon size="40" color="indigo-darken-4" class="mr-3">
            mdi-calendar-month
          </v-icon>
          <div>
            <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
              Agenda & Délais
            </h1>
            <p class="text-subtitle-1 text-grey-darken-1 mb-0">
              Gestion des audiences, rendez-vous et échéances juridiques
            </p>
          </div>
        </div>
        <v-btn
          color="indigo-darken-4"
          prepend-icon="mdi-plus"
          size="large"
          elevation="2"
          @click="openCreateDialog"
        >
          Nouvel événement
        </v-btn>
      </v-col>
    </v-row>

    <!-- Alertes délais critiques -->
    <v-expand-transition>
      <v-row v-if="criticalDeadlines.length > 0" class="mb-6">
        <v-col cols="12">
          <v-alert
            type="error"
            variant="tonal"
            prominent
            border="start"
            class="mb-0"
          >
            <template v-slot:prepend>
              <v-icon size="40">mdi-alert-circle</v-icon>
            </template>
            <div class="d-flex align-center justify-space-between">
              <div>
                <div class="text-h6 font-weight-bold mb-2">
                  ⚠️ {{ criticalDeadlines.length }} délai{{ criticalDeadlines.length > 1 ? 's' : '' }} critique{{ criticalDeadlines.length > 1 ? 's' : '' }}
                </div>
                <div class="text-body-2">
                  <span v-for="(deadline, index) in criticalDeadlines.slice(0, 3)" :key="deadline.id">
                    <strong>{{ deadline.title }}</strong> ({{ formatRelativeDate(deadline.start_date) }}){{ index < Math.min(2, criticalDeadlines.length - 1) ? ', ' : '' }}
                  </span>
                  <span v-if="criticalDeadlines.length > 3"> et {{ criticalDeadlines.length - 3 }} autre(s)</span>
                </div>
              </div>
              <v-btn
                variant="text"
                prepend-icon="mdi-eye"
                @click="showCriticalDeadlinesDialog = true"
              >
                Voir tout
              </v-btn>
            </div>
          </v-alert>
        </v-col>
      </v-row>
    </v-expand-transition>

    <!-- Statistiques rapides -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4 text-center border-t-lg" style="border-top: 4px solid #D32F2F">
          <v-icon size="40" color="red-darken-2" class="mb-2">mdi-gavel</v-icon>
          <div class="text-h5 font-weight-bold">{{ stats.audiences || 0 }}</div>
          <div class="text-caption text-grey-darken-1">Audiences</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4 text-center border-t-lg" style="border-top: 4px solid #1976D2">
          <v-icon size="40" color="blue" class="mb-2">mdi-account-tie</v-icon>
          <div class="text-h5 font-weight-bold">{{ stats.rdv || 0 }}</div>
          <div class="text-caption text-grey-darken-1">Rendez-vous</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4 text-center border-t-lg" style="border-top: 4px solid #F57C00">
          <v-icon size="40" color="orange-darken-2" class="mb-2">mdi-file-sign</v-icon>
          <div class="text-h5 font-weight-bold">{{ stats.formalites || 0 }}</div>
          <div class="text-caption text-grey-darken-1">Formalités</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4 text-center border-t-lg" style="border-top: 4px solid #388E3C">
          <v-icon size="40" color="green-darken-2" class="mb-2">mdi-calendar-check</v-icon>
          <div class="text-h5 font-weight-bold">{{ stats.total || 0 }}</div>
          <div class="text-caption text-grey-darken-1">Total ce mois</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filtres rapides -->
    <v-card elevation="2" class="mb-6">
      <v-card-text>
        <v-row dense>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.type"
              :items="eventTypeFilters"
              label="Type d'événement"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              prepend-inner-icon="mdi-filter"
              @update:model-value="filterEvents"
            >
              <template v-slot:item="{ item, props }">
                <v-list-item v-bind="props">
                  <template v-slot:prepend>
                    <v-icon :color="item.raw.color">{{ item.raw.icon }}</v-icon>
                  </template>
                </v-list-item>
              </template>
            </v-select>
          </v-col>
          <v-col cols="12" md="4">
            <v-autocomplete
              v-model="filters.dossier"
              :items="dossiers"
              :loading="loadingDossiers"
              item-title="display_name"
              item-value="id"
              label="Filtrer par dossier"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              prepend-inner-icon="mdi-folder"
              @update:model-value="filterEvents"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.priority"
              :items="priorityFilters"
              label="Priorité"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              prepend-inner-icon="mdi-flag"
              @update:model-value="filterEvents"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Calendrier FullCalendar -->
    <v-card elevation="2">
      <v-card-text class="pa-0">
        <FullCalendar
          ref="calendar"
          :options="calendarOptions"
          class="custom-calendar"
        />
      </v-card-text>
    </v-card>

    <!-- Dialog Création/Édition Événement -->
    <v-dialog v-model="eventDialog" max-width="700" persistent>
      <v-card>
        <v-card-title class="bg-indigo-darken-4 text-white py-4">
          <v-icon start color="white">{{ isEditMode ? 'mdi-pencil' : 'mdi-calendar-plus' }}</v-icon>
          {{ isEditMode ? 'Modifier l\'événement' : 'Nouvel événement' }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-form ref="eventForm" v-model="formValid">
            <v-row>
              <!-- Type -->
              <v-col cols="12">
                <v-select
                  v-model="eventFormData.type"
                  :items="eventTypes"
                  label="Type d'événement *"
                  variant="outlined"
                  density="comfortable"
                  :rules="[rules.required]"
                  prepend-inner-icon="mdi-shape"
                >
                  <template v-slot:item="{ item, props }">
                    <v-list-item v-bind="props">
                      <template v-slot:prepend>
                        <v-icon :color="item.raw.color">{{ item.raw.icon }}</v-icon>
                      </template>
                    </v-list-item>
                  </template>
                  <template v-slot:selection="{ item }">
                    <v-icon :color="item.raw.color" start>{{ item.raw.icon }}</v-icon>
                    {{ item.title }}
                  </template>
                </v-select>
              </v-col>

              <!-- Titre -->
              <v-col cols="12">
                <v-text-field
                  v-model="eventFormData.title"
                  label="Titre de l'événement *"
                  variant="outlined"
                  density="comfortable"
                  :rules="[rules.required, rules.maxLength(200)]"
                  counter="200"
                  prepend-inner-icon="mdi-format-title"
                  placeholder="Ex: Audience TPI Libreville - Affaire Mba"
                />
              </v-col>

              <!-- Dossier lié -->
              <v-col cols="12" md="6">
                <v-autocomplete
                  v-model="eventFormData.dossier"
                  :items="dossiers"
                  :loading="loadingDossiers"
                  item-title="display_name"
                  item-value="id"
                  label="Dossier lié"
                  variant="outlined"
                  density="comfortable"
                  clearable
                  prepend-inner-icon="mdi-folder-search"
                  hint="Optionnel - Lier à un dossier juridique"
                  persistent-hint
                />
              </v-col>

              <!-- Lieu -->
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="eventFormData.location"
                  label="Lieu"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-map-marker"
                  placeholder="Ex: Tribunal de Première Instance"
                />
              </v-col>

              <!-- Date -->
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="eventFormData.start_date"
                  type="date"
                  label="Date *"
                  variant="outlined"
                  density="comfortable"
                  :rules="[rules.required, rules.dateNotPast]"
                  prepend-inner-icon="mdi-calendar"
                />
              </v-col>

              <!-- Journée entière -->
              <v-col cols="12" md="6" class="d-flex align-center">
                <v-switch
                  v-model="eventFormData.all_day"
                  label="Toute la journée"
                  color="indigo"
                  hide-details
                  density="comfortable"
                  inset
                />
              </v-col>

              <!-- Horaires (si pas toute la journée) -->
              <template v-if="!eventFormData.all_day">
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="eventFormData.start_time"
                    type="time"
                    label="Heure de début *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required]"
                    prepend-inner-icon="mdi-clock-start"
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="eventFormData.end_time"
                    type="time"
                    label="Heure de fin"
                    variant="outlined"
                    density="comfortable"
                    prepend-inner-icon="mdi-clock-end"
                  />
                </v-col>
              </template>

              <!-- Priorité -->
              <v-col cols="12" md="6">
                <v-select
                  v-model="eventFormData.priority"
                  :items="priorities"
                  label="Priorité"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-flag"
                >
                  <template v-slot:item="{ item, props }">
                    <v-list-item v-bind="props">
                      <template v-slot:prepend>
                        <v-icon :color="item.raw.color">mdi-flag</v-icon>
                      </template>
                    </v-list-item>
                  </template>
                </v-select>
              </v-col>

              <!-- Rappel -->
              <v-col cols="12" md="6">
                <v-select
                  v-model="eventFormData.reminder"
                  :items="reminders"
                  label="Rappel"
                  variant="outlined"
                  density="comfortable"
                  clearable
                  prepend-inner-icon="mdi-bell"
                />
              </v-col>

              <!-- Description -->
              <v-col cols="12">
                <v-textarea
                  v-model="eventFormData.description"
                  label="Description / Notes"
                  variant="outlined"
                  density="comfortable"
                  rows="4"
                  :rules="[rules.maxLength(1000)]"
                  counter="1000"
                  prepend-inner-icon="mdi-text"
                  placeholder="Notes importantes, pièces à apporter, contacts..."
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <v-card-actions class="px-6 pb-6">
          <v-btn
            v-if="isEditMode"
            color="error"
            variant="text"
            prepend-icon="mdi-delete"
            @click="confirmDeleteEvent"
          >
            Supprimer
          </v-btn>
          <v-spacer />
          <v-btn
            variant="text"
            @click="closeEventDialog"
            :disabled="saving"
          >
            Annuler
          </v-btn>
          <v-btn
            color="indigo-darken-4"
            variant="elevated"
            :loading="saving"
            :disabled="!formValid"
            @click="saveEvent"
          >
            {{ isEditMode ? 'Enregistrer' : 'Créer l\'événement' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog Détails Événement (Vue seule) -->
    <v-dialog v-model="eventDetailsDialog" max-width="600">
      <v-card v-if="selectedEvent">
        <v-card-title 
          class="text-white py-4"
          :style="{ backgroundColor: selectedEvent.backgroundColor }"
        >
          <v-icon start color="white">{{ getEventTypeIcon(selectedEvent.extendedProps?.type) }}</v-icon>
          {{ selectedEvent.title }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-list density="comfortable">
            <v-list-item v-if="selectedEvent.extendedProps?.type" prepend-icon="mdi-shape">
              <v-list-item-title>Type</v-list-item-title>
              <v-list-item-subtitle>{{ getEventTypeLabel(selectedEvent.extendedProps.type) }}</v-list-item-subtitle>
            </v-list-item>

            <v-list-item prepend-icon="mdi-calendar">
              <v-list-item-title>Date et heure</v-list-item-title>
              <v-list-item-subtitle>
                {{ formatEventDateTime(selectedEvent) }}
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item v-if="selectedEvent.extendedProps?.location" prepend-icon="mdi-map-marker">
              <v-list-item-title>Lieu</v-list-item-title>
              <v-list-item-subtitle>{{ selectedEvent.extendedProps.location }}</v-list-item-subtitle>
            </v-list-item>

            <v-list-item 
              v-if="selectedEvent.extendedProps?.dossier_info" 
              prepend-icon="mdi-folder"
              :to="{ name: 'DossierDetail', params: { id: selectedEvent.extendedProps.dossier } }"
            >
              <v-list-item-title>Dossier lié</v-list-item-title>
              <v-list-item-subtitle>
                {{ selectedEvent.extendedProps.dossier_info.reference_code }} - 
                {{ selectedEvent.extendedProps.dossier_info.title }}
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item v-if="selectedEvent.extendedProps?.priority" prepend-icon="mdi-flag">
              <v-list-item-title>Priorité</v-list-item-title>
              <v-list-item-subtitle>
                <v-chip
                  size="small"
                  :color="getPriorityColor(selectedEvent.extendedProps.priority)"
                  variant="tonal"
                >
                  {{ selectedEvent.extendedProps.priority }}
                </v-chip>
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item v-if="selectedEvent.extendedProps?.description" prepend-icon="mdi-text">
              <v-list-item-title>Description</v-list-item-title>
              <v-list-item-subtitle class="text-wrap">
                {{ selectedEvent.extendedProps.description }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card-text>

        <v-card-actions class="px-6 pb-6">
          <v-spacer />
          <v-btn variant="text" @click="eventDetailsDialog = false">
            Fermer
          </v-btn>
          <v-btn
            color="indigo-darken-4"
            variant="elevated"
            prepend-icon="mdi-pencil"
            @click="editEventFromDetails"
          >
            Modifier
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog Liste Délais Critiques -->
    <v-dialog v-model="showCriticalDeadlinesDialog" max-width="800">
      <v-card>
        <v-card-title class="bg-error text-white py-4">
          <v-icon start color="white">mdi-alert-circle</v-icon>
          Délais critiques ({{ criticalDeadlines.length }})
        </v-card-title>

        <v-card-text class="pa-0">
          <v-list>
            <v-list-item
              v-for="deadline in criticalDeadlines"
              :key="deadline.id"
              :to="{ name: 'DossierDetail', params: { id: deadline.dossier } }"
              border
            >
              <template v-slot:prepend>
                <v-avatar :color="getEventTypeColor(deadline.type)">
                  <v-icon color="white">{{ getEventTypeIcon(deadline.type) }}</v-icon>
                </v-avatar>
              </template>

              <v-list-item-title class="font-weight-bold">
                {{ deadline.title }}
              </v-list-item-title>
              
              <v-list-item-subtitle>
                <v-icon size="14">mdi-calendar</v-icon>
                {{ formatDate(deadline.start_date) }} - 
                <strong class="text-error">{{ formatRelativeDate(deadline.start_date) }}</strong>
              </v-list-item-subtitle>

              <template v-slot:append>
                <v-chip
                  size="small"
                  :color="getPriorityColor(deadline.priority)"
                  variant="tonal"
                >
                  {{ deadline.priority }}
                </v-chip>
              </template>
            </v-list-item>
          </v-list>
        </v-card-text>

        <v-card-actions class="px-6 pb-6">
          <v-spacer />
          <v-btn
            variant="text"
            @click="showCriticalDeadlinesDialog = false"
          >
            Fermer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog Confirmation Suppression -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title class="bg-error text-white py-4">
          <v-icon start color="white">mdi-alert</v-icon>
          Confirmer la suppression
        </v-card-title>
        <v-card-text class="pt-6">
          <p class="text-body-1">
            Êtes-vous sûr de vouloir supprimer cet événement ?
          </p>
          <v-alert type="warning" variant="tonal" class="mt-4">
            Cette action est irréversible.
          </v-alert>
        </v-card-text>
        <v-card-actions class="px-6 pb-6">
          <v-spacer />
          <v-btn variant="text" @click="deleteDialog = false">
            Annuler
          </v-btn>
          <v-btn
            color="error"
            variant="elevated"
            :loading="deleting"
            @click="executeDeleteEvent"
          >
            Supprimer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import listPlugin from '@fullcalendar/list'
import frLocale from '@fullcalendar/core/locales/fr'
import api from '@/plugins/axios'

const router = useRouter()

// État
const calendar = ref(null)
const eventDialog = ref(false)
const eventDetailsDialog = ref(false)
const showCriticalDeadlinesDialog = ref(false)
const deleteDialog = ref(false)
const eventForm = ref(null)
const formValid = ref(false)
const saving = ref(false)
const deleting = ref(false)
const loading = ref(false)
const loadingDossiers = ref(false)

const events = ref([])
const allEvents = ref([]) // Pour filtrage
const dossiers = ref([])
const selectedEvent = ref(null)
const eventToDelete = ref(null)

const isEditMode = ref(false)
const eventFormData = ref({
  id: null,
  type: 'RDV',
  title: '',
  dossier: null,
  location: '',
  start_date: new Date().toISOString().split('T')[0],
  start_time: '09:00',
  end_time: '10:00',
  all_day: false,
  description: '',
  reminder: '1_DAY',
  priority: 'NORMAL'
})

// Filtres
const filters = ref({
  type: null,
  dossier: null,
  priority: null
})

// Statistiques
const stats = ref({
  total: 0,
  audiences: 0,
  rdv: 0,
  formalites: 0
})

// Computed
const criticalDeadlines = computed(() => {
  const now = new Date()
  const threeDaysFromNow = new Date(now.getTime() + 3 * 24 * 60 * 60 * 1000)
  
  return allEvents.value
    .filter(e => {
      const eventDate = new Date(e.start_date)
      return eventDate <= threeDaysFromNow && 
             eventDate >= now &&
             (e.priority === 'HIGH' || e.priority === 'URGENT' || e.type === 'AUDIENCE')
    })
    .sort((a, b) => new Date(a.start_date) - new Date(b.start_date))
})

// Configuration
const eventTypes = [
  { 
    title: 'Audience / Plaidoirie', 
    value: 'AUDIENCE', 
    icon: 'mdi-gavel',
    color: '#D32F2F'
  },
  { 
    title: 'Rendez-vous client', 
    value: 'RDV', 
    icon: 'mdi-account-tie',
    color: '#1976D2'
  },
  { 
    title: 'Formalité notariale', 
    value: 'FORMALITE', 
    icon: 'mdi-file-sign',
    color: '#F57C00'
  },
  { 
    title: 'Congé / Absence', 
    value: 'CONGE', 
    icon: 'mdi-airplane',
    color: '#757575'
  },
  { 
    title: 'Autre événement', 
    value: 'AUTRE', 
    icon: 'mdi-calendar-star',
    color: '#455A64'
  }
]

const eventTypeFilters = computed(() => [
  { title: 'Tous les types', value: null },
  ...eventTypes
])

const priorities = [
  { title: 'Normale', value: 'NORMAL', color: 'grey' },
  { title: 'Haute', value: 'HIGH', color: 'orange' },
  { title: 'Urgente', value: 'URGENT', color: 'red' }
]

const priorityFilters = [
  { title: 'Toutes priorités', value: null },
  ...priorities
]

const reminders = [
  { title: '15 minutes avant', value: '15_MIN' },
  { title: '1 heure avant', value: '1_HOUR' },
  { title: '1 jour avant', value: '1_DAY' },
  { title: '1 semaine avant', value: '1_WEEK' }
]

// Règles de validation
const rules = {
  required: v => !!v || 'Ce champ est requis',
  maxLength: max => v => !v || v.length <= max || `Maximum ${max} caractères`,
  dateNotPast: v => {
    if (!v) return true
    const selected = new Date(v)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    return selected >= today || 'La date ne peut pas être dans le passé'
  }
}

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
    today: "Aujourd'hui",
    month: 'Mois',
    week: 'Semaine',
    day: 'Jour',
    list: 'Liste'
  },
  height: 'auto',
  events: [],
  editable: true,
  selectable: true,
  selectMirror: true,
  dayMaxEvents: 3,
  eventTimeFormat: {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  },
  eventClick: handleEventClick,
  select: handleDateSelect,
  eventDrop: handleEventDrop,
  eventResize: handleEventResize,
  datesSet: handleDatesChange
})

// Méthodes
const loadEvents = async (start, end) => {
  loading.value = true
  try {
    const params = {
      page_size: 1000
    }
    
    if (start) params.start_date__gte = start
    if (end) params.start_date__lte = end

    const response = await api.get('/agenda/events/', { params })
    const eventsData = response.data.results || response.data || []
    
    allEvents.value = eventsData
    
    // Charger les infos dossiers
    for (const event of eventsData) {
      if (event.dossier && !event.dossier_info) {
        try {
          const dossierRes = await api.get(`/dossiers/${event.dossier}/`)
          event.dossier_info = dossierRes.data
        } catch (err) {
          console.error('Erreur chargement dossier:', err)
        }
      }
    }
    
    // Convertir pour FullCalendar
    events.value = formatEventsForCalendar(eventsData)
    calendarOptions.value.events = events.value
    
    // Calculer stats
    calculateStats(eventsData)
    
  } catch (error) {
    console.error('Erreur chargement événements:', error)
  } finally {
    loading.value = false
  }
}

const formatEventsForCalendar = (eventsData) => {
  return eventsData.map(event => {
    let start = event.start_date
    let end = event.end_date || event.start_date
    
    if (!event.all_day && event.start_time) {
      start += 'T' + event.start_time
      if (event.end_time) {
        end += 'T' + event.end_time
      }
    }
    
    const eventType = eventTypes.find(t => t.value === event.type)
    
    return {
      id: event.id,
      title: event.title,
      start: start,
      end: event.all_day ? null : end,
      allDay: event.all_day,
      backgroundColor: eventType?.color || '#455A64',
      borderColor: eventType?.color || '#455A64',
      extendedProps: {
        type: event.type,
        location: event.location,
        description: event.description,
        dossier: event.dossier,
        dossier_info: event.dossier_info,
        priority: event.priority,
        reminder: event.reminder
      }
    }
  })
}

const calculateStats = (eventsData) => {
  const now = new Date()
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
  const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0)
  
  const thisMonth = eventsData.filter(e => {
    const eventDate = new Date(e.start_date)
    return eventDate >= startOfMonth && eventDate <= endOfMonth
  })
  
  stats.value = {
    total: thisMonth.length,
    audiences: thisMonth.filter(e => e.type === 'AUDIENCE').length,
    rdv: thisMonth.filter(e => e.type === 'RDV').length,
    formalites: thisMonth.filter(e => e.type === 'FORMALITE').length
  }
}

const loadDossiers = async () => {
  loadingDossiers.value = true
  try {
    const response = await api.get('/dossiers/', {
      params: { page_size: 100, status: 'OUVERT', ordering: '-opening_date' }
    })
    dossiers.value = (response.data.results || []).map(d => ({
      id: d.id,
      display_name: `${d.reference_code} - ${d.title}`
    }))
  } catch (error) {
    console.error('Erreur chargement dossiers:', error)
  } finally {
    loadingDossiers.value = false
  }
}

const filterEvents = () => {
  let filtered = [...allEvents.value]
  
  if (filters.value.type) {
    filtered = filtered.filter(e => e.type === filters.value.type)
  }
  
  if (filters.value.dossier) {
    filtered = filtered.filter(e => e.dossier === filters.value.dossier)
  }
  
  if (filters.value.priority) {
    filtered = filtered.filter(e => e.priority === filters.value.priority)
  }
  
  events.value = formatEventsForCalendar(filtered)
  calendarOptions.value.events = events.value
}

const openCreateDialog = () => {
  isEditMode.value = false
  eventFormData.value = {
    id: null,
    type: 'RDV',
    title: '',
    dossier: null,
    location: '',
    start_date: new Date().toISOString().split('T')[0],
    start_time: '09:00',
    end_time: '10:00',
    all_day: false,
    description: '',
    reminder: '1_DAY',
    priority: 'NORMAL'
  }
  eventDialog.value = true
}

const handleDateSelect = (selectInfo) => {
  openCreateDialog()
  eventFormData.value.start_date = selectInfo.startStr.split('T')[0]
  eventFormData.value.all_day = selectInfo.allDay
}

const handleEventClick = (clickInfo) => {
  selectedEvent.value = clickInfo.event
  eventDetailsDialog.value = true
}

const editEventFromDetails = () => {
  eventDetailsDialog.value = false
  
  const event = allEvents.value.find(e => e.id === selectedEvent.value.id)
  if (!event) return
  
  isEditMode.value = true
  eventFormData.value = {
    id: event.id,
    type: event.type,
    title: event.title,
    dossier: event.dossier,
    location: event.location,
    start_date: event.start_date,
    start_time: event.start_time || '09:00',
    end_time: event.end_time || '10:00',
    all_day: event.all_day,
    description: event.description,
    reminder: event.reminder,
    priority: event.priority
  }
  
  eventDialog.value = true
}

const saveEvent = async () => {
  const { valid } = await eventForm.value.validate()
  if (!valid) return
  
  saving.value = true
  try {
    const payload = {
      type: eventFormData.value.type,
      title: eventFormData.value.title,
      dossier: eventFormData.value.dossier,
      location: eventFormData.value.location,
      start_date: eventFormData.value.start_date,
      all_day: eventFormData.value.all_day,
      description: eventFormData.value.description,
      priority: eventFormData.value.priority,
      reminder: eventFormData.value.reminder
    }
    
    if (!eventFormData.value.all_day) {
      payload.start_time = eventFormData.value.start_time
      payload.end_date = eventFormData.value.start_date
      payload.end_time = eventFormData.value.end_time
    }
    
    if (isEditMode.value) {
      await api.patch(`/agenda/events/${eventFormData.value.id}/`, payload)
    } else {
      await api.post('/agenda/events/', payload)
    }
    
    await loadEvents()
    closeEventDialog()
    
  } catch (error) {
    console.error('Erreur sauvegarde événement:', error)
    alert('Erreur lors de la sauvegarde de l\'événement')
  } finally {
    saving.value = false
  }
}

const handleEventDrop = async (dropInfo) => {
  try {
    const event = allEvents.value.find(e => e.id === dropInfo.event.id)
    if (!event) return
    
    const newDate = dropInfo.event.startStr.split('T')[0]
    const payload = {
      ...event,
      start_date: newDate,
      end_date: event.all_day ? newDate : (event.end_date || newDate)
    }
    
    await api.patch(`/agenda/events/${event.id}/`, payload)
    await loadEvents()
    
  } catch (error) {
    console.error('Erreur déplacement événement:', error)
    dropInfo.revert()
  }
}

const handleEventResize = async (resizeInfo) => {
  try {
    const event = allEvents.value.find(e => e.id === resizeInfo.event.id)
    if (!event) return
    
    const endDate = resizeInfo.event.endStr.split('T')[0]
    const payload = {
      ...event,
      end_date: endDate
    }
    
    await api.patch(`/agenda/events/${event.id}/`, payload)
    await loadEvents()
    
  } catch (error) {
    console.error('Erreur redimensionnement événement:', error)
    resizeInfo.revert()
  }
}

const handleDatesChange = (dateInfo) => {
  const start = dateInfo.startStr.split('T')[0]
  const end = dateInfo.endStr.split('T')[0]
  loadEvents(start, end)
}

const confirmDeleteEvent = () => {
  eventToDelete.value = eventFormData.value.id
  eventDialog.value = false
  deleteDialog.value = true
}

const executeDeleteEvent = async () => {
  if (!eventToDelete.value) return
  
  deleting.value = true
  try {
    await api.delete(`/agenda/events/${eventToDelete.value}/`)
    await loadEvents()
    deleteDialog.value = false
    eventToDelete.value = null
  } catch (error) {
    console.error('Erreur suppression événement:', error)
    alert('Erreur lors de la suppression de l\'événement')
  } finally {
    deleting.value = false
  }
}

const closeEventDialog = () => {
  eventDialog.value = false
  if (eventForm.value) {
    eventForm.value.reset()
  }
}

// Utilitaires
const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  }).format(new Date(dateString))
}

const formatRelativeDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = date - now
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return 'Aujourd\'hui'
  if (days === 1) return 'Demain'
  if (days === -1) return 'Hier'
  if (days > 0) return `Dans ${days} jour${days > 1 ? 's' : ''}`
  return `Il y a ${Math.abs(days)} jour${Math.abs(days) > 1 ? 's' : ''}`
}

const formatEventDateTime = (event) => {
  if (!event) return ''
  
  const start = new Date(event.start)
  let result = new Intl.DateTimeFormat('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  }).format(start)
  
  if (!event.allDay) {
    result += ' à ' + new Intl.DateTimeFormat('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    }).format(start)
    
    if (event.end) {
      const end = new Date(event.end)
      result += ' - ' + new Intl.DateTimeFormat('fr-FR', {
        hour: '2-digit',
        minute: '2-digit'
      }).format(end)
    }
  }
  
  return result
}

const getEventTypeIcon = (type) => {
  const eventType = eventTypes.find(t => t.value === type)
  return eventType?.icon || 'mdi-calendar'
}

const getEventTypeLabel = (type) => {
  const eventType = eventTypes.find(t => t.value === type)
  return eventType?.title || type
}

const getEventTypeColor = (type) => {
  const eventType = eventTypes.find(t => t.value === type)
  return eventType?.color || '#455A64'
}

const getPriorityColor = (priority) => {
  const p = priorities.find(pr => pr.value === priority)
  return p?.color || 'grey'
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadEvents(),
    loadDossiers()
  ])
})
</script>

<style scoped>
.border-t-lg {
  border-top-width: 4px !important;
}

:deep(.fc) {
  font-family: 'Roboto', sans-serif;
}

:deep(.fc-toolbar-title) {
  font-size: 1.5rem !important;
  font-weight: 700 !important;
  color: #1A237E;
}

:deep(.fc-button) {
  background-color: #1A237E !important;
  border-color: #1A237E !important;
  text-transform: capitalize !important;
}

:deep(.fc-button:hover) {
  background-color: #0D47A1 !important;
}

:deep(.fc-button-active) {
  background-color: #0D47A1 !important;
}

:deep(.fc-event) {
  border-radius: 4px;
  padding: 2px 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

:deep(.fc-event:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

:deep(.fc-daygrid-day-number) {
  font-weight: 600;
}

:deep(.fc-col-header-cell-cushion) {
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.75rem;
  color: #1A237E;
}

.custom-calendar {
  padding: 1rem;
}
</style>ss