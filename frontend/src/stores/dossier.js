import { defineStore } from 'pinia'
import api from '@/plugins/axios'

export const useDossierStore = defineStore('dossier', {
  state: () => ({
    // Liste des dossiers
    list: [],
    total: 0,
    loadingList: false,

    // Détail d'un dossier spécifique
    current: null,
    currentFolders: [],
    currentDocuments: [],
    loadingDetail: false,

    // Stats globales
    stats: {
      total: 0,
      ouverts: 0,
      en_attente: 0,
      clotures: 0,
      en_retard: 0,
      par_categorie: {}
    },
    loadingStats: false
  }),

  getters: {
    dossiersEnRetard: (state) => {
      const today = new Date()
      return state.list.filter(d => d.critical_deadline && new Date(d.critical_deadline) < today)
    }
  },

  actions: {
    // CORRECTION : Ajout de la fonction manquante demandée par le Dashboard
    async fetchRecent(limit = 8) {
      this.loadingList = true
      try {
        const response = await api.get('/dossiers/', { 
          params: { ordering: '-created_at', page_size: limit } 
        })
        this.list = response.data.results || response.data
      } catch (err) {
        console.error('Erreur fetchRecent:', err)
      } finally {
        this.loadingList = false
      }
    },

    async fetchList(params = {}) {
      this.loadingList = true
      try {
        const response = await api.get('/dossiers/', { params })
        this.list = response.data.results || response.data
        this.total = response.data.count || this.list.length
      } catch (err) {
        console.error('Erreur fetchList:', err)
        this.list = []
      } finally {
        this.loadingList = false
      }
    },

    async fetchStats() {
      this.loadingStats = true
      try {
        const response = await api.get('/dossiers/stats/')
        this.stats = response.data
      } catch (err) {
        console.error('Erreur stats:', err)
      } finally {
        this.loadingStats = false
      }
    },

    async fetchDetail(id) {
      // CORRECTION : On ne cast plus en Number(id) car ce sont des UUID (Strings)
      if (this.current?.id === id && this.currentDocuments.length > 0) return

      this.loadingDetail = true
      try {
        const [dossierRes, foldersRes, docsRes] = await Promise.all([
          api.get(`/dossiers/${id}/`),
          api.get('/documents/folders/', { params: { dossier: id } }),
          api.get('/documents/', { params: { dossier: id, ordering: '-uploaded_at' } })
        ])

        this.current = dossierRes.data
        this.currentFolders = foldersRes.data
        this.currentDocuments = docsRes.data.results || docsRes.data
      } catch (err) {
        console.error('Erreur fetchDetail:', err)
        this.clearCurrent()
      } finally {
        this.loadingDetail = false
      }
    },

    async cloturerDossier(id) {
      try {
        await api.post(`/dossiers/${id}/cloturer/`)
        // Mise à jour réactive de l'état local
        if (this.current?.id === id) this.current.status = 'CLOTURE'
        this.fetchStats() // On rafraîchit les compteurs du dashboard
      } catch (err) {
        console.error('Erreur clôture:', err)
        throw err
      }
    },

    clearCurrent() {
      this.current = null
      this.currentFolders = []
      this.currentDocuments = []
    }
  }
})