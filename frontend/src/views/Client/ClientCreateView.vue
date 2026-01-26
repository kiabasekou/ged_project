<template>
  <v-container fluid class="pa-6">
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        
        <!-- En-tête -->
        <div class="d-flex align-center mb-6">
          <v-btn
            icon="mdi-arrow-left"
            variant="text"
            @click="router.back()"
            class="mr-4"
          />
          <div>
            <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
              Nouveau Client
            </h1>
            <p class="text-subtitle-1 text-grey-darken-1 mt-1">
              Enregistrement d'un nouveau mandant au cabinet
            </p>
          </div>
        </div>

        <!-- Formulaire principal -->
        <v-card elevation="2" class="rounded-lg">
          <v-card-text class="pa-8">
            <v-form ref="clientForm" v-model="formValid" @submit.prevent="submitForm">
              
              <!-- Sélection type de client -->
              <v-card variant="outlined" class="mb-6 pa-4 bg-grey-lighten-4">
                <div class="text-subtitle-1 font-weight-bold mb-3 text-indigo-darken-4">
                  <v-icon start>mdi-account-circle</v-icon>
                  Nature juridique du client *
                </div>
                <v-radio-group 
                  v-model="clientData.client_type" 
                  inline 
                  hide-details
                  @update:model-value="handleTypeChange"
                >
                  <v-radio 
                    label="Personne Physique" 
                    value="PHYSIQUE" 
                    color="indigo"
                  >
                    <template v-slot:label>
                      <div class="d-flex align-center">
                        <v-icon start color="indigo">mdi-account</v-icon>
                        <span class="font-weight-medium">Personne Physique</span>
                      </div>
                    </template>
                  </v-radio>
                  
                  <v-radio 
                    label="Personne Morale" 
                    value="MORALE" 
                    color="amber-darken-3"
                  >
                    <template v-slot:label>
                      <div class="d-flex align-center">
                        <v-icon start color="amber-darken-3">mdi-domain</v-icon>
                        <span class="font-weight-medium">Personne Morale (Société)</span>
                      </div>
                    </template>
                  </v-radio>
                </v-radio-group>
              </v-card>

              <!-- Formulaire Personne Physique -->
              <v-expand-transition>
                <div v-if="clientData.client_type === 'PHYSIQUE'">
                  <h3 class="text-h6 font-weight-bold mb-4 text-indigo-darken-4">
                    <v-icon start>mdi-card-account-details</v-icon>
                    Informations personnelles
                  </h3>
                  
                  <v-row>
                    <!-- Nom -->
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="clientData.last_name"
                        label="Nom *"
                        variant="outlined"
                        density="comfortable"
                        :rules="[rules.required, rules.nameFormat]"
                        prepend-inner-icon="mdi-account"
                        placeholder="Ex: MBA"
                        hint="Nom de famille en majuscules"
                        persistent-hint
                      />
                    </v-col>

                    <!-- Prénom -->
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="clientData.first_name"
                        label="Prénom(s) *"
                        variant="outlined"
                        density="comfortable"
                        :rules="[rules.required]"
                        prepend-inner-icon="mdi-account"
                        placeholder="Ex: Jean-Pierre"
                      />
                    </v-col>

                    <!-- Date de naissance -->
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="clientData.date_of_birth"
                        type="date"
                        label="Date de naissance"
                        variant="outlined"
                        density="comfortable"
                        :rules="[rules.ageValid]"
                        prepend-inner-icon="mdi-calendar"
                        hint="Doit être majeur (18 ans)"
                        persistent-hint
                      />
                    </v-col>

                    <!-- Lieu de naissance -->
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="clientData.place_of_birth"
                        label="Lieu de naissance"
                        variant="outlined"
                        density="comfortable"
                        prepend-inner-icon="mdi-map-marker"
                        placeholder="Ex: Libreville, Gabon"
                      />
                    </v-col>

                    <!-- Type de pièce -->
                    <v-col cols="12" md="4">
                      <v-select
                        v-model="clientData.ni_type"
                        :items="idTypes"
                        label="Type de pièce *"
                        variant="outlined"
                        density="comfortable"
                        :rules="[rules.required]"
                        prepend-inner-icon="mdi-card-account-details"
                      />
                    </v-col>

                    <!-- Numéro de pièce -->
                    <v-col cols="12" md="8">
                      <v-text-field
                        v-model="clientData.ni_number"
                        :label="`Numéro ${clientData.ni_type} *`"
                        variant="outlined"
                        density="comfortable"
                        :rules="[rules.required, rules.idNumberFormat]"
                        prepend-inner-icon="mdi-numeric"
                        :placeholder="getIdPlaceholder()"
                        :hint="getIdHint()"
                        persistent-hint
                      />
                    </v-col>
                  </v-row>
                </div>
              </v-expand-transition>

              <!-- Formulaire Personne Morale -->
              <v-expand-transition>
                <div v-if="clientData.client_type === 'MORALE'">
                  <h3 class="text-h6 font-weight-bold mb-4 text-amber-darken-3">
                    <v-icon start>mdi-domain</v-icon>
                    Informations société
                  </h3>
                  
                  <v-row>
                    <!-- Raison sociale -->
                    <v-col cols="12">
                      <v-text-field
                        v-model="clientData.company_name"
                        label="Raison sociale *"
                        variant="outlined"
                        density="comfortable"
                        :rules="[rules.required]"
                        prepend-inner-icon="mdi-domain"
                        placeholder="Ex: GABONAISE D'EXPLOITATION SARL"
                      />
                    </v-col>

                    <!-- RCCM -->
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="clientData.rccm"
                        label="RCCM (OHADA) *"
                        variant="outlined"
                        density="comfortable"
                        :rules="[rules.required, rules.rccmFormat]"
                        prepend-inner-icon="mdi-file-certificate"
                        placeholder="GA-LBV-2025-A12-12345"
                        hint="Format: GA-LBV-YYYY-AXX-NNNNN"
                        persistent-hint
                      >
                        <template v-slot:append-inner>
                          <v-tooltip text="Registre du Commerce et du Crédit Mobilier">
                            <template v-slot:activator="{ props }">
                              <v-icon v-bind="props" color="grey">mdi-information</v-icon>
                            </template>
                          </v-tooltip>
                        </template>
                      </v-text-field>
                    </v-col>

                    <!-- NIF -->
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="clientData.nif"
                        label="NIF (DGI) *"
                        variant="outlined"
                        density="comfortable"
                        :rules="[rules.required, rules.nifFormat]"
                        prepend-inner-icon="mdi-file-document"
                        placeholder="123456A"
                        hint="Format: 6 chiffres + 1 lettre"
                        persistent-hint
                      >
                        <template v-slot:append-inner>
                          <v-tooltip text="Numéro d'Identification Fiscale (DGI Gabon)">
                            <template v-slot:activator="{ props }">
                              <v-icon v-bind="props" color="grey">mdi-information</v-icon>
                            </template>
                          </v-tooltip>
                        </template>
                      </v-text-field>
                    </v-col>

                    <!-- Forme juridique -->
                    <v-col cols="12" md="6">
                      <v-select
                        v-model="clientData.legal_form"
                        :items="legalForms"
                        label="Forme juridique"
                        variant="outlined"
                        density="comfortable"
                        clearable
                        prepend-inner-icon="mdi-scale-balance"
                      />
                    </v-col>

                    <!-- Secteur d'activité -->
                    <v-col cols="12" md="6">
                      <v-autocomplete
                        v-model="clientData.business_sector"
                        :items="businessSectors"
                        label="Secteur d'activité"
                        variant="outlined"
                        density="comfortable"
                        clearable
                        prepend-inner-icon="mdi-briefcase"
                      />
                    </v-col>

                    <!-- Représentant légal -->
                    <v-col cols="12">
                      <v-text-field
                        v-model="clientData.representative_name"
                        label="Représentant légal"
                        variant="outlined"
                        density="comfortable"
                        prepend-inner-icon="mdi-account-tie"
                        placeholder="Ex: M. Jean OBAME, Gérant"
                        hint="Nom et qualité du représentant"
                        persistent-hint
                      />
                    </v-col>
                  </v-row>
                </div>
              </v-expand-transition>

              <v-divider class="my-8" />

              <!-- Coordonnées (Commun) -->
              <h3 class="text-h6 font-weight-bold mb-4 text-indigo-darken-4">
                <v-icon start>mdi-contact-mail</v-icon>
                Coordonnées de contact
              </h3>

              <v-row>
                <!-- Email -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="clientData.email"
                    type="email"
                    label="Email"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.email]"
                    prepend-inner-icon="mdi-email"
                    placeholder="contact@exemple.ga"
                  />
                </v-col>

                <!-- Téléphone principal -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="clientData.phone_primary"
                    label="Téléphone principal *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required, rules.phoneFormat]"
                    prepend-inner-icon="mdi-phone"
                    placeholder="+241 XX XX XX XX"
                    hint="Format international recommandé"
                    persistent-hint
                  />
                </v-col>

                <!-- Téléphone secondaire -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="clientData.phone_secondary"
                    label="Téléphone secondaire"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.phoneFormat]"
                    prepend-inner-icon="mdi-phone-plus"
                    placeholder="+241 XX XX XX XX"
                  />
                </v-col>
              </v-row>

              <v-divider class="my-8" />

              <!-- Adresse postale -->
              <h3 class="text-h6 font-weight-bold mb-4 text-indigo-darken-4">
                <v-icon start>mdi-map-marker</v-icon>
                Adresse postale
              </h3>

              <v-row>
                <!-- Adresse -->
                <v-col cols="12">
                  <v-textarea
                    v-model="clientData.address_line"
                    label="Adresse complète"
                    variant="outlined"
                    density="comfortable"
                    rows="2"
                    prepend-inner-icon="mdi-home"
                    placeholder="Ex: BP 1234, Avenue du Colonel Parant"
                  />
                </v-col>

                <!-- Ville -->
                <v-col cols="12" md="4">
                  <v-autocomplete
                    v-model="clientData.city"
                    :items="gabonCities"
                    label="Ville *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required]"
                    prepend-inner-icon="mdi-city"
                    @update:model-value="handleCityChange"
                  />
                </v-col>

                <!-- Quartier (si Libreville) -->
                <v-col cols="12" md="4" v-if="clientData.city === 'Libreville'">
                  <v-autocomplete
                    v-model="clientData.neighborhood"
                    :items="librevilleNeighborhoods"
                    label="Quartier"
                    variant="outlined"
                    density="comfortable"
                    clearable
                    prepend-inner-icon="mdi-home-group"
                  />
                </v-col>

                <!-- Pays -->
                <v-col cols="12" md="4">
                  <v-text-field
                    v-model="clientData.country"
                    label="Pays *"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required]"
                    prepend-inner-icon="mdi-flag"
                    readonly
                  />
                </v-col>
              </v-row>

              <v-divider class="my-8" />

              <!-- Consentement RGPD -->
              <v-card variant="outlined" class="pa-4 bg-blue-grey-lighten-5">
                <div class="d-flex align-center">
                  <v-checkbox
                    v-model="clientData.consent_given"
                    color="indigo"
                    hide-details
                    class="mr-3"
                  />
                  <div class="flex-grow-1">
                    <div class="font-weight-bold">Consentement RGPD *</div>
                    <div class="text-caption text-grey-darken-1 mt-1">
                      Le client autorise le traitement de ses données personnelles conformément à la loi n° 001/2011 relative à la protection des données à caractère personnel en République Gabonaise et au secret professionnel de l'avocat.
                    </div>
                  </div>
                </div>
                <v-alert
                  v-if="!clientData.consent_given"
                  type="warning"
                  variant="tonal"
                  density="compact"
                  class="mt-3"
                >
                  Le consentement est obligatoire pour créer un dossier client
                </v-alert>
              </v-card>

              <!-- Messages d'erreur -->
              <v-expand-transition>
                <v-alert
                  v-if="error"
                  type="error"
                  variant="tonal"
                  closable
                  class="mt-6"
                  @click:close="error = null"
                >
                  {{ error }}
                </v-alert>
              </v-expand-transition>

              <!-- Actions -->
              <div class="d-flex justify-end gap-3 mt-8">
                <v-btn
                  variant="text"
                  size="large"
                  @click="router.back()"
                  :disabled="loading"
                >
                  Annuler
                </v-btn>
                <v-btn
                  color="indigo-darken-4"
                  size="large"
                  variant="elevated"
                  prepend-icon="mdi-check"
                  type="submit"
                  :loading="loading"
                  :disabled="!formValid || !clientData.consent_given"
                >
                  Créer le client
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- Aide contextuelle -->
        <v-card elevation="1" class="mt-6 bg-blue-grey-lighten-5">
          <v-card-text>
            <h3 class="text-subtitle-1 font-weight-bold mb-3">
              <v-icon start color="info">mdi-lightbulb</v-icon>
              Conseils de saisie
            </h3>
            <ul class="text-caption">
              <li class="mb-2">
                <strong>RCCM :</strong> Vérifiez le format exact sur le certificat d'immatriculation OHADA
              </li>
              <li class="mb-2">
                <strong>NIF :</strong> Disponible sur l'attestation d'immatriculation fiscale de la DGI
              </li>
              <li class="mb-2">
                <strong>CNI :</strong> Le numéro figure au recto de la carte nationale d'identité gabonaise
              </li>
              <li>
                <strong>Téléphone :</strong> Utilisez le format international (+241) pour éviter les ambiguïtés
              </li>
            </ul>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useClientStore } from '@/stores/client'

