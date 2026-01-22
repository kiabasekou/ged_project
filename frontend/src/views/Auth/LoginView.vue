<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const login = async () => {
  loading.value = true
  error.value = ''

  try {
    // 1. Connexion via le store Auth
    await authStore.login({
      username: username.value,
      password: password.value
    })

    // 2. Chargement du profil utilisateur
    await authStore.fetchMe()

    // 3. Chargement des notifications critiques
    await notificationStore.fetchOverdueDossiers()

    // 4. Redirection vers le dashboard
    router.push('/')
  } catch (err) {
    error.value = 'Identifiants incorrects ou serveur indisponible.'
    console.error('Erreur login', err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page d-flex flex-column min-vh-100">
    <!-- Header minimal -->
    <v-app-bar color="indigo-darken-4" dark elevation="0">
      <v-toolbar-title class="text-h6 font-weight-bold">
        <v-icon left>mdi-scale-balance</v-icon>
        GED Cabinet Kiaba
      </v-toolbar-title>
      <v-spacer />
      <span class="text-caption">Libreville • Gabon</span>
    </v-app-bar>

    <!-- Contenu principal -->
    <v-main class="flex-grow-1 d-flex align-center justify-center">
      <v-container>
        <v-row justify="center">
          <v-col cols="12" md="6" lg="5" xl="4">
            <v-card elevation="16" class="pa-8 pa-md-12 rounded-xl">
              <div class="text-center mb-8">
                <v-avatar size="100" color="amber" class="mb-4">
                  <v-icon size="60" color="indigo-darken-4">mdi-scale-balance</v-icon>
                </v-avatar>
                <h1 class="text-h4 font-weight-bold text-indigo-darken-4 mb-2">
                  Connexion sécurisée
                </h1>
                <p class="text-subtitle-1 text-grey-darken-2">
                  Gestion Électronique des Dossiers
                </p>
              </div>

              <v-form @submit.prevent="login">
                <v-text-field
                  v-model="username"
                  label="Nom d'utilisateur"
                  prepend-inner-icon="mdi-account"
                  variant="outlined"
                  class="mb-4"
                  :disabled="loading"
                  autofocus
                  required
                />

                <v-text-field
                  v-model="password"
                  label="Mot de passe"
                  type="password"
                  prepend-inner-icon="mdi-lock"
                  variant="outlined"
                  class="mb-6"
                  :disabled="loading"
                  required
                />

                <v-alert v-if="error" type="error" density="compact" class="mb-6">
                  {{ error }}
                </v-alert>

                <v-btn
                  :loading="loading"
                  type="submit"
                  block
                  size="x-large"
                  color="indigo-darken-4"
                  class="text-white font-weight-bold text-h6 py-6"
                >
                  Se connecter
                </v-btn>
              </v-form>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <!-- Footer -->
    <v-footer class="py-6 text-center bg-transparent">
      <div>
        <p class="text-caption text-grey-darken-2 mb-1">
          © {{ new Date().getFullYear() }} By SO Consulting — Tous droits réservés
        </p>
        <p class="text-caption text-grey-darken-1">
          GED Sécurisée & Souveraine • Conforme RGPD Gabon
        </p>
      </div>
    </v-footer>
  </div>
</template>

<style scoped>
.login-page {
  background: linear-gradient(135deg, #1A237E 0%, #0D113F 60%, #C5A059 100%);
  /* #C5A059 est une couleur bronze/or plus sobre que le jaune pur pour un cabinet */
}
</style>