// ============================================================================
// Composable : useDebounce
// Description : Optimisation des recherches et saisies avec debouncing/throttling
// Auteur : Maître Ahmed - GED Cabinet Kiaba
// Version : 2.0 (Top 1% Quality)
// ============================================================================

import { ref, watch, onUnmounted, computed } from 'vue'

/**
 * Hook pour debouncing de valeurs réactives
 * 
 * Le debouncing retarde l'exécution d'une fonction jusqu'à ce qu'un certain
 * temps se soit écoulé sans nouvelle invocation. Idéal pour les champs de recherche.
 * 
 * @param {Ref} value - Valeur réactive à debouncer
 * @param {number} delay - Délai en millisecondes (défaut: 300ms)
 * @param {Object} options - Options avancées
 * @param {boolean} options.immediate - Exécuter immédiatement la première fois
 * @param {number} options.maxWait - Temps max d'attente avant exécution forcée
 * 
 * @returns {Ref} Valeur debouncée
 * 
 * @example
 * const searchQuery = ref('')
 * const debouncedQuery = useDebounce(searchQuery, 500)
 * 
 * watch(debouncedQuery, (newVal) => {
 *   // Déclenché seulement 500ms après la dernière modification
 *   performSearch(newVal)
 * })
 */
export function useDebounce(value, delay = 300, options = {}) {
  const { immediate = false, maxWait = null } = options
  
  const debouncedValue = ref(immediate ? value.value : null)
  let timeoutId = null
  let maxWaitTimeoutId = null
  let lastCallTime = null

  // Observer les changements de la valeur source
  const unwatch = watch(value, (newValue) => {
    // Enregistrer le moment de l'appel
    const now = Date.now()
    
    // Première invocation
    if (lastCallTime === null) {
      lastCallTime = now
      
      if (immediate) {
        debouncedValue.value = newValue
      }
    }

    // Annuler le timeout précédent
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    // MaxWait: forcer l'exécution si trop de temps écoulé
    if (maxWait && !maxWaitTimeoutId) {
      maxWaitTimeoutId = setTimeout(() => {
        debouncedValue.value = newValue
        lastCallTime = null
        maxWaitTimeoutId = null
      }, maxWait)
    }

    // Créer un nouveau timeout
    timeoutId = setTimeout(() => {
      debouncedValue.value = newValue
      lastCallTime = null
      
      // Nettoyer maxWait timeout
      if (maxWaitTimeoutId) {
        clearTimeout(maxWaitTimeoutId)
        maxWaitTimeoutId = null
      }
    }, delay)
  })

  // Nettoyage lors de la destruction du composant
  onUnmounted(() => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    if (maxWaitTimeoutId) {
      clearTimeout(maxWaitTimeoutId)
    }
    unwatch()
  })

  return debouncedValue
}

/**
 * Hook pour debouncer une fonction
 * 
 * Retourne une version debouncée de la fonction fournie.
 * La fonction ne sera exécutée qu'après un délai sans nouvelle invocation.
 * 
 * @param {Function} fn - Fonction à debouncer
 * @param {number} delay - Délai en millisecondes (défaut: 300ms)
 * @param {Object} options - Options
 * @param {boolean} options.immediate - Exécuter au premier appel
 * 
 * @returns {Function} Fonction debouncée avec méthode .cancel()
 * 
 * @example
 * const debouncedSave = useDebouncedFn(
 *   (data) => api.save(data),
 *   1000
 * )
 * 
 * // Sera exécuté seulement 1s après le dernier appel
 * debouncedSave(formData)
 * 
 * // Annuler l'exécution en attente
 * debouncedSave.cancel()
 */
export function useDebouncedFn(fn, delay = 300, options = {}) {
  const { immediate = false } = options
  
  let timeoutId = null
  let lastArgs = null
  let lastThis = null
  let result = null

  const debouncedFn = function(...args) {
    lastArgs = args
    lastThis = this

    const callNow = immediate && !timeoutId

    // Annuler le timeout précédent
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    // Planifier la nouvelle exécution
    timeoutId = setTimeout(() => {
      timeoutId = null
      if (!immediate) {
        result = fn.apply(lastThis, lastArgs)
      }
    }, delay)

    // Exécution immédiate si option activée
    if (callNow) {
      result = fn.apply(lastThis, lastArgs)
    }

    return result
  }

  // Méthode pour annuler le debounce en cours
  debouncedFn.cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
  }

  // Méthode pour forcer l'exécution immédiate
  debouncedFn.flush = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
      return fn.apply(lastThis, lastArgs)
    }
  }

  // Nettoyage
  onUnmounted(() => {
    debouncedFn.cancel()
  })

  return debouncedFn
}

