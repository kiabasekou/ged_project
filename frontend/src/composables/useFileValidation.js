// ============================================================================
// Composable : useFileValidation
// Description : Gestion réactive de la validation de fichiers
// Auteur : Maître Ahmed - GED Cabinet Kiaba
// ============================================================================

i// ============================================================================
// Composable : useFileValidation
// Description : Gestion réactive de la validation de fichiers
// Auteur : Maître Ahmed - GED Cabinet Kiaba
// Version : 2.0 (Top 1% Quality)
// ============================================================================

import { ref, reactive, computed } from 'vue'
import { 
  validateFile, 
  validateFileSize, 
  validateExtension, 
  validateMimeType 
} from '@/utils/fileValidators'
import { generateImagePreview } from '@/services/filePreviewService'
import { FILE_CONSTRAINTS } from '@/constants'

/**
 * Hook Composition API pour la validation de fichiers
 * 
 * Fonctionnalités :
 * - Validation complète (taille, extension, MIME type)
 * - Extraction automatique de métadonnées
 * - Génération de prévisualisations d'images
 * - Validation batch multi-fichiers
 * - Gestion des erreurs et avertissements
 * - Support des règles personnalisées
 * 
 * @param {Object} options - Configuration optionnelle
 * @param {number} options.maxSize - Taille max en octets (défaut: 100MB)
 * @param {Array<string>} options.allowedExtensions - Extensions autorisées
 * @param {Array<string>} options.allowedMimeTypes - Types MIME autorisés
 * @param {boolean} options.generatePreview - Générer preview images (défaut: true)
 * @param {boolean} options.strictMode - Mode strict (défaut: false)
 * 
 * @example
 * const { 
 *   validationState, 
 *   fileMetadata, 
 *   imagePreview,
 *   validateSingleFile,
 *   clearValidation 
 * } = useFileValidation({
 *   maxSize: 50 * 1024 * 1024, // 50 MB
 *   allowedExtensions: ['pdf', 'docx']
 * })
 * 
 * const isValid = await validateSingleFile(file)
 * if (isValid) {
 *   console.log('Métadonnées:', fileMetadata.value)
 *   console.log('Preview:', imagePreview.value)
 * }
 * 
 * @returns {Object} État et méthodes de validation
 */
