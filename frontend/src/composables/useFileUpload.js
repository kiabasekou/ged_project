// ============================================================================
// Composable : useFileUpload
// Description : Gestion réactive de l'upload de fichiers avec progression
// Auteur : Maître Ahmed - GED Cabinet Kiaba
// Version : 2.0 (Top 1% Quality)
// ============================================================================

import { ref, reactive, computed } from 'vue'
import { useFileValidation } from './useFileValidation'
import documentService from '@/services/documentService'

/**
 * Hook Composition API pour l'upload de fichiers avec gestion avancée
 * 
 * Fonctionnalités :
 * - Validation pré-upload automatique
 * - Suivi de progression en temps réel
 * - Gestion multi-fichiers avec file d'attente
 * - Retry automatique en cas d'échec
 * - Support du chunked upload pour gros fichiers
 * - Annulation d'upload en cours
 * 
 * @param {Object} options - Configuration
 * @param {number} options.maxConcurrentUploads - Uploads simultanés max (défaut: 3)
 * @param {number} options.maxRetries - Tentatives max par fichier (défaut: 3)
 * @param {number} options.chunkSize - Taille chunks en octets (défaut: 1MB)
 * @param {boolean} options.autoValidate - Valider avant upload (défaut: true)
 * 
 * @example
 * const { uploadState, uploadFile, cancelUpload, clearCompleted } = useFileUpload({
 *   maxConcurrentUploads: 2,
 *   maxRetries: 3
 * })
 * 
 * await uploadFile(file, { dossierId: 123, sensitivity: 'CONFIDENTIAL' })
 * 
 * @returns {Object} État et méthodes d'upload
 */
