import { defineStore } from 'pinia'
import api from '@/plugins/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // Initialisation sécurisée
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('access_token') || null,
    loading: false
  }),

  getters: {
    // Un simple !!state.token ne suffit pas si le token est expiré
    isAuthenticated: (state) => !!state.token && !!state.user,
    role: (state) => state.user?.role || 'GUEST',
    isAdmin: (state) => state.user?.role === 'ADMIN',
  },

  actions: {
    /**
     * Login : Récupère le token et initialise la session
     */
    async login(credentials) {
      this.loading = true
      try {
        const response = await api.post('token/', credentials)
        const { access, refresh } = response.data

        this.token = access
        localStorage.setItem('access_token', access)
        localStorage.setItem('refresh_token', refresh)

        // Immédiatement après le login, on récupère le profil complet
        await this.fetchMe()
        
        return response
      } catch (err) {
        this.logout() // Sécurité : on nettoie tout si le login échoue
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * fetchMe : Récupère les infos de l'utilisateur connecté
     */
    async fetchMe() {
      try {
        const response = await api.get('users/me/')
        this.user = response.data
        localStorage.setItem('user', JSON.stringify(this.user))
        return this.user
      } catch (err) {
        // Si le token est invalide ou expiré
        if (err.response?.status === 401) {
          this.logout()
        }
        throw err
      }
    },

    /**
     * initialize : À appeler au démarrage de l'app (main.js ou router)
     * Vérifie si la session stockée est toujours valide.
     */
    async initialize() {
      if (this.token && !this.user) {
        try {
          await this.fetchMe()
        } catch (e) {
          console.warn("Session expirée au démarrage")
        }
      }
    },

    /**
     * Logout : Nettoyage complet
     */
    logout() {
      this.token = null
      this.user = null
      localStorage.clear() // Plus radical pour éviter les résidus
      // Optionnel : redirection vers login
      // router.push({ name: 'Login' }) 
    }
  }
})