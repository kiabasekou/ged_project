// frontend/src/stores/agenda.js

import { defineStore } from 'pinia'
import api from '@/plugins/axios'

export const useAgendaStore = defineStore('agenda', {
  state: () => ({
    events: [],
    loading: false,
    error: null,
    stats: {
      total: 0,
      audiences: 0,
      rdv: 0,
      formalites: 0,
      upcoming: 0
    }
  }),

  getters: {
    // Événements par type
    eventsByType: (state) => (type) => {
      return state.events.filter(e => e.type === type)
    },

    // Événements à venir (7 prochains jours)
    upcomingEvents: (state) => {
      const now = new Date()
      const weekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
      
      return state.events
        .filter(e => {
          const eventDate = new Date(e.start_date)
          return eventDate >= now && eventDate <= weekFromNow
        })
        .sort((a, b) => new Date(a.start_date) - new Date(b.start_date))
    },

    // Délais critiques (événements urgents dans les 3 jours)
    criticalDeadlines: (state) => {
      const now = new Date()
      const threeDaysFromNow = new Date(now.getTime() + 3 * 24 * 60 * 60 * 1000)
      
      return state.events
        .filter(e => {
          const eventDate = new Date(e.start_date)
          return eventDate >= now && 
                 eventDate <= threeDaysFromNow &&
                 (e.priority === 'HIGH' || e.priority === 'URGENT' || e.type === 'AUDIENCE')
        })
        .sort((a, b) => new Date(a.start_date) - new Date(b.start_date))
    }
  },

  actions: {
    // Charger tous les événements
    async fetchEvents(params = {}) {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.get('/agenda/events/', {
          params: {
            page_size: 1000,
            ordering: 'start_date',
            ...params
          }
        })
        
        this.events = response.data.results || response.data || []
        this.calculateStats()
        
        return this.events
      } catch (error) {
        console.error('Erreur chargement événements:', error)
        this.error = error.response?.data?.detail || 'Erreur de chargement'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Charger un événement spécifique
    async fetchEvent(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.get(`/agenda/events/${id}/`)
        return response.data
      } catch (error) {
        console.error('Erreur chargement événement:', error)
        this.error = error.response?.data?.detail || 'Erreur de chargement'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Créer un événement
    async createEvent(eventData) {
      this.loading = true
      this.error = null
      
      try {
        // Validation des données
        if (!eventData.title || !eventData.type || !eventData.start_date) {
          throw new Error('Titre, type et date de début sont obligatoires')
        }

        // Construction du payload
        const payload = {
          type: eventData.type,
          title: eventData.title,
          start_date: eventData.start_date,
          all_day: eventData.all_day || false,
          description: eventData.description || '',
          priority: eventData.priority || 'NORMAL'
        }

        // Champs optionnels
        if (eventData.dossier) payload.dossier = eventData.dossier
        if (eventData.location) payload.location = eventData.location
        if (eventData.reminder) payload.reminder = eventData.reminder

        // Horaires si pas toute la journée
        if (!payload.all_day) {
          if (eventData.start_time) payload.start_time = eventData.start_time
          if (eventData.end_time) payload.end_time = eventData.end_time
          if (eventData.end_date) payload.end_date = eventData.end_date
        }

        const response = await api.post('/agenda/events/', payload)
        
        // Ajouter à la liste locale
        this.events.push(response.data)
        this.calculateStats()
        
        return response.data
      } catch (error) {
        console.error('Erreur création événement:', error)
        
        // Gestion des erreurs spécifiques
        if (error.response?.data) {
          const errors = error.response.data
          
          if (errors.start_date) {
            this.error = `Date invalide : ${errors.start_date[0]}`
          } else if (errors.dossier) {
            this.error = `Dossier invalide : ${errors.dossier[0]}`
          } else if (errors.detail) {
            this.error = errors.detail
          } else {
            this.error = 'Erreur lors de la création de l\'événement'
          }
        } else {
          this.error = error.message || 'Erreur de création'
        }
        
        throw error
      } finally {
        this.loading = false
      }
    },

    // Mettre à jour un événement
    async updateEvent(id, eventData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.patch(`/agenda/events/${id}/`, eventData)
        
        // Mettre à jour la liste locale
        const index = this.events.findIndex(e => e.id === id)
        if (index !== -1) {
          this.events[index] = response.data
        }
        
        this.calculateStats()
        
        return response.data
      } catch (error) {
        console.error('Erreur mise à jour événement:', error)
        this.error = error.response?.data?.detail || 'Erreur de mise à jour'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Supprimer un événement
    async deleteEvent(id) {
      this.loading = true
      this.error = null
      
      try {
        await api.delete(`/agenda/events/${id}/`)
        
        // Retirer de la liste locale
        this.events = this.events.filter(e => e.id !== id)
        this.calculateStats()
        
        return true
      } catch (error) {
        console.error('Erreur suppression événement:', error)
        this.error = error.response?.data?.detail || 'Erreur de suppression'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Calculer les statistiques
    calculateStats() {
      const now = new Date()
      const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
      const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0)
      
      const thisMonth = this.events.filter(e => {
        const eventDate = new Date(e.start_date)
        return eventDate >= startOfMonth && eventDate <= endOfMonth
      })
      
      this.stats = {
        total: thisMonth.length,
        audiences: thisMonth.filter(e => e.type === 'AUDIENCE').length,
        rdv: thisMonth.filter(e => e.type === 'RDV').length,
        formalites: thisMonth.filter(e => e.type === 'FORMALITE').length,
        upcoming: this.upcomingEvents.length
      }
    },

    // Reset store
    reset() {
      this.events = []
      this.loading = false
      this.error = null
      this.stats = {
        total: 0,
        audiences: 0,
        rdv: 0,
        formalites: 0,
        upcoming: 0
      }
    }
  }
})