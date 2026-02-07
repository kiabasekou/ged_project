// ============================================================================
// Service : Document Service
// Description : Gestion des appels API pour la GED (documents juridiques)
// Auteur : Maître Ahmed - GED Cabinet Kiaba
// ============================================================================

import api from '@/plugins/axios'

/**
 * Service centralisant toutes les opérations liées aux documents
 * Gestion du versionnage, chiffrement, et intégrité des fichiers juridiques
 */
export const documentService = {
  /**
   * Récupère la liste des documents avec filtres et pagination
   * 
   * @param {Object} params - Paramètres de requête
   * @param {string} params.search - Recherche textuelle
   * @param {string} params.dossier - UUID du dossier
   * @param {string} params.folder - UUID du dossier virtuel
   * @param {string} params.sensitivity - Niveau: public, internal, confidential, secret
   * @param {string} params.file_extension - Extension (.pdf, .docx, etc.)
   * @param {string} params.uploaded_by - UUID de l'utilisateur
   * @param {boolean} params.is_current_version - Afficher uniquement versions actuelles
   * @param {number} params.page - Numéro de page
   * @param {number} params.page_size - Éléments par page
   * @param {string} params.ordering - Tri (ex: '-uploaded_at')
   * @returns {Promise<Object>} { results, count, next, previous }
   */
  async fetchList(params = {}) {
    try {
      // Par défaut, afficher uniquement les versions actuelles
      const defaultParams = {
        is_current_version: true,
        ...params
      }
      
      const response = await api.get('/documents/documents/', { params: defaultParams })
      return response.data
    } catch (error) {
      console.error('Erreur récupération liste documents:', error)
      throw this._handleError(error)
    }
  },

  /**
   * Récupère le détail complet d'un document
   * 
   * @param {string} id - UUID du document
   * @returns {Promise<Object>} Données complètes du document
   */
  async fetchDetail(id) {
    try {
      const response = await api.get(`/documents/documents/${id}/`)
      return response.data
    } catch (error) {
      console.error(`Erreur récupération document ${id}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Upload d'un nouveau document
   * 
   * @param {FormData} formData - FormData contenant le fichier et métadonnées
   * @param {Function} onUploadProgress - Callback pour progression
   * @returns {Promise<Object>} Document créé
   * 
   * @example
   * const formData = new FormData()
   * formData.append('file', file)
   * formData.append('dossier', dossierId)
   * formData.append('title', 'Contrat de vente')
   * formData.append('sensitivity', 'confidential')
   * 
   * const doc = await documentService.upload(formData, (progress) => {
   *   console.log(`Upload: ${progress}%`)
   * })
   */
  async upload(formData, onUploadProgress = null) {
    try {
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
      
      if (onUploadProgress) {
        config.onUploadProgress = (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          onUploadProgress(percentCompleted)
        }
      }
      
      const response = await api.post('/documents/documents/', formData, config)
      return response.data
    } catch (error) {
      console.error('Erreur upload document:', error)
      throw this._handleError(error)
    }
  },

  /**
   * Upload d'une nouvelle version d'un document existant
   * Conserve l'historique via le système de versionnage
   * 
   * @param {string} documentId - UUID du document à mettre à jour
   * @param {FormData} formData - FormData contenant le nouveau fichier
   * @param {Function} onUploadProgress - Callback pour progression
   * @returns {Promise<Object>} Nouvelle version du document
   */
  async uploadNewVersion(documentId, formData, onUploadProgress = null) {
    try {
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
      
      if (onUploadProgress) {
        config.onUploadProgress = (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          onUploadProgress(percentCompleted)
        }
      }
      
      const response = await api.post(
        `/documents/documents/${documentId}/new_version/`,
        formData,
        config
      )
      return response.data
    } catch (error) {
      console.error(`Erreur upload nouvelle version du document ${documentId}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Met à jour les métadonnées d'un document (sans changer le fichier)
   * 
   * @param {string} id - UUID du document
   * @param {Object} metadata - Métadonnées à mettre à jour
   * @param {string} metadata.title - Titre du document
   * @param {string} metadata.description - Description
   * @param {string} metadata.sensitivity - Niveau de confidentialité
   * @returns {Promise<Object>} Document mis à jour
   */
  async updateMetadata(id, metadata) {
    try {
      const response = await api.patch(`/documents/documents/${id}/`, metadata)
      return response.data
    } catch (error) {
      console.error(`Erreur mise à jour métadonnées document ${id}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Télécharge un document
   * Retourne le fichier déchiffré prêt à être sauvegardé
   * 
   * @param {string} id - UUID du document
   * @param {string} filename - Nom du fichier pour le download
   * @returns {Promise<void>} Déclenche le téléchargement
   */
  async download(id, filename = null) {
    try {
      const response = await api.get(`/documents/documents/${id}/download/`, {
        responseType: 'blob'
      })
      
      // Créer un lien temporaire pour déclencher le téléchargement
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      
      // Extraire le nom du fichier depuis les headers ou utiliser celui fourni
      const contentDisposition = response.headers['content-disposition']
      let downloadFilename = filename
      
      if (!downloadFilename && contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i)
        if (filenameMatch) {
          downloadFilename = filenameMatch[1]
        }
      }
      
      link.setAttribute('download', downloadFilename || 'document')
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error(`Erreur téléchargement document ${id}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Vérifie l'intégrité d'un document via son hash SHA-256
   * 
   * @param {string} id - UUID du document
   * @returns {Promise<Object>} { valid: boolean, current_hash: string, expected_hash: string }
   */
  async verifyIntegrity(id) {
    try {
      const response = await api.post(`/documents/documents/${id}/verify-integrity/`)
      return response.data
    } catch (error) {
      console.error(`Erreur vérification intégrité document ${id}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Récupère l'historique des versions d'un document
   * 
   * @param {string} id - UUID du document
   * @returns {Promise<Array>} Liste des versions ordonnées
   */
  async fetchVersionHistory(id) {
    try {
      const response = await api.get(`/documents/documents/${id}/history/`)
      return response.data
    } catch (error) {
      console.error(`Erreur récupération historique document ${id}:`, error)
      return []
    }
  },

  /**
   * Restaure une version antérieure d'un document
   * Crée une nouvelle version avec le contenu de la version spécifiée
   * 
   * @param {string} documentId - UUID du document actuel
   * @param {string} versionId - UUID de la version à restaurer
   * @returns {Promise<Object>} Nouvelle version restaurée
   */
  async restoreVersion(documentId, versionId) {
    try {
      const response = await api.post(
        `/documents/documents/${documentId}/restore-version/`,
        { version_id: versionId }
      )
      return response.data
    } catch (error) {
      console.error(`Erreur restauration version ${versionId} du document ${documentId}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Supprime définitivement un document
   * ⚠️ Attention: cette action est irréversible
   * 
   * @param {string} id - UUID du document
   * @returns {Promise<void>}
   */
  async delete(id) {
    try {
      await api.delete(`/documents/documents/${id}/`)
    } catch (error) {
      console.error(`Erreur suppression document ${id}:`, error)
      throw this._handleError(error)
    }
  },

  /**
   * Récupère les documents d'un dossier spécifique
   * 
   * @param {string} dossierId - UUID du dossier
   * @param {Object} options - Options de requête
   * @returns {Promise<Array>} Liste de documents
   */
  async fetchByDossier(dossierId, options = {}) {
    try {
      const response = await api.get('/documents/documents/', {
        params: {
          dossier: dossierId,
          is_current_version: true,
          ordering: '-uploaded_at',
          ...options
        }
      })
      return response.data.results || []
    } catch (error) {
      console.error(`Erreur récupération documents du dossier ${dossierId}:`, error)
      return []
    }
  },

  /**
   * Récupère les documents d'un folder virtuel
   * 
   * @param {string} folderId - UUID du folder
   * @param {Object} options - Options de requête
   * @returns {Promise<Array>} Liste de documents
   */
  async fetchByFolder(folderId, options = {}) {
    try {
      const response = await api.get('/documents/documents/', {
        params: {
          folder: folderId,
          is_current_version: true,
          ordering: 'title',
          ...options
        }
      })
      return response.data.results || []
    } catch (error) {
      console.error(`Erreur récupération documents du folder ${folderId}:`, error)
      return []
    }
  },

  /**
   * Recherche rapide de documents (autocomplétion)
   * 
   * @param {string} query - Terme de recherche
   * @param {number} limit - Nombre maximal de résultats
   * @returns {Promise<Array>} Liste de documents
   */
  async quickSearch(query, limit = 10) {
    try {
      const response = await api.get('/documents/documents/', {
        params: {
          search: query,
          is_current_version: true,
          page_size: limit,
          ordering: '-uploaded_at'
        }
      })
      return response.data.results || []
    } catch (error) {
      console.error('Erreur recherche rapide documents:', error)
      return []
    }
  },

  /**
   * Récupère les statistiques des documents
   * 
   * @param {string} dossierId - UUID du dossier (optionnel)
   * @returns {Promise<Object>}
   * {
   *   total: number,
   *   by_sensitivity: { [key]: number },
   *   by_extension: { [key]: number },
   *   total_size: number
   * }
   */
  async fetchStats(dossierId = null) {
    try {
      const params = dossierId ? { dossier: dossierId } : {}
      const response = await api.get('/documents/documents/stats/', { params })
      return response.data
    } catch (error) {
      console.error('Erreur récupération stats documents:', error)
      return {
        total: 0,
        by_sensitivity: {},
        by_extension: {},
        total_size: 0
      }
    }
  },

  /**
   * Déplace un document vers un autre folder
   * 
   * @param {string} documentId - UUID du document
   * @param {string} targetFolderId - UUID du folder de destination
   * @returns {Promise<Object>} Document mis à jour
   */
  async moveToFolder(documentId, targetFolderId) {
    try {
      const response = await api.patch(`/documents/documents/${documentId}/`, {
        folder: targetFolderId
      })
      return response.data
    } catch (error) {
      console.error(`Erreur déplacement document ${documentId}:`, error)
      throw this._handleError(error)
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
            data.file?.[0] ||
            'Données invalides. Vérifiez le fichier et les métadonnées.'
          )
        case 404:
          return new Error('Document introuvable.')
        case 403:
          return new Error('Vous n\'avez pas l\'autorisation d\'accéder à ce document.')
        case 413:
          return new Error('Fichier trop volumineux. Maximum: 100 MB.')
        case 415:
          return new Error('Type de fichier non supporté.')
        case 500:
          return new Error('Erreur serveur lors du traitement du document.')
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

export default documentService
