<!-- ============================================================================
CORRECTION : frontend/src/components/agenda/EventCreateModal.vue

============================================================================ -->

<script setup>
import { ref, reactive, watch, computed, onMounted, nextTick } from 'vue'
import { useAgendaStore } from '@/stores/agenda'
import { useDossierStore } from '@/stores/dossier'

// Props & Emits
const props = defineProps({
  initialDate: {
    type: String,
    default: () => new Date().toISOString().split('T')[0]
  }
})

const emit = defineEmits(['created', 'close'])

// Stores
const agendaStore = useAgendaStore()
const dossierStore = useDossierStore()

// State
const isOpen = ref(false)
const eventForm = ref(null)
const loading = ref(false)
const loadingDossiers = ref(false)
const error = ref(null)
const dossiers = ref([])

// Form data
const form = reactive({
  type: 'RDV',
  title: '',
  start_date: props.initialDate,
  start_time: '09:00',
  end_time: '10:00',
  all_day: false,
  location: '',
  dossier: null,
  priority: 'NORMAL',
  reminder: '1_DAY',
  description: ''
})

// Types d'événements
const eventTypes = [
  { value: 'AUDIENCE', title: 'Audience / Plaidoirie', icon: 'mdi-gavel', color: 'red-darken-2' },
  { value: 'RDV', title: 'Rendez-vous client', icon: 'mdi-calendar-account', color: 'blue' },
  { value: 'FORMALITE', title: 'Formalité notariale', icon: 'mdi-file-sign', color: 'purple' },
  { value: 'CONGE', title: 'Congé / Absence', icon: 'mdi-beach', color: 'green-darken-1' },
  { value: 'AUTRE', title: 'Autre événement', icon: 'mdi-calendar-blank', color: 'grey-darken-1' }
]

// Priorités
const priorities = [
  { value: 'LOW', title: 'Basse', icon: 'mdi-flag-outline', color: 'blue-grey' },
  { value: 'NORMAL', title: 'Normale', icon: 'mdi-flag', color: 'grey' },
  { value: 'HIGH', title: 'Haute', icon: 'mdi-flag', color: 'orange' },
  { value: 'URGENT', title: 'Urgente', icon: 'mdi-flag', color: 'red' }
]

// Rappels
const reminders = [
  { value: 'NONE', title: 'Aucun rappel' },
  { value: '15_MIN', title: '15 minutes avant' },
  { value: '1_HOUR', title: '1 heure avant' },
  { value: '1_DAY', title: '1 jour avant' },
  { value: '1_WEEK', title: '1 semaine avant' }
]

// Computed
const selectedEventType = computed(() => {
  return eventTypes.find(t => t.value === form.type) || { icon: 'mdi-calendar-plus', color: 'indigo' }
})

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

// Méthodes
const open = () => {
  isOpen.value = true
}

const close = () => {
  isOpen.value = false
  error.value = null
  emit('close')
}

const resetForm = () => {
  form.type = 'RDV'
  form.title = ''
  form.start_date = props.initialDate || new Date().toISOString().split('T')[0]
  form.start_time = '09:00'
  form.end_time = '10:00'
  form.all_day = false
  form.location = ''
  form.dossier = null
  form.priority = 'NORMAL'
  form.reminder = '1_DAY'
  form.description = ''
  error.value = null

  nextTick(() => {
    if (eventForm.value) {
      eventForm.value.resetValidation()
    }
  })
}

const loadDossiers = async () => {
  loadingDossiers.value = true
  try {
    await dossierStore.fetchList({ 
      status: 'OUVERT',
      page_size: 100,
      ordering: '-opening_date'
    })
    
    dossiers.value = dossierStore.list.map(d => ({
      value: d.id,
      title: `${d.reference_code} - ${d.title}`
    }))
  } catch (err) {
    console.error('Erreur chargement dossiers:', err)
    error.value = 'Impossible de charger les dossiers ouverts'
  } finally {
    loadingDossiers.value = false
  }
}

const submit = async () => {
  const { valid } = await eventForm.value.validate()
  if (!valid) return

  loading.value = true
  error.value = null

  try {
    const payload = {
      type: form.type,
      title: form.title,
      start_date: form.start_date,
      all_day: form.all_day,
      priority: form.priority,
      reminder: form.reminder
    }

    if (form.dossier) payload.dossier = form.dossier
    if (form.location) payload.location = form.location
    if (form.description) payload.description = form.description

    if (!form.all_day) {
      payload.start_time = form.start_time
      payload.end_time = form.end_time
      payload.end_date = form.start_date
    }

    const newEvent = await agendaStore.createEvent(payload)
    emit('created', newEvent)
    close()

  } catch (err) {
    console.error('Erreur création événement:', err)

    if (err.response?.data) {
      const errors = err.response.data
      if (typeof errors === 'object' && !Array.isArray(errors)) {
        error.value = Object.entries(errors)
          .map(([field, messages]) => {
            const labels = {
              title: 'Titre',
              start_date: 'Date',
              start_time: 'Heure de début',
              end_time: 'Heure de fin',
              type: 'Type d\'événement',
              dossier: 'Dossier'
            }
            const label = labels[field] || field.charAt(0).toUpperCase() + field.slice(1)
            const msg = Array.isArray(messages) ? messages.join(', ') : messages
            return `• ${label} : ${msg}`
          })
          .join('\n')
      } else {
        error.value = errors.detail || errors.non_field_errors?.[0] || 'Erreur lors de la création'
      }
    } else {
      error.value = 'Impossible de contacter le serveur'
    }
  } finally {
    loading.value = false
  }
}

