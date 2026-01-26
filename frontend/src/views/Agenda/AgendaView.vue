<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAgendaStore } from '@/stores/agenda'
import { useDossierStore } from '@/stores/dossier'

const router = useRouter()
const route = useRoute()
const agendaStore = useAgendaStore()
const dossierStore = useDossierStore()

// Références
const eventForm = ref(null) // Référence au formulaire
const loading = ref(false)
const loadingDossiers = ref(false)
const error = ref(null)
const dossiers = ref([])

// État du formulaire
const form = reactive({
  type: 'RDV',
  title: '',
  dossier: null,
  location: '',
  start_date: new Date().toISOString().split('T')[0], // Aujourd'hui par défaut
  start_time: '09:00',
  end_time: '10:00',
  all_day: false,
  description: '',
  reminder: '1_DAY',
  priority: 'NORMAL'
})

// Options statiques (Icones et Couleurs)
const eventTypes = [
  { title: 'Audience', value: 'AUDIENCE', icon: 'mdi-gavel', color: 'red-darken-2' },
  { title: 'Rendez-vous client', value: 'RDV', icon: 'mdi-account-clock', color: 'blue' },
  { title: 'Formalité notariale', value: 'FORMALITE', icon: 'mdi-file-sign', color: 'green' },
  { title: 'Congé', value: 'CONGE', icon: 'mdi-beach', color: 'orange' },
  { title: 'Autre événement', value: 'AUTRE', icon: 'mdi-calendar-star', color: 'grey' }
]

const reminderOptions = [
  { title: '15 minutes avant', value: '15_MIN' },
  { title: '1 heure avant', value: '1_HOUR' },
  { title: '1 jour avant', value: '1_DAY' },
  { title: '1 semaine avant', value: '1_WEEK' }
]

const priorityOptions = [
  { title: 'Normale', value: 'NORMAL', icon: 'mdi-flag', color: 'grey' },
  { title: 'Haute', value: 'HIGH', icon: 'mdi-flag', color: 'orange' },
  { title: 'Urgente', value: 'URGENT', icon: 'mdi-flag', color: 'red' }
]

// Règles de validation
const rules = {
  required: v => !!v || 'Ce champ est requis',
  maxLength: max => v => !v || v.length <= max || `Maximum ${max} caractères`,
  // Validation conditionnelle pour les heures
  requiredIfTime: v => form.all_day || !!v || 'Heure requise'
}

// Chargement des dossiers pour l'autocomplete
const loadDossiers = async () => {
  loadingDossiers.value = true
  try {
    // On charge tous les dossiers OUVERTS
    const response = await dossierStore.fetchDossiers({ 
      status: 'OUVERT',
      limit: 100 
    })
    
    // Mapping pour l'affichage
    dossiers.value = response.results.map(d => ({
      id: d.id,
      reference_code: d.reference_code,
      title: d.title,
      display_name: `${d.reference_code} - ${d.title}`
    }))

    // Pré-remplissage si un ID est passé dans l'URL (ex: ?dossier_id=123)
    if (route.query.dossier_id) {
        // On convertit en Int ou String selon votre ID
        const preselectedId = route.query.dossier_id 
        // Vérifier si ce dossier est dans la liste chargée
        const exists = dossiers.value.find(d => d.id == preselectedId)
        if (exists) {
            form.dossier = exists.id
        }
    }

  } catch (err) {
    console.error('Erreur chargement dossiers:', err)
  } finally {
    loadingDossiers.value = false
  }
}

// Soumission du formulaire
const handleSubmit = async () => {
  // 1. Validation Vuetify 3 (Asynchrone)
  const { valid } = await eventForm.value.validate()
  if (!valid) return

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
      description: form.description,
      priority: form.priority,
      reminder: form.reminder || null
    }

    // Gestion des heures si ce n'est pas "Toute la journée"
    if (!form.all_day) {
      eventData.start_time = form.start_time
      eventData.end_time = form.end_time
      // Par défaut, fin le même jour
      eventData.end_date = form.start_date 
    } else {
        // Nettoyage pour éviter d'envoyer des heures fantômes
        eventData.start_time = null
        eventData.end_time = null
    }

    await agendaStore.createEvent(eventData)

    // Succès -> Retour à l'agenda ou au dossier précédent
    router.back() 
    
  } catch (err) {
    console.error('Erreur création événement:', err)
    error.value = err.response?.data?.detail || 
                  'Une erreur est survenue lors de la création.'
  } finally {
    loading.value = false
  }
}

