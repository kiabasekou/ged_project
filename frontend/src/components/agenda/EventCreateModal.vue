<script setup>
import { ref, computed, watch } from 'vue'
import api from '@/plugins/axios'
import EventCreateModal from '@/components/agenda/EventCreateModal.vue'
import FullCalendar from '@fullcalendar/vue3'

const props = defineProps({
  modelValue: Boolean,
  initialDate: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'event-created'])

const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const today = new Date().toISOString().substr(0, 10)

const form = ref({
  title: '',
  type: 'AUDIENCE',
  date: props.initialDate || today,
  time: '',
  allDay: true,
  location: '',
  dossier: null,
  description: ''
})

const types = [
  { value: 'AUDIENCE', title: 'Audience / Plaidoirie', icon: 'mdi-gavel', color: 'red-darken-2' },
  { value: 'RDV', title: 'Rendez-vous client', icon: 'mdi-account-tie', color: 'indigo' },
  { value: 'FORMALITE', title: 'Formalité notariale', icon: 'mdi-file-sign', color: 'amber-darken-2' },
  { value: 'CONGE', title: 'Congé / Absence', icon: 'mdi-airplane', color: 'grey-darken-1' },
  { value: 'AUTRE', title: 'Autre événement', icon: 'mdi-calendar', color: 'blue-grey' }
]

const dossiers = ref([])
const loadingDossiers = ref(false)
const loading = ref(false)

const loadDossiers = async () => {
  loadingDossiers.value = true
  try {
    const response = await api.get('/dossiers/', { params: { page_size: 100, ordering: '-opening_date' } })
    dossiers.value = response.data.results || response.data
  } catch (err) {
    console.error('Erreur chargement dossiers', err)
  } finally {
    loadingDossiers.value = false
  }
}

const eventModal = ref(false)
const clickedDate = ref(null)

const calendarOptions = ref({
  initialView: 'dayGridMonth',
  events: []
})

const handleDateClick = (info) => {
  clickedDate.value = info.dateStr
  eventModal.value = true
}

const handleEventCreated = (newEvent) => {
  calendarOptions.value.events = [...calendarOptions.value.events, newEvent]
}

// Validation date >= aujourd’hui
const isDateValid = computed(() => form.value.date >= today)

// Validation heure si la date est aujourd’hui
const isTimeValid = computed(() => {
  if (form.value.allDay || !form.value.time) return true
  if (form.value.date > today) return true
  if (form.value.date < today) return false

  const now = new Date()
  const currentTime = now.toTimeString().substr(0, 5) // HH:MM
  return form.value.time >= currentTime
})

const submit = async () => {
  if (!isDateValid.value || !isTimeValid.value) {
    console.error('Date ou heure invalide')
    return
  }

  loading.value = true
  try {
    const newEvent = {
      title: form.value.title,
      start: form.value.allDay ? form.value.date : `${form.value.date}T${form.value.time}`,
      allDay: form.value.allDay,
      backgroundColor: types.find(t => t.value === form.value.type)?.color || '#1A237E',
      extendedProps: {
        type: form.value.type,
        location: form.value.location,
        dossier: form.value.dossier,
        description: form.value.description
      }
    }

    emit('event-created', newEvent)
    isOpen.value = false

    form.value = {
      title: '',
      type: 'AUDIENCE',
      date: today,
      time: '',
      allDay: true,
      location: '',
      dossier: null,
      description: ''
    }
  } catch (err) {
    console.error('Erreur création événement', err)
  } finally {
    loading.value = false
  }
}

watch(isOpen, (newVal) => {
  if (newVal) {
    loadDossiers()
  }
})
</script>

<template>
  <v-dialog v-model="isOpen" max-width="600" persistent>
    <v-card>
      <v-card-title class="text-h6 bg-indigo-darken-4 text-white py-4">
        <v-icon left color="white">mdi-calendar-plus</v-icon>
        Créer un événement
      </v-card-title>

      <v-card-text class="pt-6">
        <v-form @submit.prevent="submit">
          <v-row>
            <!-- Champ date -->
            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.date"
                label="Date *"
                type="date"
                variant="outlined"
                prepend-inner-icon="mdi-calendar"
                :error-messages="isDateValid ? [] : ['La date doit être >= aujourd’hui']"
              />
            </v-col>

            <!-- Champ heure -->
            <v-col cols="12" md="6" v-if="!form.allDay">
              <v-text-field
                v-model="form.time"
                label="Heure"
                type="time"
                variant="outlined"
                prepend-inner-icon="mdi-clock-outline"
                :error-messages="isTimeValid ? [] : ['Heure invalide (passée)']"
              />
            </v-col>

            <!-- autres champs inchangés -->
          </v-row>
        </v-form>
      </v-card-text>

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" @click="isOpen = false">Annuler</v-btn>
        <v-btn
          color="#1A237E"
          :loading="loading"
          @click="submit"
          :disabled="!form.title || !form.date || !isDateValid || !isTimeValid"
        >
          Créer l'événement
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <FullCalendar :options="calendarOptions" @dateClick="handleDateClick" />

  <EventCreateModal
    v-model="eventModal"
    :initial-date="clickedDate"
    @event-created="handleEventCreated"
  />
</template>