const router = useRouter()
const clientStore = useClientStore()

// État
const clientForm = ref(null)
const formValid = ref(false)
const loading = ref(false)
const error = ref(null)

// Données du formulaire
const clientData = ref({
  client_type: 'PHYSIQUE',
  
  // Personne Physique
  first_name: '',
  last_name: '',
  date_of_birth: null,
  place_of_birth: '',
  ni_type: 'CNI',
  ni_number: '',
  
  // Personne Morale
  company_name: '',
  rccm: '',
  nif: '',
  legal_form: null,
  business_sector: null,
  representative_name: '',
  
  // Commun
  email: '',
  phone_primary: '',
  phone_secondary: '',
  address_line: '',
  city: 'Libreville',
  neighborhood: '',
  country: 'Gabon',
  consent_given: false
})

// Options
const idTypes = [
  { title: 'CNI (Carte Nationale d\'Identité)', value: 'CNI' },
  { title: 'Passeport', value: 'PASSPORT' },
  { title: 'Permis de séjour', value: 'RESIDENCE_PERMIT' },
  { title: 'Autre', value: 'OTHER' }
]

const legalForms = [
  'SARL (Société à Responsabilité Limitée)',
  'SA (Société Anonyme)',
  'SAS (Société par Actions Simplifiée)',
  'SARLU (SARL Unipersonnelle)',
  'SNC (Société en Nom Collectif)',
  'GIE (Groupement d\'Intérêt Économique)',
  'Association',
  'Autre'
]

