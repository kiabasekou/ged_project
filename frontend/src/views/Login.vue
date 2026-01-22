<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { formatDate } from '@/utils/format'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const login = async () => {
  loading.value = true
  error.value = ''

  try {
    // À adapter selon ton endpoint Django (ex: token JWT ou session)
    // Exemple avec endpoint /api/auth/login/ retournant { access_token, user }
    await authStore.login({
      username: username.value,
      password: password.value
    })

    // Optionnel : charger le profil complet
    await authStore.fetchMe()

    // Redirection vers dashboard
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
    <!-- Header minimal pour login -->
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
      <v-container class="fill-height">
        <v-row align="center" justify="center">
          <v-col cols="12" md="8" lg="6" xl="4">
            <v-card elevation="12" class="pa-8 pa-md-12 rounded-xl" max-width="500">
              <div class="text-center mb-8">
                <v-avatar size="100" color="amber" class="mb-4">
                  <v-icon size="60" color="indigo-darken-4">mdi-scale-balance</v-icon>
                </v-avatar>
                <h1 class="text-h4 font-weight-bold text-indigo-darken-4 mb-2">
                  Bienvenue
                </h1>
                <p class="text-h6 text-grey-darken-2">
                  Gestion Électronique des Dossiers
                </p>
                <p class="text-caption text-grey mt-2">
                  Cabinet sécurisé • Libreville, Gabon
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
                />

                <v-text-field
                  v-model="password"
                  label="Mot de passe"
                  type="password"
                  prepend-inner-icon="mdi-lock"
                  variant="outlined"
                  class="mb-6"
                  :disabled="loading"
                />

                <v-alert
                  v-if="error"
                  type="error"
                  density="compact"
                  class="mb-6"
                >
                  {{ error }}
                </v-alert>

                <v-btn
                  :loading="loading"
                  type="submit"
                  block
                  size="x-large"
                  color="indigo-darken-4"
                  class="text-white font-weight-bold py-6 text-h6"
                >
                  Se connecter
                </v-btn>
              </v-form>

              <div class="text-center mt-8">
                <p class="text-caption text-grey-darken-1">
                  Mot de passe oublié ? Contactez l'administrateur.
                </p>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <!-- Footer -->
    <v-footer class="py-6 bg-transparent text-center">
      <div>
        <p class="text-caption text-grey-darken-2 mb-1">
          © {{ new Date().getFullYear() }} Cabinet Kiaba — Tous droits réservés
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
  background: linear-gradient(135deg, #1A237E 0%, #0D113F 50%, #FFD700 100%);
  background-attachment: fixed;
}

.v-card {
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.95);
}
</style>