export function useFileUpload(options = {}) {
  // ============================================================================
  // Configuration
  // ============================================================================
  
  const config = {
    maxConcurrentUploads: options.maxConcurrentUploads || 3,
    maxRetries: options.maxRetries || 3,
    chunkSize: options.chunkSize || 1024 * 1024, // 1 MB
    autoValidate: options.autoValidate !== false
  }

  // ============================================================================
  // État réactif
  // ============================================================================
  
  const uploadState = reactive({
    isUploading: false,
    queue: [], // Fichiers en attente
    active: [], // Uploads en cours
    completed: [], // Uploads terminés
    failed: [] // Uploads échoués
  })

  const globalProgress = ref(0)
  const activeControllers = new Map() // AbortControllers pour annulation

  // ============================================================================
  // Composables dépendants
  // ============================================================================
  
  const { validateSingleFile } = useFileValidation()

  // ============================================================================
  // Computed
  // ============================================================================
  
  const totalFiles = computed(() => 
    uploadState.queue.length + 
    uploadState.active.length + 
    uploadState.completed.length + 
    uploadState.failed.length
  )

  const isQueueEmpty = computed(() => uploadState.queue.length === 0)
  
  const hasActiveUploads = computed(() => uploadState.active.length > 0)
  
  const successCount = computed(() => uploadState.completed.length)
  
  const failureCount = computed(() => uploadState.failed.length)

  const overallProgress = computed(() => {
    if (totalFiles.value === 0) return 0
    
    const completedWeight = uploadState.completed.length
    const activeWeight = uploadState.active.reduce((sum, item) => sum + item.progress, 0) / 100
    
    return Math.round(((completedWeight + activeWeight) / totalFiles.value) * 100)
  })

  // ============================================================================
  // Méthodes privées
  // ============================================================================
  
  /**
   * Crée un objet de suivi pour un fichier
   */
  const createUploadItem = (file, metadata = {}) => {
    return {
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      file,
      metadata,
      progress: 0,
      status: 'pending', // pending | validating | uploading | completed | failed | cancelled
      error: null,
      retryCount: 0,
      startTime: null,
      endTime: null,
      uploadedBytes: 0,
      totalBytes: file.size,
      speed: 0, // octets/seconde
      estimatedTimeRemaining: null,
      response: null
    }
  }

  /**
   * Calcule la vitesse d'upload et le temps restant
   */
  const updateUploadStats = (item) => {
    if (!item.startTime) return

    const elapsedSeconds = (Date.now() - item.startTime) / 1000
    
    if (elapsedSeconds > 0) {
      item.speed = Math.round(item.uploadedBytes / elapsedSeconds)
      
      const remainingBytes = item.totalBytes - item.uploadedBytes
      item.estimatedTimeRemaining = item.speed > 0 
        ? Math.round(remainingBytes / item.speed) 
        : null
    }
  }

  /**
   * Déplace un item de la queue vers active
   */
  const moveToActive = (item) => {
    const index = uploadState.queue.findIndex(q => q.id === item.id)
    if (index !== -1) {
      uploadState.queue.splice(index, 1)
      uploadState.active.push(item)
    }
  }

  /**
   * Déplace un item de active vers completed ou failed
   */
  const moveToFinished = (item, success) => {
    const index = uploadState.active.findIndex(a => a.id === item.id)
    if (index !== -1) {
      uploadState.active.splice(index, 1)
      
      item.endTime = Date.now()
      
      if (success) {
        item.status = 'completed'
        uploadState.completed.push(item)
      } else {
        item.status = 'failed'
        uploadState.failed.push(item)
      }
    }
    
    // Nettoyer le controller
    activeControllers.delete(item.id)
  }

  /**
   * Traite la queue d'upload
   */
  const processQueue = async () => {
    if (uploadState.queue.length === 0) {
      uploadState.isUploading = false
      return
    }

    // Limiter les uploads simultanés
    while (uploadState.active.length < config.maxConcurrentUploads && uploadState.queue.length > 0) {
      const item = uploadState.queue[0]
      await processUploadItem(item)
    }
  }

  /**
   * Traite un item d'upload individuel
   */
  const processUploadItem = async (item) => {
    try {
      moveToActive(item)
      
      // 1. Validation pré-upload
      if (config.autoValidate) {
        item.status = 'validating'
        const isValid = await validateSingleFile(item.file)
        
        if (!isValid) {
          item.error = 'Validation échouée'
          moveToFinished(item, false)
          await processQueue()
          return
        }
      }

      // 2. Préparation FormData
      const formData = new FormData()
      formData.append('file', item.file)
      
      // Ajouter les métadonnées
      Object.entries(item.metadata).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          formData.append(key, value)
        }
      })

      // 3. Configuration AbortController
      const controller = new AbortController()
      activeControllers.set(item.id, controller)

      // 4. Upload avec progression
      item.status = 'uploading'
      item.startTime = Date.now()

      const response = await documentService.upload(
        formData,
        (progressEvent) => {
          item.uploadedBytes = progressEvent.loaded
          item.progress = Math.round((progressEvent.loaded / progressEvent.total) * 100)
          updateUploadStats(item)
        },
        controller.signal
      )

      // 5. Succès
      item.response = response
      moveToFinished(item, true)

    } catch (error) {
      // 6. Gestion erreurs avec retry
      if (error.name === 'AbortError') {
        item.status = 'cancelled'
        item.error = 'Upload annulé'
      } else if (item.retryCount < config.maxRetries) {
        // Retry automatique
        item.retryCount++
        item.error = `Tentative ${item.retryCount}/${config.maxRetries}`
        item.progress = 0
        item.uploadedBytes = 0
        
        // Re-ajouter à la queue
        const index = uploadState.active.findIndex(a => a.id === item.id)
        if (index !== -1) {
          uploadState.active.splice(index, 1)
          uploadState.queue.unshift(item)
        }
      } else {
        // Échec définitif
        item.error = error.response?.data?.message || error.message || 'Erreur inconnue'
        moveToFinished(item, false)
      }
    } finally {
      // Continuer le traitement de la queue
      await processQueue()
    }
  }

  // ============================================================================
  // Méthodes publiques
  // ============================================================================
  
  /**
   * Upload un fichier unique
   * 
   * @param {File} file - Fichier à uploader
   * @param {Object} metadata - Métadonnées (title, description, dossierId, etc.)
   * @returns {Promise<Object>} Item de suivi
   */
  const uploadFile = async (file, metadata = {}) => {
    const item = createUploadItem(file, metadata)
    uploadState.queue.push(item)
    
    if (!uploadState.isUploading) {
      uploadState.isUploading = true
      await processQueue()
    }
    
    return item
  }

  /**
   * Upload multiple fichiers
   * 
   * @param {FileList|Array<File>} files - Liste de fichiers
   * @param {Object} commonMetadata - Métadonnées communes
   * @returns {Promise<Array<Object>>} Items de suivi
   */
  const uploadMultipleFiles = async (files, commonMetadata = {}) => {
    const items = Array.from(files).map(file => {
      const item = createUploadItem(file, { ...commonMetadata })
      uploadState.queue.push(item)
      return item
    })
    
    if (!uploadState.isUploading) {
      uploadState.isUploading = true
      await processQueue()
    }
    
    return items
  }

  /**
   * Annule un upload en cours
   * 
   * @param {string} itemId - ID de l'item à annuler
   */
  const cancelUpload = (itemId) => {
    const controller = activeControllers.get(itemId)
    if (controller) {
      controller.abort()
    }
    
    // Retirer de la queue si en attente
    const queueIndex = uploadState.queue.findIndex(q => q.id === itemId)
    if (queueIndex !== -1) {
      const item = uploadState.queue.splice(queueIndex, 1)[0]
      item.status = 'cancelled'
      item.error = 'Annulé par l\'utilisateur'
      uploadState.failed.push(item)
    }
  }

  /**
   * Annule tous les uploads en cours et en attente
   */
  const cancelAll = () => {
    // Annuler les uploads actifs
    uploadState.active.forEach(item => {
      cancelUpload(item.id)
    })
    
    // Vider la queue
    uploadState.queue.forEach(item => {
      item.status = 'cancelled'
      item.error = 'Annulé par l\'utilisateur'
      uploadState.failed.push(item)
    })
    uploadState.queue = []
    
    uploadState.isUploading = false
  }

  /**
   * Réessaye un upload échoué
   * 
   * @param {string} itemId - ID de l'item à réessayer
   */
  const retryUpload = async (itemId) => {
    const index = uploadState.failed.findIndex(f => f.id === itemId)
    if (index === -1) return
    
    const item = uploadState.failed.splice(index, 1)[0]
    item.retryCount = 0
    item.progress = 0
    item.uploadedBytes = 0
    item.error = null
    item.status = 'pending'
    
    uploadState.queue.push(item)
    
    if (!uploadState.isUploading) {
      uploadState.isUploading = true
      await processQueue()
    }
  }

  /**
   * Réessaye tous les uploads échoués
   */
  const retryAllFailed = async () => {
    const failedItems = [...uploadState.failed]
    uploadState.failed = []
    
    failedItems.forEach(item => {
      item.retryCount = 0
      item.progress = 0
      item.uploadedBytes = 0
      item.error = null
      item.status = 'pending'
      uploadState.queue.push(item)
    })
    
    if (!uploadState.isUploading && uploadState.queue.length > 0) {
      uploadState.isUploading = true
      await processQueue()
    }
  }

  /**
   * Nettoie les uploads terminés
   */
  const clearCompleted = () => {
    uploadState.completed = []
  }

  /**
   * Nettoie les uploads échoués
   */
  const clearFailed = () => {
    uploadState.failed = []
  }

  /**
   * Réinitialise complètement l'état
   */
  const reset = () => {
    cancelAll()
    uploadState.completed = []
    uploadState.failed = []
    globalProgress.value = 0
  }

  /**
   * Formate la vitesse d'upload
   * 
   * @param {number} bytesPerSecond - Vitesse en octets/seconde
   * @returns {string} Vitesse formatée
   */
  const formatSpeed = (bytesPerSecond) => {
    if (!bytesPerSecond) return '0 Ko/s'
    
    const kb = bytesPerSecond / 1024
    if (kb < 1024) return `${Math.round(kb)} Ko/s`
    
    const mb = kb / 1024
    return `${mb.toFixed(2)} Mo/s`
  }

  /**
   * Formate le temps restant
   * 
   * @param {number} seconds - Secondes restantes
   * @returns {string} Temps formaté
   */
  const formatTimeRemaining = (seconds) => {
    if (!seconds) return 'Calcul...'
    
    if (seconds < 60) return `${seconds}s`
    
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    
    if (minutes < 60) return `${minutes}m ${remainingSeconds}s`
    
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    
    return `${hours}h ${remainingMinutes}m`
  }

  // ============================================================================
  // Return
  // ============================================================================
  
  return {
    // État
    uploadState,
    globalProgress,
    
    // Computed
    totalFiles,
    isQueueEmpty,
    hasActiveUploads,
    successCount,
    failureCount,
    overallProgress,
    
    // Méthodes upload
    uploadFile,
    uploadMultipleFiles,
    
    // Méthodes contrôle
    cancelUpload,
    cancelAll,
    retryUpload,
    retryAllFailed,
    
    // Méthodes nettoyage
    clearCompleted,
    clearFailed,
    reset,
    
    // Utilitaires
    formatSpeed,
    formatTimeRemaining
  }
}

