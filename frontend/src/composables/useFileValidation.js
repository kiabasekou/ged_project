// ============================================================================
// Composable : useFileValidation
// Description : Gestion réactive de la validation de fichiers
// Auteur : Maître Ahmed - GED Cabinet Kiaba
// ============================================================================

import { ref, reactive, computed } from 'vue'
import { validateFile, validateFileSize, validateExtension, validateMimeType } from '@/utils/fileValidators'
import { generateImagePreview } from '@/services/filePreviewService'

/**
 * Hook Composition API pour la validation de fichiers
 * 
 * @example
 * const { errors, isValidating, validateSingleFile, clearValidation } = useFileValidation()
 * await validateSingleFile(file)
 * if (errors.value.length === 0) { ... }
 * 
 * @returns {Object} État et méthodes de validation
 */
export function useFileValidation() {
  // ============================================================================
  // État réactif
  // ============================================================================
  
  const validationState = reactive({
    isValidating: false,
    errors: [],
    warnings: [],
    validFiles: [],
    invalidFiles: []
  })

  const fileMetadata = ref(null)
  const imagePreview = ref(null)

  // ============================================================================
  // Computed
  // ============================================================================
  
  const hasErrors = computed(() => validationState.errors.length > 0)
  const hasWarnings = computed(() => validationState.warnings.length > 0)
  const isValid = computed(() => !hasErrors.value)
  const errorCount = computed(() => validationState.errors.length)
  const warningCount = computed(() => validationState.warnings.length)

  // ============================================================================
  // Méthodes privées
  // ============================================================================
  
  /**
   * Extrait les métadonnées d'un fichier
   */
  const extractMetadata = (file) => {
    const extension = file.name.split('.').pop().toLowerCase()
    
    return {
      name: file.name,
      size: file.size,
      sizeFormatted: formatFileSize(file.size),
      extension: `.${extension}`,
      mimeType: file.type,
      lastModified: new Date(file.lastModified).toLocaleString('fr-FR'),
      lastModifiedTimestamp: file.lastModified
    }
  }

  /**
   * Formate la taille d'un fichier
   */
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 octet'
    const k = 1024
    const sizes = ['octets', 'Ko', 'Mo', 'Go']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  // ============================================================================
  // Méthodes publiques
  // ============================================================================
  
  /**
   * Valide un seul fichier
   * 
   * @param {File} file - Fichier à valider
   * @returns {Promise<boolean>} True si valide
   */
  const validateSingleFile = async (file) => {
    validationState.isValidating = true
    validationState.errors = []
    validationState.warnings = []
    imagePreview.value = null
    
    try {
      // 1. Extraction des métadonnées
      fileMetadata.value = extractMetadata(file)
      
      // 2. Validation complète
      const result = validateFile(file)
      
      if (!result.valid) {
        validationState.errors.push(result.error)
        validationState.invalidFiles.push(file)
        return false
      }
      
      // 3. Génération de la prévisualisation pour les images
      if (file.type.startsWith('image/')) {
        try {
          imagePreview.value = await generateImagePreview(file)
        } catch (previewError) {
          // Erreur non bloquante
          validationState.warnings.push(
            'Impossible de générer la prévisualisation de l\'image'
          )
        }
      }
      
      // 4. Avertissements potentiels
      if (file.size > 10 * 1024 * 1024) { // > 10 MB
        validationState.warnings.push(
          'Fichier volumineux : le téléversement peut prendre du temps'
        )
      }
      
      validationState.validFiles.push(file)
      return true
      
    } catch (error) {
      console.error('Erreur validation fichier:', error)
      validationState.errors.push(
        `Erreur de validation: ${error.message}`
      )
      return false
      
    } finally {
      validationState.isValidating = false
    }
  }

  /**
   * Valide plusieurs fichiers
   * 
   * @param {FileList|Array<File>} files - Liste de fichiers
   * @returns {Promise<Object>} Résultats de validation
   */
  const validateMultipleFiles = async (files) => {
    validationState.isValidating = true
    validationState.errors = []
    validationState.warnings = []
    validationState.validFiles = []
    validationState.invalidFiles = []
    
    try {
      const fileArray = Array.from(files)
      
      const results = await Promise.all(
        fileArray.map(async (file, index) => {
          const result = validateFile(file)
          
          return {
            file,
            index,
            valid: result.valid,
            error: result.error
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
      
      return {
        totalFiles: fileArray.length,
        validCount: validationState.validFiles.length,
        invalidCount: validationState.invalidFiles.length,
        allValid: validationState.invalidFiles.length === 0
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
        allValid: false
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
   * Ajoute un avertissement personnalisé
   */
  const addWarning = (message) => {
    validationState.warnings.push(message)
  }

  /**
   * Ajoute une erreur personnalisée
   */
  const addError = (message) => {
    validationState.errors.push(message)
  }

  // ============================================================================
  // Return
  // ============================================================================
  
  return {
    // État
    validationState,
    fileMetadata,
    imagePreview,
    
    // Computed
    hasErrors,
    hasWarnings,
    isValid,
    errorCount,
    warningCount,
    
    // Méthodes
    validateSingleFile,
    validateMultipleFiles,
    clearValidation,
    addWarning,
    addError
  }
}

/**
 * Hook simplifié pour validation rapide
 * Utile pour les cas où on a juste besoin d'un booléen
 */
export function useQuickValidation() {
  const validate = async (file) => {
    const result = validateFile(file)
    return result.valid
  }
  
  return { validate }
}
