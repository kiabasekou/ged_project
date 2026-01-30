// ============================================================================
// Composable : useDebounce
// Description : Gestion du debouncing pour optimiser les recherches
// Auteur : Maître Ahmed - GED Cabinet Kiaba
// ============================================================================

import { ref, watch, onUnmounted } from 'vue'

/**
 * Hook pour debouncing de valeurs réactives
 * Utile pour éviter trop de requêtes API lors de la saisie
 * 
 * @param {Ref} value - Valeur réactive à debouncer
 * @param {number} delay - Délai en millisecondes (défaut: 300ms)
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
export function useDebounce(value, delay = 300) {
  const debouncedValue = ref(value.value)
  let timeoutId = null

  // Observer les changements de la valeur source
  const unwatch = watch(value, (newValue) => {
    // Annuler le timeout précédent
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    // Créer un nouveau timeout
    timeoutId = setTimeout(() => {
      debouncedValue.value = newValue
    }, delay)
  })

  // Nettoyage lors de la destruction du composant
  onUnmounted(() => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    unwatch()
  })

  return debouncedValue
}

/**
 * Hook pour debouncer une fonction
 * Retourne une version debouncée de la fonction fournie
 * 
 * @param {Function} fn - Fonction à debouncer
 * @param {number} delay - Délai en millisecondes
 * @returns {Function} Fonction debouncée
 * 
 * @example
 * const handleSearch = useDebouncedFn((query) => {
 *   api.search(query)
 * }, 400)
 * 
 * // Appels multiples, mais une seule exécution après 400ms
 * handleSearch('test')
 * handleSearch('test1')
 * handleSearch('test12') // Seul celui-ci sera exécuté
 */
export function useDebouncedFn(fn, delay = 300) {
  let timeoutId = null

  const debouncedFn = (...args) => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    timeoutId = setTimeout(() => {
      fn(...args)
    }, delay)
  }

  // Fonction pour annuler le debounce en cours
  debouncedFn.cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
  }

  // Fonction pour exécuter immédiatement
  debouncedFn.flush = (...args) => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
    fn(...args)
  }

  // Nettoyage
  onUnmounted(() => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
  })

  return debouncedFn
}

/**
 * Hook pour debouncer avec gestion du loading
 * Idéal pour les recherches avec indicateur de chargement
 * 
 * @param {Function} fn - Fonction asynchrone à debouncer
 * @param {number} delay - Délai en millisecondes
 * @returns {Object} { execute, isLoading, cancel }
 * 
 * @example
 * const { execute, isLoading } = useDebouncedSearch(
 *   async (query) => {
 *     const results = await api.search(query)
 *     return results
 *   },
 *   500
 * )
 * 
 * // Dans le template
 * <v-progress-circular v-if="isLoading" />
 * 
 * // Lors de la saisie
 * execute(searchQuery.value)
 */
export function useDebouncedSearch(fn, delay = 300) {
  const isLoading = ref(false)
  let timeoutId = null
  let abortController = null

  const execute = async (...args) => {
    // Annuler la recherche précédente
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    
    if (abortController) {
      abortController.abort()
    }

    return new Promise((resolve, reject) => {
      timeoutId = setTimeout(async () => {
        isLoading.value = true
        abortController = new AbortController()

        try {
          const result = await fn(...args, abortController.signal)
          resolve(result)
        } catch (error) {
          if (error.name !== 'AbortError') {
            reject(error)
          }
        } finally {
          isLoading.value = false
          abortController = null
        }
      }, delay)
    })
  }

  const cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
    
    if (abortController) {
      abortController.abort()
      abortController = null
    }
    
    isLoading.value = false
  }

  onUnmounted(() => {
    cancel()
  })

  return {
    execute,
    isLoading,
    cancel
  }
}

/**
 * Hook pour throttling (alternative au debounce)
 * Garantit qu'une fonction est appelée au maximum une fois par intervalle
 * 
 * @param {Function} fn - Fonction à throttler
 * @param {number} limit - Intervalle minimum entre les appels (ms)
 * @returns {Function} Fonction throttlée
 * 
 * @example
 * const handleScroll = useThrottle(() => {
 *   console.log('Scroll event')
 * }, 200)
 * 
 * window.addEventListener('scroll', handleScroll)
 */
export function useThrottle(fn, limit = 300) {
  let inThrottle = false
  let lastResult = null

  const throttledFn = (...args) => {
    if (!inThrottle) {
      lastResult = fn(...args)
      inThrottle = true

      setTimeout(() => {
        inThrottle = false
      }, limit)
    }

    return lastResult
  }

  return throttledFn
}

/**
 * Hook combiné debounce + throttle
 * Utile pour scroll avec recherche
 * 
 * @param {Function} fn - Fonction à optimiser
 * @param {Object} options - Options de configuration
 * @returns {Function} Fonction optimisée
 * 
 * @example
 * const optimizedSearch = useDebouncedThrottle(
 *   (query) => api.search(query),
 *   { debounce: 300, throttle: 1000 }
 * )
 */
export function useDebouncedThrottle(fn, options = {}) {
  const { debounce: debounceDelay = 300, throttle: throttleDelay = 1000 } = options
  
  let debounceTimeout = null
  let throttleTimeout = null
  let lastExecution = 0

  const optimizedFn = (...args) => {
    const now = Date.now()
    
    // Nettoyer le debounce précédent
    if (debounceTimeout) {
      clearTimeout(debounceTimeout)
    }

    // Throttle: si pas assez de temps écoulé, debouncer
    if (now - lastExecution < throttleDelay) {
      debounceTimeout = setTimeout(() => {
        lastExecution = Date.now()
        fn(...args)
      }, debounceDelay)
    } else {
      // Throttle: assez de temps écoulé, exécuter immédiatement
      lastExecution = now
      fn(...args)
    }
  }

  optimizedFn.cancel = () => {
    if (debounceTimeout) clearTimeout(debounceTimeout)
    if (throttleTimeout) clearTimeout(throttleTimeout)
  }

  onUnmounted(() => {
    optimizedFn.cancel()
  })

  return optimizedFn
}

export default {
  useDebounce,
  useDebouncedFn,
  useDebouncedSearch,
  useThrottle,
  useDebouncedThrottle
}
