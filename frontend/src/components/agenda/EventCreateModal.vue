<template>
  <v-dialog v-model="isOpen" max-width="700" persistent>
    <v-card>
      <v-card-title class="bg-indigo-darken-4 text-white py-4">
        <v-icon start color="white">mdi-calendar-plus</v-icon>
        Nouvel événement
      </v-card-title>

      <v-card-text class="pa-6">
        <v-form ref="eventForm" v-model="formValid">
          <v-row>
            <!-- Type -->
            <v-col cols="12">
              <v-select
                v-model="form.type"
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
                v-model="form.title"
                label="Titre *"
                variant="outlined"
                density="comfortable"
                :rules="[rules.required, rules.maxLength(200)]"
                counter="200"
                prepend-inner-icon="mdi-format-title"
                placeholder="Ex: Audience TPI Libreville"
              />
            </v-col>

            <!-- Date -->
            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.start_date"
                type="date"
                label="Date *"
                variant="outlined"
                density="comfortable"
                :rules="[rules.required, rules.dateNotPast]"
                prepend-inner-icon="mdi-calendar"
              />
            </v-col>

            <!-- Toute la journée -->
            <v-col cols="12" md="6" class="d-flex align-center">
              <v-switch
                v-model="form.all_day"
                label="Toute la journée"
                color="indigo"
                hide-details
                inset
              />
            </v-col>

            <!-- Horaires -->
            <template v-if="!form.all_day">
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.start_time"
                  type="time"
                  label="Heure début *"
                  variant="outlined"
                  density="comfortable"
                  :rules="[rules.required]"
                  prepend-inner-icon="mdi-clock-start"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.end_time"
                  type="time"
                  label="Heure fin"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-clock-end"
                />
              </v-col>
            </template>

            <!-- Lieu -->
            <v-col cols="12">
              <v-text-field
                v-model="form.location"
                label="Lieu"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-map-marker"
                placeholder="Ex: TPI Libreville"
              />
            </v-col>

            <!-- Dossier -->
            <v-col cols="12">
              <v-autocomplete
                v-model="form.dossier"
                :items="dossiers"
                :loading="loadingDossiers"
                item-title="display_name"
                item-value="id"
                label="Dossier lié"
                variant="outlined"
                density="comfortable"
                clearable
                prepend-inner-icon="mdi-folder"
              />
            </v-col>

            <!-- Priorité -->
            <v-col cols="12" md="6">
              <v-select
                v-model="form.priority"
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
                v-model="form.reminder"
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
                v-model="form.description"
                label="Description / Notes"
                variant="outlined"
                density="comfortable"
                rows="3"
                prepend-inner-icon="mdi-text"
                placeholder="Notes importantes..."
              />
            </v-col>
          </v-row>
        </v-form>

        <!-- Erreurs -->
        <v-expand-transition>
          <v-alert
            v-if="error"
            type="error"
            variant="tonal"
            closable
            class="mt-4"
            @click:close="error = null"
          >
            {{ error }}
          </v-alert>
        </v-expand-transition>
      </v-card-text>

      <v-card-actions class="px-6 pb-6">
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
          :disabled="!formValid"
          @click="submit"
        >
          Créer l'événement
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useAgendaStore } from '@/stores/agenda'
import api from '@/plugins/axios'

const props = defineProps({
  modelValue: Boolean,
  initialDate: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'created'])

const agendaStore = useAgendaStore()

// État
const eventForm = ref(null)
const formValid = ref(false)
const loading = ref(false)
const loadingDossiers = ref(false)
const error = ref(null)
const dossiers = ref([])

// Computed
const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// Formulaire
const form = ref({
  type: 'RDV',
  title: '',
  start_date: props.initialDate || new Date().toISOString().split('T')[0],
  start_time: '09:00',
  end_time: '10:00',
  all_day: false,
  location: '',
  dossier: null,
  priority: 'NORMAL',
  reminder: '1_DAY',
  description: ''
})

// Configuration
const eventTypes = [
  { 
    title: 'Audience', 
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
    title: 'Congé', 
    value: 'CONGE', 
    icon: 'mdi-airplane',
    color: '#757575'
  },
  { 
    title: 'Autre', 
    value: 'AUTRE', 
    icon: 'mdi-calendar-star',
    color: '#455A64'
  }
]

const priorities = [
  { title: 'Normale', value: 'NORMAL', color: 'grey' },
  { title: 'Haute', value: 'HIGH', color: 'orange' },
  { title: 'Urgente', value: 'URGENT', color: 'red' }
]

const reminders = [
  { title: '15 minutes avant', value: '15_MIN' },
  { title: '1 heure avant', value: '1_HOUR' },
  { title: '1 jour avant', value: '1_DAY' },
  { title: '1 semaine avant', value: '1_WEEK' }
]

// Règles
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
const loadDossiers = async () => {
  loadingDossiers.value = true
  try {
    const response = await api.get('/dossiers/', {
      params: { 
        page_size: 100, 
        status: 'OUVERT',
        ordering: '-opening_date' 
      }
    })
    dossiers.value = (response.data.results || []).map(d => ({
      id: d.id,
      display_name: `${d.reference_code} - ${d.title}`
    }))
  } catch (err) {
    console.error('Erreur chargement dossiers:', err)
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
      type: form.value.type,
      title: form.value.title,
      start_date: form.value.start_date,
      all_day: form.value.all_day,
      priority: form.value.priority,
      description: form.value.description
    }
    
    // Champs optionnels
    if (form.value.dossier) payload.dossier = form.value.dossier
    if (form.value.location) payload.location = form.value.location
    if (form.value.reminder) payload.reminder = form.value.reminder
    
    // Horaires si pas toute la journée
    if (!form.value.all_day) {
      if (form.value.start_time) payload.start_time = form.value.start_time
      if (form.value.end_time) payload.end_time = form.value.end_time
      payload.end_date = form.value.start_date
    }
    
    const newEvent = await agendaStore.createEvent(payload)
    
    // Succès
    emit('created', newEvent)
    close()
    
  } catch (err) {
    console.error('Erreur création événement:', err)
    error.value = agendaStore.error || 'Erreur lors de la création de l\'événement'
  } finally {
    loading.value = false
  }
}

const close = () => {
  isOpen.value = false
  if (eventForm.value) {
    eventForm.value.reset()
  }
  error.value = null
}

// Watch ouverture dialog
watch(isOpen, (newVal) => {
  if (newVal) {
    loadDossiers()
    // Reset form
    form.value = {
      type: 'RDV',
      title: '',
      start_date: props.initialDate || new Date().toISOString().split('T')[0],
      start_time: '09:00',
      end_time: '10:00',
      all_day: false,
      location: '',
      dossier: null,
      priority: 'NORMAL',
      reminder: '1_DAY',
      description: ''
    }
  }
})
</script>

<style scoped>
/* Styles spécifiques si nécessaire */
</style>