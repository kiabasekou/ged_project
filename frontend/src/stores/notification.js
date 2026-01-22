// src/stores/notification.js

import { defineStore } from 'pinia'
import api from '@/plugins/axios'

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    overdueDossiers: [],
    count: 0,
    loading: false,
    drawer: false
  }),

  getters: {
    hasOverdue: (state) => state.count > 0,
    urgentCount: (state) => state.count
  },

  actions: {
    async fetchOverdueDossiers() {
      // Protection : ne charge pas si pas authentifié
      const token = localStorage.getItem('access_token')
      if (!token) {
        this.overdueDossiers = []
        this.count = 0
        return
      }

      this.loading = true
      try {
        const today = new Date().toISOString().split('T')[0]

        const response = await api.get('/dossiers/', {
          params: {
            critical_deadline__lt: today,
            status: 'OUVERT',
            ordering: 'critical_deadline',
            page_size: 20
          }
        })

        this.overdueDossiers = response.data.results || response.data
        this.count = this.overdueDossiers.length
      } catch (err) {
        // Si 401 ou autre erreur auth, on ignore silencieusement
        if (err.response?.status === 401) {
          this.overdueDossiers = []
          this.count = 0
        } else {
          console.error('Erreur chargement notifications', err)
        }
      } finally {
        this.loading = false
      }
    },

    toggleDrawer() {
      this.drawer = !this.drawer
      if (this.drawer && this.count === 0) {
        this.fetchOverdueDossiers()
      }
    },

    closeDrawer() {
      this.drawer = false
    }
  }
})