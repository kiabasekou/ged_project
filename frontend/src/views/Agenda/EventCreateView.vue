<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col cols="12">
        <!-- En-tête -->
        <div class="d-flex align-center mb-6">
          <v-btn
            icon
            variant="text"
            @click="$router.back()"
            class="mr-4"
          >
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
          <div>
            <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
              Nouvel événement
            </h1>
            <p class="text-subtitle-1 text-grey-darken-1 mt-1">
              Planifier une audience, un rendez-vous ou une formalité
            </p>
          </div>
        </div>

        <!-- Formulaire -->
        <v-card elevation="3" class="rounded-lg">
          <v-card-text class="pa-8">
            <v-form ref="eventForm" @submit.prevent="handleSubmit">
              <v-row>
                <!-- Type d'événement -->
                <v-col cols="12">
                  <v-select
                    v-model="form.type"
                    :items="eventTypes"
                    label="Type d'événement *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required]"
                    prepend-inner-icon="mdi-calendar-star"
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
                      {{ item.raw.title }}
                    </template>
                  </v-select>
                </v-col>

                <!-- Titre -->
                <v-col cols="12">
                  <v-text-field
                    v-model="form.title"
                    label="Titre de l'événement *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required, rules.maxLength(200)]"
                    counter="200"
                    prepend-inner-icon="mdi-format-title"
                    placeholder="Ex: Audience TPI Libreville - Affaire Mba c/ Nguema"
                  />
                </v-col>

                <!-- Dossier lié -->
                <v-col cols="12" md="6">
                  <v-autocomplete
                    v-model="form.dossier"
                    :items="dossiers"
                    :loading="loadingDossiers"
                    item-title="display_name"
                    item-value="id"
                    label="Dossier lié *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required]"
                    prepend-inner-icon="mdi-folder"
                    clearable
                  >
                    <template v-slot:item="{ item, props }">
                      <v-list-item v-bind="props">
                        <template v-slot:subtitle>
                          <span class="text-caption">{{ item.raw.reference_code }}</span>
                        </template>
                      </v-list-item>
                    </template>
                  </v-autocomplete>
                </v-col>

                <!-- Lieu -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.location"
                    label="Lieu"
                    variant="outlined"
                    density="comfortable"
                    prepend-inner-icon="mdi-map-marker"
                    placeholder="Ex: Tribunal de Première Instance de Libreville"
                  />
                </v-col>

                <!-- Date de début -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.start_date"
                    type="date"
                    label="Date *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required]"
                    prepend-inner-icon="mdi-calendar"
                  />
                </v-col>

                <!-- Journée entière ou horaire -->
                <v-col cols="12" md="6">
                  <v-switch
                    v-model="form.all_day"
                    label="Journée entière"
                    color="indigo"
                    hide-details
                    class="mt-2"
                  />
                </v-col>

                <!-- Horaires (si pas journée entière) -->
                <template v-if="!form.all_day">
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="form.start_time"
                      type="time"
                      label="Heure de début *"
                      variant="outlined"
                      density="comfortable"
                      :rules="form.all_day ? [] : [rules.required]"
                      prepend-inner-icon="mdi-clock-start"
                    />
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="form.end_time"
                      type="time"
                      label="Heure de fin *"
                      variant="outlined"
                      density="comfortable"
                      :rules="form.all_day ? [] : [rules.required]"
                      prepend-inner-icon="mdi-clock-end"
                    />
                  </v-col>
                </template>

                <!-- Description -->
                <v-col cols="12">
                  <v-textarea
                    v-model="form.description"
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

                <!-- Rappel -->
                <v-col cols="12" md="6">
                  <v-select
                    v-model="form.reminder"
                    :items="reminderOptions"
                    label="Rappel"
                    variant="outlined"
                    density="comfortable"
                    prepend-inner-icon="mdi-bell"
                    clearable
                  />
                </v-col>

                <!-- Priorité -->
                <v-col cols="12" md="6">
                  <v-select
                    v-model="form.priority"
                    :items="priorityOptions"
                    label="Priorité"
                    variant="outlined"
                    density="comfortable"
                    prepend-inner-icon="mdi-flag"
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
              </v-row>

              <!-- Messages d'erreur -->
              <v-expand-transition>
                <v-alert
                  v-if="error"
                  type="error"
                  variant="tonal"
                  class="mt-4"
                  closable
                  @click:close="error = null"
                >
                  {{ error }}
                </v-alert>
              </v-expand-transition>

              <!-- Actions -->
              <div class="d-flex justify-end gap-3 mt-6">
                <v-btn
                  variant="outlined"
                  color="grey"
                  @click="$router.back()"
                  :disabled="loading"
                >
                  <v-icon start>mdi-close</v-icon>
                  Annuler
                </v-btn>
                <v-btn
                  type="submit"
                  color="indigo"
                  :loading="loading"
                >
                  <v-icon start>mdi-check</v-icon>
                  Créer l'événement
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- Aide -->
        <v-card elevation="1" class="mt-6 bg-blue-grey-lighten-5">
          <v-card-text>
            <h3 class="text-subtitle-1 font-weight-bold mb-3">
              <v-icon start color="info">mdi-lightbulb</v-icon>
              Conseils
            </h3>
            <ul class="text-caption">
              <li class="mb-1">
                <strong>Audiences :</strong> Pensez à noter le numéro de chambre et le nom du juge
              </li>
              <li class="mb-1">
                <strong>Rendez-vous clients :</strong> Indiquez le nom du client dans le titre
              </li>
              <li class="mb-1">
                <strong>Formalités notariales :</strong> Précisez les pièces requises dans la description
              </li>
              <li>
                <strong>Délais critiques :</strong> Utilisez la priorité "Haute" et activez un rappel
              </li>
            </ul>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAgendaStore } from '@/stores/agenda'
