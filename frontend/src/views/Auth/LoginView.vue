<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

// === ÉTATS DU FORMULAIRE ===
const username = ref<string>('')
const password = ref<string>('')
const loading = ref<boolean>(false)
const error = ref<string | null>(null)

// === SOUMISSION ===
const login = async (): Promise<void> => {
  // Validation minimale côté client
  if (!username.value.trim() || !password.value) {
    error.value = 'Veuillez saisir votre nom d’utiliseur et votre mot de passe.'
    return
  }

  loading.value = true
  error.value = null

  try {
    // 1. Authentification
    await authStore.login({
      username: username.value.trim(),
      password: password.value
    })

    // 2. Chargement du profil utilisateur (rôles, permissions…)
    await authStore.fetchMe()

    // 3. Chargement des notifications critiques (délais dépassés)
    await notificationStore.fetchOverdueDossiers()

    // 4. Redirection sécurisée vers le tableau de bord
    await router.push({ name: 'Dashboard' })
  } catch (err: any) {
    console.error('Échec de l’authentification', err)

    // Gestion différenciée des erreurs pour une UX claire
    if (err.response?.status === 401) {
      error.value = 'Identifiants incorrects. Veuillez vérifier votre nom d’utilisateur et votre mot de passe.'
    } else if (err.response?.status === 403) {
      error.value = 'Votre compte est désactivé ou en attente de validation. Contactez l’administrateur.'
    } else if (!navigator.onLine) {
      error.value = 'Aucune connexion internet détectée.'
    } else {
      error.value = 'Erreur de connexion au serveur. Veuillez réessayer dans quelques instants.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page d-flex flex-column min-vh-100">
    <!-- Barre supérieure -->
    <v-app-bar color="indigo-darken-4" elevation="0" class="border-b">
      <v-app-bar-title class="text-h6 font-weight-bold d-flex align-center">
        <v-icon start size="28">mdi-scale-balance</v-icon>
        GED Cabinet Kiaba
      </v-app-bar-title>

      <v-spacer />

      <div class="text-caption text-grey-lighten-2 d-none d-sm-flex align-center">
        <v-icon start size="16">mdi-map-marker</v-icon>
        Libreville • Gabon
      </div>
    </v-app-bar>

    <!-- Contenu principal -->
    <v-main class="flex-grow-1 d-flex align-center justify-center pa-4">
      <v-container class="max-width-500">
        <v-card
          elevation="20"
          class="pa-8 pa-md-12 rounded-xl overflow-hidden"
          max-width="500"
          role="region"
          aria-labelledby="login-title"
        >
          <!-- En-tête -->
          <div class="text-center mb-10">
            <v-avatar size="110" color="indigo-darken-4" class="mb-6 shadow-lg">
              <v-icon size="64" color="white">mdi-scale-balance</v-icon>
            </v-avatar>

            <h1 id="login-title" class="text-h4 font-weight-black text-indigo-darken-4 mb-3">
              Connexion sécurisée
            </h1>

            <p class="text-h6 text-grey-darken-3 font-weight-medium">
              Gestion Électronique des Dossiers
            </p>

            <p class="text-caption text-grey-darken-1 mt-4">
              Cabinet Kiaba • Libreville, Estuaire
            </p>
          </div>

          <!-- Formulaire -->
          <v-form @submit.prevent="login" novalidate>
            <v-text-field
              v-model="username"
              label="Nom d’utilisateur"
              prepend-inner-icon="mdi-account"
              variant="outlined"
              density="comfortable"
              autocomplete="username"
              :disabled="loading"
              autofocus
              required
              aria-required="true"
              class="mb-6"
            />

            <v-text-field
              v-model="password"
              label="Mot de  mot de passe"
              type="password"
              prepend-inner-icon="mdi-lock"
              variant="outlined"
              density="comfortable"
              autocomplete="current-password"
              :disabled="loading"
              required
              aria-required="true"
              class="mb-8"
              @keydown.enter="login"
            />

            <!-- Erreur -->
            <v-alert
              v-if="error"
              type="error"
              variant="tonal"
              density="compact"
              class="mb-6"
              closable
              @click:close="error = null"
            >
              {{ error }}
            </v-alert>

            <!-- Bouton principal -->
            <v-btn
              :loading="loading"
              :disabled="loading"
              type="submit"
              block
              size="x-large"
              color="indigo-darken-4"
              class="text-white font-weight-bold text-h6 py-8 rounded-lg shadow-lg"
            >
              <v-icon start size="32">mdi-login</v-icon>
              Se connecter
            </v-btn>
          </v-form>

          <!-- Pied de carte -->
          <div class="text-center mt-10">
            <p class="text-caption text-grey-darken-2">
              Mot de passe oublié ? Contactez l’administrateur du cabinet.
            </p>
          </div>
        </v-card>
      </v-container>
    </v-main>

    <!-- Footer -->
    <v-footer class="py-8 bg-transparent text-center border-t">
      <div>
        <p class="text-caption text-grey-darken-2 mb-1">
          © {{ new Date().getFullYear() }} By SO Consulting — Tous droits réservés
        </p>
        <p class="text-caption text-grey-darken-1">
          GED Sécurisée & Souveraine • Conforme aux normes gabonaises et RGPD
        </p>
      </div>
    </v-footer>
  </div>
</template>

<style scoped>
.login-page {
  background: linear-gradient(135deg, #1a237e 0%, #0d113f 45%, #3949ab 100%);
  background-attachment: fixed;
  min-height: 100vh;
}

.v-card {
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.shadow-lg {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
}

.max-width-500 {
  max-width: 500px;
  width: 100%;
}
</style>