/**
 * Hook pour recherche debouncée avec état de chargement
 * 
 * Combine debouncing et gestion d'état pour les recherches asynchrones.
 * Gère automatiquement les états de chargement et les erreurs.
 * 
 * @param {Function} searchFn - Fonction de recherche asynchrone
 * @param {number} delay - Délai de debounce (défaut: 400ms)
 * @param {Object} options - Options
 * @param {number} options.minLength - Longueur min pour déclencher (défaut: 0)
 * @param {*} options.initialValue - Valeur initiale des résultats
 * 
 * @returns {Object} État et méthodes de recherche
 * 
 * @example
 * const { 
 *   results, 
 *   isLoading, 
 *   error, 
 *   execute, 
 *   clear 
 * } = useDebouncedSearch(
 *   async (query) => {
 *     const res = await api.search(query)
 *     return res.data
 *   },
 *   400,
 *   { minLength: 3 }
 * )
 * 
 * // Dans le template
 * <input @input="execute($event.target.value)" />
 * <div v-if="isLoading">Recherche...</div>
 * <div v-for="item in results">{{ item }}</div>
 */
export function useDebouncedSearch(searchFn, delay = 400, options = {}) {
  const { minLength = 0, initialValue = [] } = options

  const results = ref(initialValue)
  const isLoading = ref(false)
  const error = ref(null)
  const lastQuery = ref('')
  const abortController = ref(null)

  let timeoutId = null

  const execute = (query) => {
    lastQuery.value = query

    // Annuler la recherche précédente
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    // Annuler la requête HTTP en cours
    if (abortController.value) {
      abortController.value.abort()
    }

    // Vérifier la longueur minimale
    if (query.length < minLength) {
      results.value = initialValue
      isLoading.value = false
      error.value = null
      return
    }

    // Debounce
    isLoading.value = true
    error.value = null

    timeoutId = setTimeout(async () => {
      try {
        // Créer un nouveau AbortController
        abortController.value = new AbortController()

        const searchResults = await searchFn(query, abortController.value.signal)
        
        // Vérifier que c'est toujours la dernière recherche
        if (query === lastQuery.value) {
          results.value = searchResults
          error.value = null
        }

      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Erreur recherche:', err)
          error.value = err.message || 'Erreur de recherche'
          results.value = initialValue
        }

      } finally {
        if (query === lastQuery.value) {
          isLoading.value = false
        }
      }
    }, delay)
  }

  const clear = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    if (abortController.value) {
      abortController.value.abort()
    }
    results.value = initialValue
    isLoading.value = false
    error.value = null
    lastQuery.value = ''
  }

  // Nettoyage
  onUnmounted(() => {
    clear()
  })

  return {
    results,
    isLoading,
    error,
    lastQuery: computed(() => lastQuery.value),
    execute,
    clear
  }
}

/**
 * Hook pour throttling de fonction
 * 
 * Le throttling garantit qu'une fonction n'est exécutée qu'une fois
 * par période de temps, même si invoquée plusieurs fois.
 * Idéal pour scroll, resize, mousemove.
 * 
 * @param {Function} fn - Fonction à throttler
 * @param {number} limit - Intervalle minimum en ms (défaut: 300ms)
 * @param {Object} options - Options
 * @param {boolean} options.leading - Exécuter au début (défaut: true)
 * @param {boolean} options.trailing - Exécuter à la fin (défaut: true)
 * 
 * @returns {Function} Fonction throttlée
 * 
 * @example
 * const handleScroll = useThrottle(
 *   () => console.log('Scroll position:', window.scrollY),
 *   200
 * )
 * 
 * window.addEventListener('scroll', handleScroll)
 */
export function useThrottle(fn, limit = 300, options = {}) {
  const { leading = true, trailing = true } = options
  
  let lastRan = null
  let lastFunc = null
  let result = null

  const throttledFn = function(...args) {
    const context = this
    const now = Date.now()

    if (!lastRan) {
      if (leading) {
        result = fn.apply(context, args)
        lastRan = now
      }
    } else {
      // Annuler le trailing précédent
      if (lastFunc) {
        clearTimeout(lastFunc)
      }

      if (now - lastRan >= limit) {
        result = fn.apply(context, args)
        lastRan = now
      } else if (trailing) {
        // Planifier un trailing call
        lastFunc = setTimeout(() => {
          result = fn.apply(context, args)
          lastRan = Date.now()
          lastFunc = null
        }, limit - (now - lastRan))
      }
    }

    return result
  }

  throttledFn.cancel = () => {
    if (lastFunc) {
      clearTimeout(lastFunc)
      lastFunc = null
    }
    lastRan = null
  }

  onUnmounted(() => {
    throttledFn.cancel()
  })

  return throttledFn
}