const businessSectors = [
  'Bâtiment & Travaux Publics',
  'Commerce & Distribution',
  'Services aux entreprises',
  'Transport & Logistique',
  'Immobilier',
  'Industrie',
  'Agriculture & Pêche',
  'Banque & Finance',
  'Télécommunications',
  'Pétrole & Mines',
  'Santé',
  'Éducation',
  'Hôtellerie & Tourisme',
  'Autre'
]

const gabonCities = [
  'Libreville',
  'Port-Gentil',
  'Franceville',
  'Oyem',
  'Moanda',
  'Mouila',
  'Lambaréné',
  'Tchibanga',
  'Koulamoutou',
  'Makokou',
  'Bitam',
  'Autre'
]

const librevilleNeighborhoods = [
  'Akanda',
  'Alibandeng',
  'Angondjé',
  'Atok Ebe',
  'Aviation',
  'Bambouchine',
  'Belle-Vue',
  'Centre-Ville',
  'Charbonnages',
  'Cocotiers',
  'Derrière Prison',
  'Dragage',
  'Glass',
  'Gros Bouquet',
  'IAI',
  'Lalala',
  'Louis',
  'Lowé',
  'Mont-Bouët',
  'Nkembo',
  'Nombakélé',
  'Nzeng-Ayong',
  'Okala',
  'Oloumi',
  'Owendo',
  'PK5',
  'PK8',
  'Plaine Orety',
  'Pointe Denis',
  'Quartier Industriel',
  'Queben',
  'Sainte-Marie',
  'Sablière',
  'Sibang',
  'Sotega',
  'Wavignée'
]

