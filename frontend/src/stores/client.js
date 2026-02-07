import { defineStore } from 'pinia'
import api from '@/plugins/axios'

export const useClientStore = defineStore('client', {
  state: () => ({
    list: [],
    total: 0,
    loadingList: false,
    current: null,
    loadingDetail: false,
    // On initialise les stats pour éviter les erreurs "undefined" au rendu
    stats: {
      total: 0,
      physiques: 0,
      moraux: 0,
      actifs: 0,
      avec_dossiers: 0
    },
    loadingStats: false
  }),

  actions: {
    // 1. Chargement de la liste
    async fetchList(params = {}) {
      this.loadingList = true
      try {
        const response = await api.get('/clients/', { params })
        this.list = response.data.results || response.data
        this.total = response.data.count || this.list.length
      } catch (err) {
        console.error('Erreur liste clients:', err)
      } finally {
        this.loadingList = false
      }
    },

    // 2. Chargement des statistiques
    async fetchStats() {
      this.loadingStats = true
      try {
        const response = await api.get('/clients/stats/')
        const data = response.data
        // Mapper les clés backend vers les clés frontend
        this.stats = {
          total: data.total_clients ?? data.total ?? 0,
          physiques: data.clients_physiques ?? data.physiques ?? 0,
          moraux: data.clients_moraux ?? data.moraux ?? 0,
          actifs: data.clients_actifs ?? data.actifs ?? 0,
          avec_dossiers: data.avec_dossiers ?? 0
        }
      } catch (err) {
        console.error('Erreur chargement statistiques clients:', err)
      } finally {
        this.loadingStats = false
      }
    },

    // 3. Chargement du détail
    async fetchDetail(id) {
      if (!id || id === 'undefined' || id === 'create') {
        this.current = null
        return
      }
      if (this.current?.id === id) return 

      this.loadingDetail = true
      try {
        const response = await api.get(`/clients/${id}/`)
        this.current = response.data
      } catch (err) {
        console.error('Erreur détail client:', err)
        this.current = null
        throw err
      } finally {
        this.loadingDetail = false
      }
    },

    // 4. Création
    async createClient(clientData) {
      try {
        const response = await api.post('/clients/', clientData)
        const newClient = response.data
        this.list.unshift(newClient)
        // On rafraîchit les stats après une création pour avoir les chiffres à jour
        await this.fetchStats() 
        return newClient
      } catch (err) {
        console.error('Erreur création client:', err)
        throw err 
      }
    },

    // 5. Consentement RGPD
    async grantConsent(id) {
      if (!id || id === 'undefined') return
      try {
        await api.post(`/clients/${id}/grant-consent/`)
        if (this.current?.id === id) {
          this.current.consent_given = true
          this.current.consent_date = new Date().toISOString()
        }
      } catch (err) {
        console.error('Erreur consentement:', err)
        throw err
      }
    }
  }
})