/**
 * Hook combiné debounce + throttle
 * 
 * Combine debouncing et throttling pour un contrôle maximal.
 * La fonction sera throttlée pour éviter les exécutions trop fréquentes,
 * et debouncée pour attendre la fin des saisies rapides.
 * 
 * Cas d'usage : Recherche avec scroll infini
 * 
 * @param {Function} fn - Fonction à optimiser
 * @param {Object} options - Configuration
 * @param {number} options.debounce - Délai debounce (défaut: 300ms)
 * @param {number} options.throttle - Délai throttle (défaut: 1000ms)
 * 
 * @returns {Function} Fonction optimisée
 * 
 * @example
 * const optimizedSearch = useDebouncedThrottle(
 *   (query) => api.search(query),
 *   { debounce: 300, throttle: 1000 }
 * )
 * 
 * // Saisie rapide → attendre 300ms après la dernière saisie
 * // Saisie lente continue → max 1 appel par seconde
 */
export function useDebouncedThrottle(fn, options = {}) {
  const { 
    debounce: debounceDelay = 300, 
    throttle: throttleDelay = 1000 
  } = options
  
  let debounceTimeout = null
  let lastExecution = 0
  let pendingArgs = null

  const optimizedFn = function(...args) {
    const now = Date.now()
    pendingArgs = args

    // Nettoyer le debounce précédent
    if (debounceTimeout) {
      clearTimeout(debounceTimeout)
    }

    // Throttle: si pas assez de temps écoulé, debouncer
    const timeSinceLastExecution = now - lastExecution

    if (timeSinceLastExecution >= throttleDelay) {
      // Assez de temps écoulé → exécuter immédiatement
      lastExecution = now
      return fn.apply(this, args)
    } else {
      // Pas assez de temps → debouncer
      return new Promise((resolve) => {
        debounceTimeout = setTimeout(() => {
          lastExecution = Date.now()
          resolve(fn.apply(this, pendingArgs))
        }, debounceDelay)
      })
    }
  }

  optimizedFn.cancel = () => {
    if (debounceTimeout) {
      clearTimeout(debounceTimeout)
      debounceTimeout = null
    }
    pendingArgs = null
  }

  onUnmounted(() => {
    optimizedFn.cancel()
  })

  return optimizedFn
}

/**
 * Hook pour auto-save avec debounce
 * 
 * Sauvegarde automatiquement les données après un délai sans modification.
 * Gère les états de sauvegarde, erreurs et dernière sauvegarde.
 * 
 * @param {Function} saveFn - Fonction de sauvegarde asynchrone
 * @param {number} delay - Délai avant sauvegarde (défaut: 2000ms)
 * 
 * @returns {Object} État et méthodes
 * 
 * @example
 * const { 
 *   isSaving, 
 *   lastSaved, 
 *   error, 
 *   save, 
 *   saveNow 
 * } = useAutoSave(
 *   async (data) => await api.updateDocument(data),
 *   2000
 * )
 * 
 * // Auto-save après 2s de non-modification
 * watch(formData, () => save(formData.value), { deep: true })
 */
export function useAutoSave(saveFn, delay = 2000) {
  const isSaving = ref(false)
  const lastSaved = ref(null)
  const error = ref(null)
  const hasUnsavedChanges = ref(false)

  let timeoutId = null

  const save = (data) => {
    hasUnsavedChanges.value = true

    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    timeoutId = setTimeout(async () => {
      await saveNow(data)
    }, delay)
  }

  const saveNow = async (data) => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    isSaving.value = true
    error.value = null

    try {
      await saveFn(data)
      lastSaved.value = new Date()
      hasUnsavedChanges.value = false
    } catch (err) {
      console.error('Erreur auto-save:', err)
      error.value = err.message || 'Erreur de sauvegarde'
    } finally {
      isSaving.value = false
    }
  }

  const cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
  }

  onUnmounted(() => {
    cancel()
  })

  return {
    isSaving,
    lastSaved,
    error,
    hasUnsavedChanges: computed(() => hasUnsavedChanges.value),
    save,
    saveNow,
    cancel
  }
}

// ============================================================================
// Exports
// ============================================================================

export default {
  useDebounce,
  useDebouncedFn,
  useDebouncedSearch,
  useThrottle,
  useDebouncedThrottle,
  useAutoSave
}