// Watch pour ouverture
watch(isOpen, (newVal) => {
  if (newVal) {
    resetForm()
    loadDossiers()
  }
})

// Expose open method
defineExpose({ open })
</script>

<template>
  <v-dialog v-model="isOpen" max-width="700" persistent>
    <v-card>
      <!-- En-tête avec icône dynamique -->
      <v-card-title class="bg-indigo-darken-4 text-white py-4 d-flex align-center">
        <v-icon :color="selectedEventType.color" start size="32">
          {{ selectedEventType.icon }}
        </v-icon>
        <span class="text-h6 font-weight-bold">Nouvel événement</span>
      </v-card-title>

      <!-- Contenu -->
      <v-card-text class="pa-6">
        <v-form ref="eventForm" @submit.prevent="submit">
          <!-- Type d'événement -->
          <v-select
            v-model="form.type"
            :items="eventTypes"
            item-title="title"
            item-value="value"
            label="Type d'événement *"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-shape"
            :rules="[rules.required]"
            class="mb-4"
          >
            <template #item="{ props, item }">
              <v-list-item v-bind="props">
                <template #prepend>
                  <v-icon :color="item.raw.color" class="mr-3">{{ item.raw.icon }}</v-icon>
                </template>
                <template #title>
                  {{ item.title }}
                </template>
              </v-list-item>
            </template>
            <template #selection="{ item }">
              <v-icon :color="item.raw.color" start>{{ item.raw.icon }}</v-icon>
              {{ item.title }}
            </template>
          </v-select>

          <!-- Titre -->
          <v-text-field
            v-model="form.title"
            label="Titre de l'événement *"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-format-title"
            placeholder="Ex: Audience TPI - Affaire Mba c/ Nguema"
            :rules="[rules.required, rules.maxLength(200)]"
            counter="200"
            autofocus
            class="mb-4"
          />

          <!-- Dossier lié -->
          <v-autocomplete
            v-model="form.dossier"
            :items="dossiers"
            item-title="title"
            item-value="value"
            label="Dossier lié (optionnel)"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-folder-search"
            :loading="loadingDossiers"
            clearable
            class="mb-4"
          />

          <!-- Date -->
          <v-text-field
            v-model="form.start_date"
            type="date"
            label="Date *"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-calendar"
            :rules="[rules.required, rules.dateNotPast]"
            class="mb-4"
          />

          <!-- Journée entière -->
          <v-checkbox
            v-model="form.all_day"
            label="Événement sur toute la journée"
            color="indigo-darken-4"
            hide-details
            class="mb-4"
          />

          <!-- Horaires conditionnels -->
          <v-row v-if="!form.all_day" class="mb-4">
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="form.start_time"
                type="time"
                label="Heure de début *"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-clock-start"
                :rules="[rules.required]"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="form.end_time"
                type="time"
                label="Heure de fin *"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-clock-end"
                :rules="[rules.required]"
              />
            </v-col>
          </v-row>

          <!-- Lieu -->
          <v-text-field
            v-model="form.location"
            label="Lieu (optionnel)"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-map-marker"
            placeholder="Ex: Tribunal de Première Instance"
            class="mb-4"
          />

          <!-- Priorité -->
          <v-select
            v-model="form.priority"
            :items="priorities"
            item-title="title"
            item-value="value"
            label="Priorité"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-flag"
            class="mb-4"
          >
            <template #item="{ props, item }">
              <v-list-item v-bind="props">
                <template #prepend>
                  <v-icon :color="item.raw.color" class="mr-3">{{ item.raw.icon }}</v-icon>
                </template>
              </v-list-item>
            </template>
            <template #selection="{ item }">
              <v-icon :color="item.raw.color" start>{{ item.raw.icon }}</v-icon>
              {{ item.title }}
            </template>
          </v-select>

          <!-- Rappel -->
          <v-select
            v-model="form.reminder"
            :items="reminders"
            item-title="title"
            item-value="value"
            label="Rappel"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-bell"
            clearable
            class="mb-4"
          />

          <!-- Description -->
          <v-textarea
            v-model="form.description"
            label="Description / Notes (optionnel)"
            variant="outlined"
            density="comfortable"
            rows="3"
            prepend-inner-icon="mdi-text"
            placeholder="Pièces à apporter, contacts, remarques importantes..."
            :rules="[rules.maxLength(1000)]"
            counter="1000"
            class="mb-4"
          />

          <!-- Erreur -->
          <v-alert
            v-if="error"
            type="error"
            variant="tonal"
            class="mb-4"
            closable
            @click:close="error = null"
          >
            <div class="text-body-2" style="white-space: pre-line;">{{ error }}</div>
          </v-alert>
        </v-form>
      </v-card-text>

      <!-- Actions -->
      <v-card-actions class="pa-6 pt-0">
        <v-spacer />
        <v-btn
          variant="text"
          @click="close"
          :disabled="loading"
        >
          Annuler
        </v-btn>
        <v-btn
          color="indigo-darken-4"
          variant="elevated"
          :loading="loading"
          prepend-icon="mdi-check"
          @click="submit"
        >
          Créer l'événement
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>