export function useFileValidation(options = {}) {
  // ============================================================================
  // Configuration
  // ============================================================================
  
  const config = {
    maxSize: options.maxSize || FILE_CONSTRAINTS.MAX_FILE_SIZE,
    allowedExtensions: options.allowedExtensions || FILE_CONSTRAINTS.ALLOWED_EXTENSIONS,
    allowedMimeTypes: options.allowedMimeTypes || FILE_CONSTRAINTS.ALLOWED_MIME_TYPES,
    generatePreview: options.generatePreview !== false,
    strictMode: options.strictMode || false
  }

  // ============================================================================
  // État réactif
  // ============================================================================
  
  const validationState = reactive({
    isValidating: false,
    errors: [],
    warnings: [],
    validFiles: [],
    invalidFiles: [],
    totalValidated: 0,
    lastValidation: null
  })

  const fileMetadata = ref(null)
  const imagePreview = ref(null)
  const validationHistory = ref([])

  // ============================================================================
  // Computed
  // ============================================================================
  
  const hasErrors = computed(() => validationState.errors.length > 0)
  
  const hasWarnings = computed(() => validationState.warnings.length > 0)
  
  const isValid = computed(() => !hasErrors.value)
  
  const errorCount = computed(() => validationState.errors.length)
  
  const warningCount = computed(() => validationState.warnings.length)
  
  const validCount = computed(() => validationState.validFiles.length)
  
  const invalidCount = computed(() => validationState.invalidFiles.length)
  
  const validationSummary = computed(() => ({
    total: validationState.totalValidated,
    valid: validCount.value,
    invalid: invalidCount.value,
    errors: errorCount.value,
    warnings: warningCount.value,
    successRate: validationState.totalValidated > 0 
      ? Math.round((validCount.value / validationState.totalValidated) * 100)
      : 0
  }))

  // ============================================================================
  // Méthodes privées
  // ============================================================================
  
  /**
   * Extrait les métadonnées complètes d'un fichier
   * 
   * @param {File} file - Fichier à analyser
   * @returns {Object} Métadonnées extraites
   */
  const extractMetadata = (file) => {
    const extension = file.name.split('.').pop().toLowerCase()
    const nameWithoutExt = file.name.substring(0, file.name.lastIndexOf('.'))
    
    return {
      // Informations de base
      name: file.name,
      nameWithoutExtension: nameWithoutExt,
      size: file.size,
      sizeFormatted: formatFileSize(file.size),
      extension: `.${extension}`,
      extensionOnly: extension,
      mimeType: file.type,
      
      // Dates
      lastModified: new Date(file.lastModified).toLocaleString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }),
      lastModifiedTimestamp: file.lastModified,
      lastModifiedISO: new Date(file.lastModified).toISOString(),
      
      // Catégorisation
      category: detectFileCategory(extension, file.type),
      isImage: file.type.startsWith('image/'),
      isDocument: ['pdf', 'doc', 'docx', 'odt'].includes(extension),
      isSpreadsheet: ['xls', 'xlsx', 'ods', 'csv'].includes(extension),
      isArchive: ['zip', 'rar', '7z', 'tar', 'gz'].includes(extension),
      
      // Validation flags
      sizeValid: file.size <= config.maxSize,
      extensionValid: config.allowedExtensions.includes(extension),
      mimeTypeValid: !file.type || config.allowedMimeTypes.includes(file.type),
      
      // Métadonnées calculées
      estimatedPageCount: estimatePageCount(file),
      isLargeFile: file.size > 10 * 1024 * 1024, // > 10 MB
      needsCompression: shouldCompress(file)
    }
  }

  /**
   * Détecte la catégorie du fichier
   */
  const detectFileCategory = (extension, mimeType) => {
    if (mimeType.startsWith('image/')) return 'Image'
    if (mimeType.startsWith('video/')) return 'Vidéo'
    if (mimeType.startsWith('audio/')) return 'Audio'
    
    const categories = {
      document: ['pdf', 'doc', 'docx', 'odt', 'rtf', 'txt'],
      spreadsheet: ['xls', 'xlsx', 'ods', 'csv'],
      presentation: ['ppt', 'pptx', 'odp'],
      archive: ['zip', 'rar', '7z', 'tar', 'gz'],
      image: ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'],
      code: ['js', 'py', 'java', 'cpp', 'html', 'css', 'php']
    }
    
    for (const [category, extensions] of Object.entries(categories)) {
      if (extensions.includes(extension)) {
        return category.charAt(0).toUpperCase() + category.slice(1)
      }
    }
    
    return 'Autre'
  }

  /**
   * Estime le nombre de pages d'un document PDF
   */
  const estimatePageCount = (file) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) return null
    
    // Estimation approximative : 50 KB par page en moyenne
    return Math.ceil(file.size / (50 * 1024))
  }

  /**
   * Détermine si le fichier devrait être compressé
   */
  const shouldCompress = (file) => {
    const compressibleTypes = ['image/jpeg', 'image/png', 'image/bmp']
    return compressibleTypes.includes(file.type) && file.size > 2 * 1024 * 1024
  }

  /**
   * Formate la taille d'un fichier
   * 
   * @param {number} bytes - Taille en octets
   * @returns {string} Taille formatée
   */
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 octet'
    
    const k = 1024
    const sizes = ['octets', 'Ko', 'Mo', 'Go', 'To']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    const value = bytes / Math.pow(k, i)
    const formatted = i === 0 ? Math.round(value) : value.toFixed(2)
    
    return `${formatted} ${sizes[i]}`
  }

  /**
   * Valide le nom du fichier (caractères interdits)
   */
  const validateFileName = (fileName) => {
    const invalidChars = /[<>:"/\\|?*\x00-\x1F]/g
    const errors = []
    
    if (invalidChars.test(fileName)) {
      errors.push('Le nom contient des caractères invalides : < > : " / \\ | ? *')
    }
    
    if (fileName.length > 255) {
      errors.push('Le nom du fichier est trop long (max 255 caractères)')
    }
    
    if (fileName.trim() === '') {
      errors.push('Le nom du fichier ne peut pas être vide')
    }
    
    return errors
  }

  /**
   * Ajoute une entrée à l'historique de validation
   */
  const addToHistory = (file, result) => {
    validationHistory.value.unshift({
      timestamp: Date.now(),
      fileName: file.name,
      fileSize: file.size,
      valid: result.valid,
      errors: result.errors || [],
      warnings: result.warnings || []
    })
    
    // Limiter l'historique à 50 entrées
    if (validationHistory.value.length > 50) {
      validationHistory.value = validationHistory.value.slice(0, 50)
    }
  }

  // ============================================================================
  // Méthodes publiques
  // ============================================================================
  
  /**
   * Valide un seul fichier avec toutes les vérifications
   * 
   * @param {File} file - Fichier à valider
   * @param {Object} customRules - Règles de validation personnalisées
   * @returns {Promise<boolean>} True si valide
   */
  const validateSingleFile = async (file, customRules = {}) => {
    validationState.isValidating = true
    validationState.errors = []
    validationState.warnings = []
    imagePreview.value = null
    
    try {
      // 0. Vérification fichier null/undefined
      if (!file) {
        validationState.errors.push('Aucun fichier sélectionné')
        return false
      }

      // 1. Extraction des métadonnées
      fileMetadata.value = extractMetadata(file)
      
      // 2. Validation du nom de fichier
      const nameErrors = validateFileName(file.name)
      if (nameErrors.length > 0) {
        validationState.errors.push(...nameErrors)
      }
      
      // 3. Validation complète via utilitaire
      const validationResult = validateFile(file, {
        maxSize: customRules.maxSize || config.maxSize,
        allowedExtensions: customRules.allowedExtensions || config.allowedExtensions,
        allowedMimeTypes: customRules.allowedMimeTypes || config.allowedMimeTypes
      })
      
      if (!validationResult.valid) {
        validationState.errors.push(validationResult.error)
        validationState.invalidFiles.push(file)
        
        // Historique
        addToHistory(file, { 
          valid: false, 
          errors: [validationResult.error] 
        })
        
        return false
      }
      
      // 4. Avertissements (non bloquants)
      if (file.size > 10 * 1024 * 1024) {
        validationState.warnings.push(
          `Fichier volumineux (${fileMetadata.value.sizeFormatted}): le téléversement peut prendre du temps`
        )
      }
      
      if (fileMetadata.value.needsCompression) {
        validationState.warnings.push(
          'Ce fichier pourrait bénéficier d\'une compression pour réduire sa taille'
        )
      }
      
      if (!file.type) {
        validationState.warnings.push(
          'Type MIME non détecté, la validation est basée uniquement sur l\'extension'
        )
      }
      
      // 5. Génération de la prévisualisation pour les images
      if (config.generatePreview && fileMetadata.value.isImage) {
        try {
          imagePreview.value = await generateImagePreview(file)
        } catch (previewError) {
          console.warn('Erreur génération preview:', previewError)
          validationState.warnings.push(
            'Impossible de générer la prévisualisation de l\'image'
          )
        }
      }
      
      // 6. Validation réussie
      validationState.validFiles.push(file)
      validationState.totalValidated++
      validationState.lastValidation = new Date().toISOString()
      
      // Historique
      addToHistory(file, { 
        valid: true, 
        warnings: validationState.warnings 
      })
      
      return true
      
    } catch (error) {
      console.error('Erreur validation fichier:', error)
      validationState.errors.push(
        `Erreur de validation: ${error.message}`
      )
      validationState.invalidFiles.push(file)
      
      return false
      
    } finally {
      validationState.isValidating = false
    }
  }

  /**
   * Valide plusieurs fichiers en batch
   * 
   * @param {FileList|Array<File>} files - Liste de fichiers
   * @param {Object} customRules - Règles personnalisées
   * @returns {Promise<Object>} Résultats détaillés
   */
  const validateMultipleFiles = async (files, customRules = {}) => {
    validationState.isValidating = true
    validationState.errors = []
    validationState.warnings = []
    validationState.validFiles = []
    validationState.invalidFiles = []
    
    try {
      const fileArray = Array.from(files)
      
      // Validation parallèle
      const results = await Promise.all(
        fileArray.map(async (file, index) => {
          try {
            const result = validateFile(file, {
              maxSize: customRules.maxSize || config.maxSize,
              allowedExtensions: customRules.allowedExtensions || config.allowedExtensions,
              allowedMimeTypes: customRules.allowedMimeTypes || config.allowedMimeTypes
            })
            
            return {
              file,
              index,
              valid: result.valid,
              error: result.error,
              metadata: extractMetadata(file)
            }
          } catch (error) {
            return {
              file,
              index,
              valid: false,
              error: error.message,
              metadata: null
            }
          }
        })
      )
      
      // Séparation des fichiers valides et invalides
      results.forEach(result => {
        if (result.valid) {
          validationState.validFiles.push(result.file)
        } else {
          validationState.invalidFiles.push(result.file)
          validationState.errors.push(
            `Fichier ${result.index + 1} (${result.file.name}): ${result.error}`
          )
        }
      })
      
      validationState.totalValidated += fileArray.length
      validationState.lastValidation = new Date().toISOString()
      
      // Avertissements globaux
      const totalSize = fileArray.reduce((sum, f) => sum + f.size, 0)
      if (totalSize > 100 * 1024 * 1024) {
        validationState.warnings.push(
          `Taille totale importante (${formatFileSize(totalSize)})`
        )
      }
      
      return {
        totalFiles: fileArray.length,
        validCount: validationState.validFiles.length,
        invalidCount: validationState.invalidFiles.length,
        allValid: validationState.invalidFiles.length === 0,
        validFiles: validationState.validFiles,
        invalidFiles: validationState.invalidFiles,
        errors: validationState.errors,
        warnings: validationState.warnings
      }
      
    } catch (error) {
      console.error('Erreur validation multiple:', error)
      validationState.errors.push(
        `Erreur de validation: ${error.message}`
      )
      
      return {
        totalFiles: files.length,
        validCount: 0,
        invalidCount: files.length,
        allValid: false,
        validFiles: [],
        invalidFiles: Array.from(files),
        errors: validationState.errors,
        warnings: []
      }
      
    } finally {
      validationState.isValidating = false
    }
  }

  /**
   * Réinitialise l'état de validation
   */
  const clearValidation = () => {
    validationState.errors = []
    validationState.warnings = []
    validationState.validFiles = []
    validationState.invalidFiles = []
    fileMetadata.value = null
    imagePreview.value = null
  }

  /**
   * Réinitialise complètement (y compris l'historique)
   */
  const resetAll = () => {
    clearValidation()
    validationState.totalValidated = 0
    validationState.lastValidation = null
    validationHistory.value = []
  }

  /**
   * Ajoute un avertissement personnalisé
   * 
   * @param {string} message - Message d'avertissement
   */
  const addWarning = (message) => {
    if (!validationState.warnings.includes(message)) {
      validationState.warnings.push(message)
    }
  }

  /**
   * Ajoute une erreur personnalisée
   * 
   * @param {string} message - Message d'erreur
   */
  const addError = (message) => {
    if (!validationState.errors.includes(message)) {
      validationState.errors.push(message)
    }
  }

  /**
   * Supprime une erreur spécifique
   * 
   * @param {number} index - Index de l'erreur
   */
  const removeError = (index) => {
    if (index >= 0 && index < validationState.errors.length) {
      validationState.errors.splice(index, 1)
    }
  }

  /**
   * Supprime un avertissement spécifique
   * 
   * @param {number} index - Index de l'avertissement
   */
  const removeWarning = (index) => {
    if (index >= 0 && index < validationState.warnings.length) {
      validationState.warnings.splice(index, 1)
    }
  }

  // ============================================================================
  // Return
  // ============================================================================
  
  return {
    // État
    validationState,
    fileMetadata,
    imagePreview,
    validationHistory,
    
    // Computed
    hasErrors,
    hasWarnings,
    isValid,
    errorCount,
    warningCount,
    validCount,
    invalidCount,
    validationSummary,
    
    // Méthodes validation
    validateSingleFile,
    validateMultipleFiles,
    
    // Méthodes gestion état
    clearValidation,
    resetAll,
    addWarning,
    addError,
    removeError,
    removeWarning,
    
    // Utilitaires
    formatFileSize,
    extractMetadata
  }
}

/**
 * Hook simplifié pour validation rapide
 * Idéal pour validation synchrone sans métadonnées
 * 
 * @returns {Object} Méthode de validation simple
 */
export function useQuickValidation() {
  const isValid = ref(false)
  const error = ref(null)

  const validate = (file, options = {}) => {
    const result = validateFile(file, options)
    isValid.value = result.valid
    error.value = result.error
    return result.valid
  }
  
  return { 
    isValid, 
    error, 
    validate 
  }
}

export default {
  useFileValidation,
  useQuickValidation
}