// Règles de validation
const rules = {
  required: v => !!v || 'Ce champ est requis',
  
  email: v => {
    if (!v) return true
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return pattern.test(v) || 'Email invalide'
  },
  
  phoneFormat: v => {
    if (!v) return true
    const pattern = /^\+?[0-9\s-]{8,20}$/
    return pattern.test(v) || 'Format de téléphone invalide'
  },
  
  nameFormat: v => {
    if (!v) return true
    return v === v.toUpperCase() || 'Le nom doit être en majuscules'
  },
  
  ageValid: v => {
    if (!v) return true
    const birthDate = new Date(v)
    const today = new Date()
    const age = today.getFullYear() - birthDate.getFullYear()
    return age >= 18 || 'Le client doit être majeur (18 ans)'
  },
  
  idNumberFormat: v => {
    if (!v) return true
    // Validation basique - au moins 5 caractères
    return v.length >= 5 || 'Numéro de pièce invalide'
  },
  
  rccmFormat: v => {
    if (!v) return true
    // Format OHADA Gabon: GA-LBV-YYYY-AXX-NNNNN
    const pattern = /^GA-[A-Z]{3}-\d{4}-[AB]\d{2}-\d{5}$/
    return pattern.test(v) || 'Format RCCM invalide (ex: GA-LBV-2025-A12-12345)'
  },
  
  nifFormat: v => {
    if (!v) return true
    // Format DGI Gabon: 6 chiffres + 1 lettre
    const pattern = /^\d{6}[A-Z]$/
    return pattern.test(v.toUpperCase()) || 'Format NIF invalide (ex: 123456A)'
  }
}

