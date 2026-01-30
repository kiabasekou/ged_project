// ============================================================================
// Service : Dossier Service
// Description : Gestion des appels API pour les dossiers juridiques
// Auteur : Maître Ahmed - GED Cabinet Kiaba
// ============================================================================

import api from '@/plugins/axios'

/**
 * Service centralisant toutes les opérations liées aux dossiers juridiques
 */
export const dossierService = {
  /**
   * Récupère la liste des dossiers avec filtres et pagination
   * 
   * @param {Object} params - Paramètres de requête
   * @param {string} params.search - Recherche textuelle
   * @param {string} params.status - Statut: OUVERT, ATTENTE, SUSPENDU, CLOTURE, ARCHIVE
   * @param {string} params.category - Catégorie juridique
   * @param {string} params.client - UUID du client
   * @param {string} params.responsible - UUID de l'avocat responsable
   * @param {string} params.critical_deadline__lt - Dossiers en retard (date < aujourd'hui)
   * @param {number} params.page - Numéro de page
   * @param {number} params.page_size - Éléments par page
   * @param {string} params.ordering - Tri (ex: '-opening_date')
   * @returns {Promise<Object>} { results, count, next, previous }
   */
  async fetchList(params = {}) {
    try {
      const response = await api.get('/dossiers/', { params })
      return response.data
    } catch (error) {
      console.error('Erreur récupération liste dossiers:', error)
      throw this._handleError(error)
    }
  },

  /**
   * Récupère le détail complet d'un dossier
   * 
   * @param {string} id - UUID du dossier
   * @returns {Promise<Object>} Données complètes du dossier
   */
  async fetchDetail(id) {
    try {
      const response = await api.get(`/dossiers/${id}/`)
      return response.data
    } catch (error) {
      console.error(`Erreur récupération dossier ${id}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Crée un nouveau dossier
   * 
   * @param {Object} dossierData - Données du dossier
   * @param {string} dossierData.title - Titre du dossier
   * @param {string} dossierData.client - UUID du client
   * @param {string} dossierData.responsible - UUID de l'avocat responsable
   * @param {string} dossierData.category - Catégorie juridique
   * @param {string} dossierData.status - Statut (défaut: OUVERT)
   * @param {string} dossierData.opening_date - Date d'ouverture (ISO format)
   * @param {string} dossierData.critical_deadline - Date limite critique (optionnel)
   * @param {string} dossierData.jurisdiction - Juridiction compétente
   * @param {string} dossierData.description - Description détaillée
   * @returns {Promise<Object>} Dossier créé avec reference_code généré
   * 
   * @example
   * const newDossier = await dossierService.create({
   *   title: 'Contentieux commercial SARL Alpha',
   *   client: 'uuid-client',
   *   responsible: 'uuid-avocat',
   *   category: 'CONTENTIEUX',
   *   jurisdiction: 'Tribunal de Commerce de Libreville',
   *   critical_deadline: '2026-03-15'
   * })
   */
  async create(dossierData) {
    try {
      const response = await api.post('/dossiers/', dossierData)
      return response.data
    } catch (error) {
      console.error('Erreur création dossier:', error)
      throw this._handleError(error)
    }
  },

  /**
   * Met à jour un dossier existant
   * 
   * @param {string} id - UUID du dossier
   * @param {Object} dossierData - Données à mettre à jour (partiel autorisé)
   * @returns {Promise<Object>} Dossier mis à jour
   */
  async update(id, dossierData) {
    try {
      const response = await api.patch(`/dossiers/${id}/`, dossierData)
      return response.data
    } catch (error) {
      console.error(`Erreur mise à jour dossier ${id}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Change le statut d'un dossier
   * 
   * @param {string} id - UUID du dossier
   * @param {string} newStatus - Nouveau statut
   * @returns {Promise<Object>} Dossier mis à jour
   * 
   * @example
   * await dossierService.changeStatus(dossierId, 'CLOTURE')
   */
  async changeStatus(id, newStatus) {
    try {
      const response = await api.patch(`/dossiers/${id}/`, {
        status: newStatus
      })
      return response.data
    } catch (error) {
      console.error(`Erreur changement statut dossier ${id}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Clôture un dossier
   * 
   * @param {string} id - UUID du dossier
   * @param {string} closing_date - Date de clôture (ISO format, optionnel)
   * @returns {Promise<Object>} Dossier clôturé
   */
  async close(id, closing_date = null) {
    try {
      const data = { status: 'CLOTURE' }
      if (closing_date) {
        data.closing_date = closing_date
      }
      
      const response = await api.patch(`/dossiers/${id}/`, data)
      return response.data
    } catch (error) {
      console.error(`Erreur clôture dossier ${id}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Archive un dossier clôturé
   * 
   * @param {string} id - UUID du dossier
   * @returns {Promise<Object>} Dossier archivé
   */
  async archive(id) {
    try {
      const response = await api.patch(`/dossiers/${id}/`, {
        status: 'ARCHIVE'
      })
      return response.data
    } catch (error) {
      console.error(`Erreur archivage dossier ${id}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Récupère l'arborescence de dossiers (folders) d'un dossier
   * 
   * @param {string} dossierId - UUID du dossier
   * @returns {Promise<Array>} Arborescence de dossiers
   */
  async fetchFolders(dossierId) {
    try {
      const response = await api.get('/folders/', {
        params: {
          dossier: dossierId
        }
      })
      return response.data.results || []
    } catch (error) {
      console.error(`Erreur récupération folders du dossier ${dossierId}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Récupère les statistiques globales des dossiers
   * 
   * @returns {Promise<Object>}
   * {
   *   total: number,
   *   ouverts: number,
   *   en_retard: number,
   *   clotures: number,
   *   par_categorie: { [key]: number }
   * }
   */
  async fetchStats() {
    try {
      const response = await api.get('/dossiers/stats/')
      return response.data
    } catch (error) {
      console.error('Erreur récupération stats dossiers:', error)
      throw this._handleError(error)
    }
  },

  /**
   * Récupère les dossiers en retard (délai critique dépassé)
   * 
   * @param {number} limit - Nombre maximal de résultats
   * @returns {Promise<Array>} Liste de dossiers en retard
   */
  async fetchOverdue(limit = 20) {
    try {
      const today = new Date().toISOString().split('T')[0]
      
      const response = await api.get('/dossiers/', {
        params: {
          critical_deadline__lt: today,
          status: 'OUVERT',
          ordering: 'critical_deadline',
          page_size: limit
        }
      })
      return response.data.results || []
    } catch (error) {
      console.error('Erreur récupération dossiers en retard:', error)
      return []
    }
  },

  /**
   * Récupère les dossiers d'un client spécifique
   * 
   * @param {string} clientId - UUID du client
   * @param {Object} options - Options de requête
   * @returns {Promise<Array>} Liste de dossiers
   */
  async fetchByClient(clientId, options = {}) {
    try {
      const response = await api.get('/dossiers/', {
        params: {
          client: clientId,
          ordering: '-opening_date',
          ...options
        }
      })
      return response.data.results || []
    } catch (error) {
      console.error(`Erreur récupération dossiers du client ${clientId}:`, error)
      return []
    }
  },

  /**
   * Récupère les dossiers d'un avocat spécifique
   * 
   * @param {string} lawyerId - UUID de l'avocat
   * @param {Object} options - Options de requête
   * @returns {Promise<Array>} Liste de dossiers
   */
  async fetchByLawyer(lawyerId, options = {}) {
    try {
      const response = await api.get('/dossiers/', {
        params: {
          responsible: lawyerId,
          ordering: '-opening_date',
          ...options
        }
      })
      return response.data.results || []
    } catch (error) {
      console.error(`Erreur récupération dossiers de l'avocat ${lawyerId}:`, error)
      return []
    }
  },

  /**
   * Recherche rapide de dossiers (autocomplétion)
   * 
   * @param {string} query - Terme de recherche
   * @param {number} limit - Nombre maximal de résultats
   * @returns {Promise<Array>} Liste de dossiers
   */
  async quickSearch(query, limit = 10) {
    try {
      const response = await api.get('/dossiers/', {
        params: {
          search: query,
          page_size: limit,
          ordering: '-opening_date'
        }
      })
      return response.data.results || []
    } catch (error) {
      console.error('Erreur recherche rapide dossiers:', error)
      return []
    }
  },

  /**
   * Exporte la liste des dossiers en CSV
   * 
   * @param {Object} filters - Filtres à appliquer
   * @returns {Promise<Blob>} Fichier CSV
   */
  async exportToCSV(filters = {}) {
    try {
      const response = await api.get('/dossiers/export/', {
        params: filters,
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      console.error('Erreur export CSV dossiers:', error)
      throw this._handleError(error)
    }
  },

  /**
   * Récupère l'historique d'audit d'un dossier
   * 
   * @param {string} id - UUID du dossier
   * @returns {Promise<Array>} Historique des actions
   */
  async fetchAuditLog(id) {
    try {
      const response = await api.get(`/dossiers/${id}/audit-log/`)
      return response.data
    } catch (error) {
      console.error(`Erreur récupération audit log du dossier ${id}:`, error)
      return []
    }
  },

  /**
   * Gestion centralisée des erreurs
   * 
   * @private
   * @param {Error} error - Erreur capturée
   * @returns {Error} Erreur formatée
   */
  _handleError(error) {
    if (error.response) {
      const status = error.response.status
      const data = error.response.data
      
      switch (status) {
        case 400:
          return new Error(
            data.detail || 
            'Données invalides. Vérifiez les champs du formulaire.'
          )
        case 404:
          return new Error('Dossier introuvable.')
        case 403:
          return new Error('Vous n\'avez pas l\'autorisation d\'accéder à ce dossier.')
        case 409:
          return new Error('Conflit: ce dossier existe déjà.')
        case 500:
          return new Error('Erreur serveur. Veuillez réessayer plus tard.')
        default:
          return new Error(
            data.detail || 
            `Erreur ${status}: ${error.message}`
          )
      }
    } else if (error.request) {
      return new Error('Impossible de contacter le serveur. Vérifiez votre connexion.')
    } else {
      return new Error(`Erreur: ${error.message}`)
    }
  }
}

export default dossierService
