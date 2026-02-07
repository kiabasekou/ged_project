// frontend/src/stores/dossier.js

import { defineStore } from 'pinia'
import api from '@/plugins/axios'

export const useDossierStore = defineStore('dossier', {
  state: () => ({
    list: [],
    current: null,
    loading: false,
    loadingStats: false,
    loadingList: false,
    error: null,
    stats: {
      total: 0,
      ouverts: 0,
      en_retard: 0,
      clotures: 0,
      par_categorie: {}
    },
    pagination: {
      page: 1,
      pageSize: 25,
      total: 0
    }
  }),

  getters: {
    // Dossiers ouverts
    openDossiers: (state) => {
      return state.list.filter(d => d.status === 'OUVERT')
    },

    // Dossiers en retard
    overdueDossiers: (state) => {
      const now = new Date()
      return state.list.filter(d => {
        if (!d.critical_deadline || d.status === 'CLOTURE') return false
        return new Date(d.critical_deadline) < now
      })
    }
  },

  actions: {
    // Charger la liste des dossiers
    async fetchList(params = {}) {
      this.loadingList = true
      this.error = null
      
      try {
        const response = await api.get('/dossiers/', {
          params: {
            page: this.pagination.page,
            page_size: this.pagination.pageSize,
            ordering: '-opening_date',
            ...params
          }
        })
        
        this.list = response.data.results || []
        this.pagination.total = response.data.count || 0
        
        return response.data
      } catch (error) {
        console.error('Erreur chargement dossiers:', error)
        this.error = error.response?.data?.detail || 'Erreur de chargement'
        throw error
      } finally {
        this.loadingList = false
      }
    },

    // Charger les statistiques depuis l'endpoint backend dédié
    async fetchStats() {
      this.loadingStats = true
      this.error = null

      try {
        const response = await api.get('/dossiers/stats/')
        const data = response.data

        this.stats = {
          total: data.total ?? 0,
          ouverts: data.ouverts ?? 0,
          en_retard: data.en_retard ?? 0,
          clotures: data.clotures ?? 0,
          par_categorie: data.par_categorie ?? {}
        }

        return this.stats
      } catch (error) {
        console.error('Erreur chargement stats:', error)
        this.error = error.response?.data?.detail || 'Erreur de chargement'

        this.stats = {
          total: 0,
          ouverts: 0,
          en_retard: 0,
          clotures: 0,
          par_categorie: {}
        }

        return this.stats
      } finally {
        this.loadingStats = false
      }
    },

    // Charger les dossiers récents
    async fetchRecent(limit = 8) {
      this.loadingList = true
      this.error = null
      
      try {
        const response = await api.get('/dossiers/', {
          params: {
            page_size: limit,
            ordering: '-opening_date',
            status: 'OUVERT'
          }
        })
        
        this.list = response.data.results || []
        
        return this.list
      } catch (error) {
        console.error('Erreur chargement dossiers récents:', error)
        this.error = error.response?.data?.detail || 'Erreur de chargement'
        throw error
      } finally {
        this.loadingList = false
      }
    },

    // Charger un dossier spécifique
    async fetchDossier(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.get(`/dossiers/${id}/`)
        this.current = response.data
        return response.data
      } catch (error) {
        console.error('Erreur chargement dossier:', error)
        this.error = error.response?.data?.detail || 'Erreur de chargement'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Créer un dossier
    async createDossier(dossierData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.post('/dossiers/', dossierData)
        
        // Ajouter à la liste locale
        this.list.unshift(response.data)
        
        return response.data
      } catch (error) {
        console.error('Erreur création dossier:', error)
        this.error = error.response?.data?.detail || 'Erreur de création'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Mettre à jour un dossier
    async updateDossier(id, dossierData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.patch(`/dossiers/${id}/`, dossierData)
        
        // Mettre à jour la liste locale
        const index = this.list.findIndex(d => d.id === id)
        if (index !== -1) {
          this.list[index] = response.data
        }
        
        if (this.current?.id === id) {
          this.current = response.data
        }
        
        return response.data
      } catch (error) {
        console.error('Erreur mise à jour dossier:', error)
        this.error = error.response?.data?.detail || 'Erreur de mise à jour'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Clôturer un dossier
    async closeDossier(id) {
      return this.updateDossier(id, { status: 'CLOTURE' })
    },

    // Archiver un dossier
    async archiveDossier(id) {
      return this.updateDossier(id, { status: 'ARCHIVE' })
    },

    // Reset store
    reset() {
      this.list = []
      this.current = null
      this.loading = false
      this.loadingStats = false
      this.loadingList = false
      this.error = null
      this.stats = {
        total: 0,
        ouverts: 0,
        en_retard: 0,
        clotures: 0,
        par_categorie: {}
      }
    }
  }
})