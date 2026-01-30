// ============================================================================
// Service : Client Service
// Description : Gestion des appels API pour les clients du cabinet
// Auteur : Maître Ahmed - GED Cabinet Kiaba
// ============================================================================

import api from '@/plugins/axios'

/**
 * Service centralisant toutes les opérations liées aux clients
 * Sépare la logique métier de la gestion d'état (stores)
 */
export const clientService = {
  /**
   * Récupère la liste des clients avec filtres et pagination
   * 
   * @param {Object} params - Paramètres de requête
   * @param {string} params.search - Recherche textuelle
   * @param {string} params.client_type - Type: PHYSIQUE ou MORALE
   * @param {boolean} params.is_active - Clients actifs uniquement
   * @param {number} params.page - Numéro de page
   * @param {number} params.page_size - Éléments par page
   * @param {string} params.ordering - Tri (ex: '-created_at')
   * @returns {Promise<Object>} { results, count, next, previous }
   * 
   * @example
   * const { results, count } = await clientService.fetchList({
   *   search: 'Dupont',
   *   client_type: 'PHYSIQUE',
   *   page: 1,
   *   page_size: 25
   * })
   */
  async fetchList(params = {}) {
    try {
      const response = await api.get('/clients/', { params })
      return response.data
    } catch (error) {
      console.error('Erreur récupération liste clients:', error)
      throw this._handleError(error)
    }
  },

  /**
   * Récupère le détail d'un client
   * 
   * @param {string} id - UUID du client
   * @returns {Promise<Object>} Données complètes du client
   * 
   * @throws {Error} Si le client n'existe pas (404)
   */
  async fetchDetail(id) {
    try {
      const response = await api.get(`/clients/${id}/`)
      return response.data
    } catch (error) {
      console.error(`Erreur récupération client ${id}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Crée un nouveau client
   * 
   * @param {Object} clientData - Données du client
   * @param {string} clientData.client_type - PHYSIQUE ou MORALE
   * @param {string} clientData.first_name - Prénom (si physique)
   * @param {string} clientData.last_name - Nom (si physique)
   * @param {string} clientData.company_name - Raison sociale (si morale)
   * @param {string} clientData.nif - NIF (10 chiffres)
   * @param {string} clientData.rccm - RCCM (format GA-LBV-YYYY-AXX-NNNNN)
   * @param {string} clientData.email - Email
   * @param {string} clientData.phone_primary - Téléphone principal
   * @returns {Promise<Object>} Client créé
   * 
   * @example
   * const newClient = await clientService.create({
   *   client_type: 'MORALE',
   *   company_name: 'TotalEnergies Gabon',
   *   nif: '2024888888',
   *   rccm: 'LBV/2024/B/88888',
   *   email: 'contact@example.com',
   *   phone_primary: '+24166000000'
   * })
   */
  async create(clientData) {
    try {
      const response = await api.post('/clients/', clientData)
      return response.data
    } catch (error) {
      console.error('Erreur création client:', error)
      throw this._handleError(error)
    }
  },

  /**
   * Met à jour un client existant
   * 
   * @param {string} id - UUID du client
   * @param {Object} clientData - Données à mettre à jour (partiel autorisé)
   * @returns {Promise<Object>} Client mis à jour
   */
  async update(id, clientData) {
    try {
      const response = await api.patch(`/clients/${id}/`, clientData)
      return response.data
    } catch (error) {
      console.error(`Erreur mise à jour client ${id}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Désactive un client (soft delete)
   * Le client reste dans la base mais est marqué comme inactif
   * 
   * @param {string} id - UUID du client
   * @returns {Promise<void>}
   */
  async deactivate(id) {
    try {
      await api.delete(`/clients/${id}/`)
    } catch (error) {
      console.error(`Erreur désactivation client ${id}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Enregistre le consentement RGPD d'un client
   * Conformité Loi 001/2011 modifiée 2023 (Gabon)
   * 
   * @param {string} id - UUID du client
   * @returns {Promise<Object>} Client avec consentement mis à jour
   * 
   * @example
   * await clientService.grantConsent(clientId)
   * // Le champ consent_given passe à true avec horodatage
   */
  async grantConsent(id) {
    try {
      const response = await api.post(`/clients/${id}/grant-consent/`)
      return response.data
    } catch (error) {
      console.error(`Erreur enregistrement consentement ${id}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Récupère les statistiques globales des clients
   * 
   * @returns {Promise<Object>} 
   * {
   *   total: number,
   *   physiques: number,
   *   moraux: number,
   *   actifs: number,
   *   avec_dossiers: number
   * }
   */
  async fetchStats() {
    try {
      const response = await api.get('/clients/stats/')
      return response.data
    } catch (error) {
      console.error('Erreur récupération stats clients:', error)
      throw this._handleError(error)
    }
  },

  /**
   * Recherche rapide de clients (autocomplétion)
   * 
   * @param {string} query - Terme de recherche
   * @param {number} limit - Nombre maximal de résultats
   * @returns {Promise<Array>} Liste de clients
   * 
   * @example
   * const suggestions = await clientService.quickSearch('Dupont', 5)
   */
  async quickSearch(query, limit = 10) {
    try {
      const response = await api.get('/clients/', {
        params: {
          search: query,
          page_size: limit,
          ordering: '-created_at'
        }
      })
      return response.data.results || []
    } catch (error) {
      console.error('Erreur recherche rapide clients:', error)
      return [] // Retourne un tableau vide en cas d'erreur (UX)
    }
  },

  /**
   * Exporte la liste des clients en CSV
   * 
   * @param {Object} filters - Filtres à appliquer
   * @returns {Promise<Blob>} Fichier CSV
   */
  async exportToCSV(filters = {}) {
    try {
      const response = await api.get('/clients/export/', {
        params: filters,
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      console.error('Erreur export CSV clients:', error)
      throw this._handleError(error)
    }
  },

  /**
   * Vérifie si un NIF existe déjà
   * Utile pour validation en temps réel
   * 
   * @param {string} nif - NIF à vérifier (10 chiffres)
   * @returns {Promise<boolean>} True si existe
   */
  async checkNifExists(nif) {
    try {
      const response = await api.get('/clients/', {
        params: {
          nif: nif,
          page_size: 1
        }
      })
      return response.data.count > 0
    } catch (error) {
      console.error('Erreur vérification NIF:', error)
      return false
    }
  },

  /**
   * Vérifie si un RCCM existe déjà
   * 
   * @param {string} rccm - RCCM à vérifier
   * @returns {Promise<boolean>} True si existe
   */
  async checkRccmExists(rccm) {
    try {
      const response = await api.get('/clients/', {
        params: {
          rccm: rccm,
          page_size: 1
        }
      })
      return response.data.count > 0
    } catch (error) {
      console.error('Erreur vérification RCCM:', error)
      return false
    }
  },

  /**
   * Gestion centralisée des erreurs
   * Transforme les erreurs API en messages exploitables
   * 
   * @private
   * @param {Error} error - Erreur capturée
   * @returns {Error} Erreur formatée
   */
  _handleError(error) {
    if (error.response) {
      // Erreur HTTP du serveur
      const status = error.response.status
      const data = error.response.data
      
      switch (status) {
        case 400:
          return new Error(
            data.detail || 
            'Données invalides. Vérifiez les champs du formulaire.'
          )
        case 404:
          return new Error('Client introuvable.')
        case 409:
          return new Error('Ce client existe déjà (NIF ou RCCM en doublon).')
        case 403:
          return new Error('Vous n\'avez pas l\'autorisation d\'effectuer cette action.')
        case 500:
          return new Error('Erreur serveur. Veuillez réessayer plus tard.')
        default:
          return new Error(
            data.detail || 
            `Erreur ${status}: ${error.message}`
          )
      }
    } else if (error.request) {
      // Requête envoyée mais pas de réponse
      return new Error('Impossible de contacter le serveur. Vérifiez votre connexion.')
    } else {
      // Erreur lors de la configuration de la requête
      return new Error(`Erreur: ${error.message}`)
    }
  }
}

export default clientService