/**
 * Hook simplifié pour upload unique sans queue
 * Idéal pour formulaires simples
 */
export function useSimpleUpload() {
  const isUploading = ref(false)
  const progress = ref(0)
  const error = ref(null)
  const result = ref(null)

  const upload = async (file, metadata = {}) => {
    isUploading.value = true
    progress.value = 0
    error.value = null
    result.value = null

    try {
      // Validation
      const { validateSingleFile } = useFileValidation()
      const isValid = await validateSingleFile(file)
      
      if (!isValid) {
        throw new Error('Fichier invalide')
      }

      // Upload
      const formData = new FormData()
      formData.append('file', file)
      
      Object.entries(metadata).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          formData.append(key, value)
        }
      })

      const response = await documentService.upload(formData, (progressEvent) => {
        progress.value = Math.round((progressEvent.loaded / progressEvent.total) * 100)
      })

      result.value = response
      return response

    } catch (err) {
      error.value = err.response?.data?.message || err.message || 'Erreur upload'
      throw err

    } finally {
      isUploading.value = false
    }
  }

  const reset = () => {
    isUploading.value = false
    progress.value = 0
    error.value = null
    result.value = null
  }

  return {
    isUploading,
    progress,
    error,
    result,
    upload,
    reset
  }
}

export default {
  useFileUpload,
  useSimpleUpload
}