import { useDossierStore } from '@/stores/dossier'

const router = useRouter()
const agendaStore = useAgendaStore()
const dossierStore = useDossierStore()

// Données
const eventForm = ref(null)
const loading = ref(false)
const loadingDossiers = ref(false)
const error = ref(null)
const dossiers = ref([])

const form = reactive({
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

// Options
const eventTypes = [
  { 
    title: 'Audience', 
    value: 'AUDIENCE', 
    icon: 'mdi-gavel',
    color: 'red-darken-2'
  },
  { 
    title: 'Rendez-vous client', 
    value: 'RDV', 
    icon: 'mdi-account-clock',
    color: 'blue'
  },
  { 
    title: 'Formalité notariale', 
    value: 'FORMALITE', 
    icon: 'mdi-file-sign',
    color: 'green'
  },
  { 
    title: 'Congé', 
    value: 'CONGE', 
    icon: 'mdi-beach',
    color: 'orange'
  },
  { 
    title: 'Autre événement', 
    value: 'AUTRE', 
    icon: 'mdi-calendar-star',
    color: 'grey'
  }
]

const reminderOptions = [
  { title: '15 minutes avant', value: '15_MIN' },
  { title: '1 heure avant', value: '1_HOUR' },
  { title: '1 jour avant', value: '1_DAY' },
  { title: '1 semaine avant', value: '1_WEEK' }
]

const priorityOptions = [
  { 
    title: 'Normale', 
    value: 'NORMAL',
    icon: 'mdi-flag',
    color: 'grey'
  },
  { 
    title: 'Haute', 
    value: 'HIGH',
    icon: 'mdi-flag',
    color: 'orange'
  },
  { 
    title: 'Urgente', 
    value: 'URGENT',
    icon: 'mdi-flag',
    color: 'red'
  }
]

// Règles de validation
const rules = {
  required: v => !!v || 'Ce champ est requis',
  maxLength: max => v => !v || v.length <= max || `Maximum ${max} caractères`
}

// Méthodes
const loadDossiers = async () => {
  loadingDossiers.value = true
  try {
    const response = await dossierStore.fetchDossiers({ 
      status: 'OUVERT',
      limit: 100 
    })
    dossiers.value = response.results.map(d => ({
      id: d.id,
      reference_code: d.reference_code,
      display_name: `${d.reference_code} - ${d.title}`
    }))
  } catch (err) {
    console.error('Erreur chargement dossiers:', err)
  } finally {
    loadingDossiers.value = false
  }
}

const handleSubmit = async () => {
  if (!eventForm.value.validate()) return

  loading.value = true
  error.value = null

  try {
    const eventData = {
      type: form.type,
      title: form.title,
      dossier: form.dossier,
      location: form.location,
      start_date: form.start_date,
      all_day: form.all_day,
      description: form.description
    }

    // Ajouter horaires si pas journée entière
    if (!form.all_day) {
      eventData.start_time = form.start_time
      eventData.end_date = form.start_date
      eventData.end_time = form.end_time
    }

    await agendaStore.createEvent(eventData)

    // Redirection vers l'agenda
    router.push({ name: 'Agenda' })
  } catch (err) {
    console.error('Erreur création événement:', err)
    error.value = err.response?.data?.detail || 
                  'Erreur lors de la création de l\'événement'
  } finally {
    loading.value = false
  }
}

// Chargement initial
onMounted(() => {
  loadDossiers()
})
</script>

<style scoped>
.gap-3 {
  gap: 12px;
}
</style>