// Initialisation
onMounted(() => {
  loadDossiers()
})
</script>

<template>
  <v-container fluid class="pa-6">
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        
        <div class="d-flex align-center mb-6">
          <v-btn
            icon="mdi-arrow-left"
            variant="text"
            @click="router.back()"
            class="mr-4"
          />
          <div>
            <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
              Nouvel événement
            </h1>
            <p class="text-subtitle-1 text-grey-darken-1 mt-1">
              Planifier une audience, un rendez-vous ou une formalité
            </p>
          </div>
        </div>

        <v-card elevation="2" class="rounded-lg border">
          <v-card-text class="pa-8">
            <v-form ref="eventForm" @submit.prevent="handleSubmit">
              <v-row>
                
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
                      <v-list-item v-bind="props" :title="item.title">
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

                <v-col cols="12">
                  <v-text-field
                    v-model="form.title"
                    label="Titre de l'événement *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required, rules.maxLength(200)]"
                    counter="200"
                    prepend-inner-icon="mdi-format-title"
                    placeholder="Ex: Audience TPI Libreville - Affaire Mba"
                  />
                </v-col>

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
                    prepend-inner-icon="mdi-folder-search"
                    clearable
                    no-data-text="Aucun dossier trouvé"
                  >
                    <template v-slot:item="{ item, props }">
                      <v-list-item v-bind="props" :title="item.raw.reference_code" :subtitle="item.raw.title">
                      </v-list-item>
                    </template>
                  </v-autocomplete>
                </v-col>

                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.location"
                    label="Lieu"
                    variant="outlined"
                    density="comfortable"
                    prepend-inner-icon="mdi-map-marker"
                    placeholder="Ex: Tribunal de Première Instance"
                  />
                </v-col>

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

                <v-col cols="12" md="6" class="d-flex align-center">
                  <v-switch
                    v-model="form.all_day"
                    label="Toute la journée"
                    color="indigo"
                    hide-details
                    inset
                  />
                </v-col>

                <v-expand-transition>
                  <div v-if="!form.all_day" class="d-flex flex-wrap w-100">
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="form.start_time"
                        type="time"
                        label="Heure de début *"
                        variant="outlined"
                        density="comfortable"
                        :rules="[rules.requiredIfTime]"
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
                        :rules="[rules.requiredIfTime]"
                        prepend-inner-icon="mdi-clock-end"
                      />
                    </v-col>
                  </div>
                </v-expand-transition>

                <v-col cols="12" md="6">
                   <v-select
                    v-model="form.priority"
                    :items="priorityOptions"
                    label="Priorité"
                    variant="outlined"
                    density="comfortable"
                    prepend-inner-icon="mdi-flag"
                  >
                     <template v-slot:selection="{ item }">
                      <v-icon :color="item.raw.color" start>{{ item.raw.icon }}</v-icon>
                      {{ item.title }}
                    </template>
                    <template v-slot:item="{ item, props }">
                        <v-list-item v-bind="props">
                            <template v-slot:prepend>
                                <v-icon :color="item.raw.color">{{ item.raw.icon }}</v-icon>
                            </template>
                        </v-list-item>
                    </template>
                  </v-select>
                </v-col>

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
                    placeholder="Notes importantes..."
                  />
                </v-col>
              </v-row>

              <v-expand-transition>
                <v-alert
                  v-if="error"
                  type="error"
                  variant="tonal"
                  class="mt-4 mb-4"
                  closable
                  @click:close="error = null"
                >
                  {{ error }}
                </v-alert>
              </v-expand-transition>

              <div class="d-flex justify-end gap-3 mt-6">
                <v-btn
                  variant="outlined"
                  color="grey-darken-1"
                  @click="router.back()"
                  :disabled="loading"
                  size="large"
                >
                  Annuler
                </v-btn>
                
                <v-btn
                  type="submit"
                  color="indigo-darken-4"
                  :loading="loading"
                  size="large"
                  prepend-icon="mdi-check"
                >
                  Créer l'événement
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>

      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.gap-3 {
  gap: 12px;
}
</style>