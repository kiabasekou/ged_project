import { defineStore } from 'pinia'
import api from '@/plugins/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('access_token') || null,
    loading: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    role: (state) => state.user?.role || 'GUEST',
    isAdmin: (state) => state.user?.role === 'ADMIN',
  },

  actions: {
    async login(credentials) {
      this.loading = true
      try {
        // ✅ CORRECTION : Slash initial obligatoire
        const response = await api.post('/token/', credentials)
        const { access, refresh } = response.data

        this.token = access
        localStorage.setItem('access_token', access)
        localStorage.setItem('refresh_token', refresh)

        await this.fetchMe()
        
        return response
      } catch (err) {
        this.logout()
        throw err
      } finally {
        this.loading = false
      }
    },

    async fetchMe() {
      try {
        // ✅ CORRECTION : Slash initial obligatoire
        const response = await api.get('/users/me/')
        this.user = response.data
        localStorage.setItem('user', JSON.stringify(this.user))
        return this.user
      } catch (err) {
        if (err.response?.status === 401) {
          this.logout()
        }
        throw err
      }
    },

    async initialize() {
      if (this.token && !this.user) {
        try {
          await this.fetchMe()
        } catch (e) {
          console.warn("Session expirée au démarrage")
          this.logout()
        }
      }
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.clear()
    }
  }
})