// Méthodes
const handleTypeChange = () => {
  // Reset champs spécifiques au type
  if (clientData.value.client_type === 'PHYSIQUE') {
    clientData.value.company_name = ''
    clientData.value.rccm = ''
    clientData.value.nif = ''
    clientData.value.legal_form = null
    clientData.value.business_sector = null
    clientData.value.representative_name = ''
  } else {
    clientData.value.first_name = ''
    clientData.value.last_name = ''
    clientData.value.date_of_birth = null
    clientData.value.place_of_birth = ''
    clientData.value.ni_type = 'CNI'
    clientData.value.ni_number = ''
  }
}

const handleCityChange = () => {
  // Reset quartier si changement de ville
  if (clientData.value.city !== 'Libreville') {
    clientData.value.neighborhood = ''
  }
}

const getIdPlaceholder = () => {
  const placeholders = {
    CNI: 'Ex: 0123456789',
    PASSPORT: 'Ex: GA1234567',
    RESIDENCE_PERMIT: 'Ex: RS20250123',
    OTHER: 'Numéro de la pièce'
  }
  return placeholders[clientData.value.ni_type] || ''
}

const getIdHint = () => {
  const hints = {
    CNI: '10 chiffres (nouvelle génération)',
    PASSPORT: 'Format passeport gabonais',
    RESIDENCE_PERMIT: 'Numéro du permis de séjour',
    OTHER: ''
  }
  return hints[clientData.value.ni_type] || ''
}

const submitForm = async () => {
  // Validation finale
  const { valid } = await clientForm.value.validate()
  if (!valid) {
    error.value = 'Veuillez corriger les erreurs dans le formulaire'
    return
  }
  
  if (!clientData.value.consent_given) {
    error.value = 'Le consentement RGPD est obligatoire'
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    // Préparer les données
    const payload = { ...clientData.value }
    
    // Normaliser les données selon le type
    if (payload.client_type === 'PHYSIQUE') {
      // Nettoyer les champs personne morale
      delete payload.company_name
      delete payload.rccm
      delete payload.nif
      delete payload.legal_form
      delete payload.business_sector
      delete payload.representative_name
      
      // Formater le nom en majuscules
      if (payload.last_name) {
        payload.last_name = payload.last_name.toUpperCase()
      }
    } else {
      // Nettoyer les champs personne physique
      delete payload.first_name
      delete payload.last_name
      delete payload.date_of_birth
      delete payload.place_of_birth
      delete payload.ni_type
      delete payload.ni_number
      
      // Formater RCCM et NIF en majuscules
      if (payload.rccm) payload.rccm = payload.rccm.toUpperCase()
      if (payload.nif) payload.nif = payload.nif.toUpperCase()
    }
    
    // Créer le client
    const newClient = await clientStore.createClient(payload)
    
    // Redirection vers la fiche client
    router.push({ 
      name: 'ClientDetail', 
      params: { id: newClient.id } 
    })
    
  } catch (err) {
    console.error('Erreur création client:', err)
    
    // Gestion des erreurs backend
    if (err.response?.data) {
      const errors = err.response.data
      
      // Erreurs spécifiques
      if (errors.rccm) {
        error.value = `RCCM invalide : ${errors.rccm[0]}`
      } else if (errors.nif) {
        error.value = `NIF invalide : ${errors.nif[0]}`
      } else if (errors.email) {
        error.value = `Email invalide : ${errors.email[0]}`
      } else if (errors.phone_primary) {
        error.value = `Téléphone invalide : ${errors.phone_primary[0]}`
      } else if (errors.detail) {
        error.value = errors.detail
      } else {
        error.value = 'Une erreur est survenue lors de la création. Vérifiez les données saisies.'
      }
    } else {
      error.value = 'Erreur de connexion au serveur. Veuillez réessayer.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.gap-3 {
  gap: 12px;
}
</style>