// frontend/src/stores/document.js

import { defineStore } from 'pinia'
import axios from '@/plugins/axios'

export const useDocumentStore = defineStore('document', {
  state: () => ({
    // Données
    documents: [],
    currentDocument: null,
    versionHistory: [],
    folders: [],
    
    // Pagination
    total: 0,
    page: 1,
    pageSize: 20,
    
    // État de chargement
    loading: false,
    uploadingDocument: false,
    uploadProgress: 0,
    
    // Filtres actifs
    filters: {
      search: '',
      dossier: null,
      folder: null,
      sensitivity: null,
      file_extension: null,
      uploaded_by: null,
      date_from: null,
      date_to: null
    },
    
    // Erreurs
    error: null
  }),

  getters: {
    /**
     * Documents filtrés et triés
     */
    filteredDocuments: (state) => {
      let filtered = [...state.documents]
      
      // Recherche textuelle
      if (state.filters.search) {
        const search = state.filters.search.toLowerCase()
        filtered = filtered.filter(doc => 
          doc.title.toLowerCase().includes(search) ||
          doc.original_filename.toLowerCase().includes(search) ||
          doc.description?.toLowerCase().includes(search)
        )
      }
      
      // Filtre par dossier
      if (state.filters.dossier) {
        filtered = filtered.filter(doc => doc.dossier === state.filters.dossier)
      }
      
      // Filtre par sensibilité
      if (state.filters.sensitivity) {
        filtered = filtered.filter(doc => doc.sensitivity === state.filters.sensitivity)
      }
      
      // Filtre par extension
      if (state.filters.file_extension) {
        filtered = filtered.filter(doc => 
          doc.file_extension?.toLowerCase() === state.filters.file_extension.toLowerCase()
        )
      }
      
      return filtered
    },

    /**
     * Documents par dossier
     */
    documentsByDossier: (state) => (dossierId) => {
      return state.documents.filter(doc => doc.dossier === dossierId)
    },

    /**
     * Documents par sensibilité
     */
    documentsBySensitivity: (state) => (sensitivity) => {
      return state.documents.filter(doc => doc.sensitivity === sensitivity)
    },

    /**
     * Statistiques
     */
    statistics: (state) => {
      return {
        total: state.documents.length,
        byType: state.documents.reduce((acc, doc) => {
          const ext = doc.file_extension || 'unknown'
          acc[ext] = (acc[ext] || 0) + 1
          return acc
        }, {}),
        bySensitivity: state.documents.reduce((acc, doc) => {
          acc[doc.sensitivity] = (acc[doc.sensitivity] || 0) + 1
          return acc
        }, {}),
        totalSize: state.documents.reduce((sum, doc) => sum + (doc.file_size || 0), 0)
      }
    },

    /**
     * Version actuelle du document
     */
    currentVersion: (state) => {
      if (!state.versionHistory.length) return null
      return state.versionHistory.find(v => v.is_current_version)
    },

    /**
     * Nombre de versions
     */
    versionCount: (state) => state.versionHistory.length
  },

  actions: {
    /**
     * Récupérer la liste des documents
     */
    async fetchDocuments(params = {}) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.get('/documents/documents/', {
          params: {
            page: this.page,
            page_size: this.pageSize,
            ...this.filters,
            ...params
          }
        })

        this.documents = response.data.results || response.data
        this.total = response.data.count || this.documents.length

        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors du chargement des documents'
        console.error('Erreur fetchDocuments:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Récupérer un document par ID
     */
    async fetchDocument(id) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.get(`/documents/documents/${id}/`)
        this.currentDocument = response.data

        // Mettre à jour dans la liste si présent
        const index = this.documents.findIndex(d => d.id === id)
        if (index !== -1) {
          this.documents[index] = response.data
        }

        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors du chargement du document'
        console.error('Erreur fetchDocument:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Upload d'un nouveau document
     */
    async uploadDocument(formData, onProgress = null) {
      this.uploadingDocument = true
      this.uploadProgress = 0
      this.error = null

      try {
        const response = await axios.post('/documents/documents/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            this.uploadProgress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
            if (onProgress) {
              onProgress(progressEvent)
            }
          }
        })

        // Ajouter le nouveau document en tête de liste
        this.documents.unshift(response.data)
        this.total += 1

        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de l\'upload du document'
        console.error('Erreur uploadDocument:', error)
        throw error
      } finally {
        this.uploadingDocument = false
        this.uploadProgress = 0
      }
    },

    /**
     * Créer une nouvelle version d'un document
     */
    async createNewVersion(documentId, formData, onProgress = null) {
      this.uploadingDocument = true
      this.uploadProgress = 0
      this.error = null

      try {
        const response = await axios.post(
          `/documents/documents/${documentId}/new_version/`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
              this.uploadProgress = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              )
              if (onProgress) {
                onProgress(progressEvent)
              }
            }
          }
        )

        // Mettre à jour le document dans la liste
        const index = this.documents.findIndex(d => d.id === documentId)
        if (index !== -1) {
          this.documents[index] = response.data
        }

        // Recharger l'historique des versions
        await this.fetchVersionHistory(documentId)

        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la création de la version'
        console.error('Erreur createNewVersion:', error)
        throw error
      } finally {
        this.uploadingDocument = false
        this.uploadProgress = 0
      }
    },

    /**
     * Récupérer l'historique des versions d'un document
     */
    async fetchVersionHistory(documentId) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.get(`/documents/documents/${documentId}/history/`)
        this.versionHistory = response.data.history || []

        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors du chargement de l\'historique'
        console.error('Erreur fetchVersionHistory:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Mettre à jour les métadonnées d'un document
     */
    async updateDocument(documentId, data) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.patch(`/documents/documents/${documentId}/`, data)

        // Mettre à jour dans la liste
        const index = this.documents.findIndex(d => d.id === documentId)
        if (index !== -1) {
          this.documents[index] = response.data
        }

        // Mettre à jour le document courant si c'est le même
        if (this.currentDocument?.id === documentId) {
          this.currentDocument = response.data
        }

        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la mise à jour'
        console.error('Erreur updateDocument:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Supprimer un document
     */
    async deleteDocument(documentId) {
      this.loading = true
      this.error = null

      try {
        await axios.delete(`/documents/documents/${documentId}/`)

        // Retirer de la liste
        this.documents = this.documents.filter(d => d.id !== documentId)
        this.total -= 1

        // Nettoyer le document courant si c'est le même
        if (this.currentDocument?.id === documentId) {
          this.currentDocument = null
        }

        return true
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la suppression'
        console.error('Erreur deleteDocument:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Récupérer les dossiers (arborescence)
     */
    async fetchFolders(dossierId = null) {
      this.loading = true
      this.error = null

      try {
        const params = dossierId ? { dossier: dossierId } : {}
        const response = await axios.get('/documents/folders/', { params })

        this.folders = response.data.results || response.data

        return this.folders
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors du chargement des dossiers'
        console.error('Erreur fetchFolders:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Créer un nouveau dossier
     */
    async createFolder(data) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post('/documents/folders/', data)

        this.folders.push(response.data)

        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la création du dossier'
        console.error('Erreur createFolder:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Obtenir l'URL de téléchargement d'un document
     */
    getDownloadUrl(documentId) {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
      return `${baseUrl}/documents/documents/${documentId}/download/`
    },

    /**
     * Télécharger un document
     */
    async downloadDocument(documentId, filename = null) {
      try {
        const url = this.getDownloadUrl(documentId)
        
        // Créer un lien temporaire et le cliquer
        const link = document.createElement('a')
        link.href = url
        if (filename) {
          link.download = filename
        }
        link.target = '_blank'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)

        return true
      } catch (error) {
        this.error = 'Erreur lors du téléchargement'
        console.error('Erreur downloadDocument:', error)
        throw error
      }
    },

    /**
     * Mettre à jour les filtres
     */
    setFilters(newFilters) {
      this.filters = {
        ...this.filters,
        ...newFilters
      }
    },

    /**
     * Réinitialiser les filtres
     */
    resetFilters() {
      this.filters = {
        search: '',
        dossier: null,
        folder: null,
        sensitivity: null,
        file_extension: null,
        uploaded_by: null,
        date_from: null,
        date_to: null
      }
    },

    /**
     * Changer de page
     */
    setPage(page) {
      this.page = page
    },

    /**
     * Changer la taille de page
     */
    setPageSize(size) {
      this.pageSize = size
      this.page = 1 // Reset à la première page
    },

    /**
     * Nettoyer le store
     */
    $reset() {
      this.documents = []
      this.currentDocument = null
      this.versionHistory = []
      this.folders = []
      this.total = 0
      this.page = 1
      this.pageSize = 20
      this.loading = false
      this.uploadingDocument = false
      this.uploadProgress = 0
      this.resetFilters()
      this.error = null
    }
  }
})