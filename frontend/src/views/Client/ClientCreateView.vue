<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useClientStore } from '@/stores/client'

const router = useRouter()
const clientStore = useClientStore()

const form = ref(null)
const loading = ref(false)
const error = ref(null)

// Structure initiale du client (Alignée sur votre modèle Django)
const clientData = ref({
  client_type: 'PHYSIQUE',
  first_name: '',
  last_name: '',
  date_of_birth: null,
  place_of_birth: '',
  ni_number: '',
  ni_type: 'CNI',
  company_name: '',
  rccm: '',
  nif: '',
  representative_name: '',
  email: '',
  phone_primary: '',
  address_line: '',
  city: 'Libreville',
  country: 'Gabon',
  consent_given: false
})

// Règles de validation simples
const rules = {
  required: v => !!v || 'Ce champ est obligatoire',
  email: v => /.+@.+\..+/.test(v) || 'Email invalide'
}

const submitForm = async () => {
  const { valid } = await form.value.validate()
  if (!valid) return

  loading.value = true
  error.value = null

  try {
    const newClient = await clientStore.createClient(clientData.value)
    // Succès : Direction la fiche du client fraîchement créé
    router.push({ name: 'ClientDetail', params: { id: newClient.id } })
  } catch (err) {
    error.value = "Une erreur est survenue lors de la création. Vérifiez les données (NIF ou RCCM peut-être déjà utilisé)."
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <v-container>
    <div class="d-flex align-center mb-6">
      <v-btn icon="mdi-arrow-left" variant="text" @click="router.back()" class="mr-4"></v-btn>
      <h1 class="text-h4 font-weight-bold text-indigo-darken-4">Nouveau Client</h1>
    </div>

    <v-form ref="form" @submit.prevent="submitForm">
      <v-row>
        <v-col cols="12" md="8">
          <v-card elevation="2" class="pa-6 rounded-lg">
            <v-radio-group v-model="clientData.client_type" inline label="Nature juridique du client" class="mb-4">
              <v-radio label="Personne Physique" value="PHYSIQUE" color="indigo"></v-radio>
              <v-radio label="Personne Morale (Société)" value="MORALE" color="indigo"></v-radio>
            </v-radio-group>

            <v-divider class="mb-6"></v-divider>

            <v-row v-if="clientData.client_type === 'PHYSIQUE'">
              <v-col cols="12" sm="6">
                <v-text-field v-model="clientData.last_name" label="Nom" variant="outlined" :rules="[rules.required]"></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="clientData.first_name" label="Prénom" variant="outlined" :rules="[rules.required]"></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="clientData.date_of_birth" label="Date de naissance" type="date" variant="outlined"></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-select v-model="clientData.ni_type" :items="['CNI', 'PASSEPORT', 'CARTE_SEJOUR']" label="Type de pièce" variant="outlined"></v-select>
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="clientData.ni_number" label="Numéro de la pièce d'identité" variant="outlined"></v-text-field>
              </v-col>
            </v-row>

            <v-row v-else>
              <v-col cols="12">
                <v-text-field v-model="clientData.company_name" label="Raison Sociale" variant="outlined" :rules="[rules.required]"></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="clientData.rccm" label="RCCM" placeholder="ex: RG-LBV-..." variant="outlined"></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="clientData.nif" label="NIF" variant="outlined"></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="clientData.representative_name" label="Nom du représentant légal" variant="outlined"></v-text-field>
              </v-col>
            </v-row>
          </v-card>

          <v-card elevation="2" class="pa-6 rounded-lg mt-6">
            <v-card-title class="px-0 text-indigo-darken-4">Contact & Localisation</v-card-title>
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field v-model="clientData.email" label="Email" type="email" variant="outlined" :rules="[rules.email]"></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="clientData.phone_primary" label="Téléphone principal" variant="outlined" :rules="[rules.required]"></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="clientData.address_line" label="Adresse (Quartier, Rue)" variant="outlined"></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="clientData.city" label="Ville" variant="outlined"></v-text-field>
              </v-col>
            </v-row>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card elevation="2" class="pa-6 rounded-lg sticky-top">
            <v-alert v-if="error" type="error" variant="tonal" class="mb-4 text-caption">
              {{ error }}
            </v-alert>

            <v-checkbox
              v-model="clientData.consent_given"
              label="Le client a donné son consentement RGPD"
              color="success"
              hide-details
            ></v-checkbox>
            
            <p class="text-caption text-grey mb-6">
              En cochant cette case, vous confirmez que le client accepte le traitement de ses données personnelles conformément à la loi gabonaise.
            </p>

            <v-btn
              block
              color="indigo-darken-4"
              size="large"
              type="submit"
              :loading="loading"
              class="mb-3"
            >
              Enregistrer le client
            </v-btn>
            
            <v-btn block variant="text" @click="router.back()">
              Annuler
            </v-btn>
          </v-card>
        </v-col>
      </v-row>
    </v-form>
  </v-container>
</template>

<style scoped>
.sticky-top {
  position: sticky;
  top: 100px;
}
</style>