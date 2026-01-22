import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import api from './plugins/axios'
import { useAuthStore } from '@/stores/auth' // Import du store

const app = createApp(App)
const pinia = createPinia()

app.use(pinia) // Pinia doit être chargé en premier
app.use(router)
app.use(vuetify)

// Rendre api disponible globalement
app.config.globalProperties.$api = api

// --- SYNCHRONISATION DE LA SESSION ---
const authStore = useAuthStore()

// On initialise la session (vérification du token + chargement du profil)
// avant de monter l'application pour éviter les erreurs de navigation.
authStore.initialize().then(() => {
    app.mount('#app')
}).catch(() => {
    // Si l'initialisation échoue vraiment, on monte quand même 
    // l'app, le routeur se chargera de renvoyer vers /login
    app.mount('#app')
})