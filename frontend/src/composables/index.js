// ============================================================================
// Index Composables - GED Cabinet Kiaba
// Description : Point d'entrée centralisé pour tous les composables
// Auteur : Maître Ahmed
// Version : 2.0
// ============================================================================

/**
 * COMPOSABLES - UPLOAD DE FICHIERS
 * 
 * Gestion complète de l'upload avec progression, retry et queue
 */
export { 
  useFileUpload,      // Upload avancé avec queue et retry
  useSimpleUpload     // Upload simple pour formulaires
} from './useFileUpload'

/**
 * COMPOSABLES - VALIDATION DE FICHIERS
 * 
 * Validation complète avec métadonnées et prévisualisation
 */
export { 
  useFileValidation,  // Validation complète avec métadonnées
  useQuickValidation  // Validation rapide (booléen simple)
} from './useFileValidation'

/**
 * COMPOSABLES - OPTIMISATION PERFORMANCES
 * 
 * Debouncing, throttling et auto-save
 */
export { 
  useDebounce,           // Debounce valeur réactive
  useDebouncedFn,        // Debounce fonction
  useDebouncedSearch,    // Recherche debouncée avec loading
  useThrottle,           // Throttle fonction
  useDebouncedThrottle,  // Combinaison debounce + throttle
  useAutoSave            // Auto-save avec debounce
} from './useDebounce'

// ============================================================================
// GUIDE D'UTILISATION RAPIDE
// ============================================================================

/**
 * EXEMPLE 1 : Upload simple
 * 
 * import { useSimpleUpload } from '@/composables'
 * 
 * const { isUploading, progress, upload } = useSimpleUpload()
 * 
 * await upload(file, { dossierId: 123 })
 */

/**
 * EXEMPLE 2 : Upload avancé avec queue
 * 
 * import { useFileUpload } from '@/composables'
 * 
 * const { 
 *   uploadState, 
 *   uploadFile, 
 *   cancelUpload,
 *   overallProgress 
 * } = useFileUpload({
 *   maxConcurrentUploads: 3,
 *   maxRetries: 3
 * })
 * 
 * await uploadFile(file, { dossierId: 123 })
 */

/**
 * EXEMPLE 3 : Validation fichier
 * 
 * import { useFileValidation } from '@/composables'
 * 
 * const { 
 *   validationState, 
 *   fileMetadata, 
 *   validateSingleFile 
 * } = useFileValidation()
 * 
 * const isValid = await validateSingleFile(file)
 * if (isValid) {
 *   console.log('Métadonnées:', fileMetadata.value)
 * } else {
 *   console.error('Erreurs:', validationState.errors)
 * }
 */

/**
 * EXEMPLE 4 : Recherche debouncée
 * 
 * import { useDebouncedSearch } from '@/composables'
 * 
 * const { 
 *   results, 
 *   isLoading, 
 *   execute 
 * } = useDebouncedSearch(
 *   async (query) => await api.search(query),
 *   400,
 *   { minLength: 2 }
 * )
 * 
 * execute('recherche')
 */

/**
 * EXEMPLE 5 : Auto-save
 * 
 * import { useAutoSave } from '@/composables'
 * 
 * const { 
 *   isSaving, 
 *   lastSaved, 
 *   save 
 * } = useAutoSave(
 *   async (data) => await api.save(data),
 *   2000
 * )
 * 
 * watch(formData, () => save(formData.value), { deep: true })
 */

// ============================================================================
// EXPORTS PAR CATÉGORIE
// ============================================================================

/**
 * Upload de fichiers
 */
export const uploadComposables = {
  useFileUpload,
  useSimpleUpload
}

/**
 * Validation de fichiers
 */
export const validationComposables = {
  useFileValidation,
  useQuickValidation
}

/**
 * Optimisation performances
 */
export const performanceComposables = {
  useDebounce,
  useDebouncedFn,
  useDebouncedSearch,
  useThrottle,
  useDebouncedThrottle,
  useAutoSave
}

/**
 * Export par défaut avec tous les composables
 */
export default {
  // Upload
  useFileUpload,
  useSimpleUpload,
  
  // Validation
  useFileValidation,
  useQuickValidation,
  
  // Performance
  useDebounce,
  useDebouncedFn,
  useDebouncedSearch,
  useThrottle,
  useDebouncedThrottle,
  useAutoSave
}