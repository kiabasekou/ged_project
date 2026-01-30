// ============================================================================
// Constantes : Application Frontend
// Description : Constantes centralisées pour tout le projet
// Auteur : Maître Ahmed - GED Cabinet Kiaba
// ============================================================================

/**
 * Configuration de l'application
 */
export const APP_CONFIG = {
  NAME: 'GED Cabinet Kiaba',
  VERSION: '1.0.0',
  ENVIRONMENT: import.meta.env.VITE_APP_ENV || 'development',
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/',
  ENABLE_DEBUG: import.meta.env.VITE_ENABLE_DEBUG === 'true'
}

/**
 * Statuts des dossiers juridiques
 */
export const DOSSIER_STATUS = {
  OUVERT: {
    value: 'OUVERT',
    label: 'Ouvert / En cours',
    color: 'green',
    icon: 'mdi-folder-open'
  },
  ATTENTE: {
    value: 'ATTENTE',
    label: 'En attente de pièces ou décision',
    color: 'orange',
    icon: 'mdi-clock-alert'
  },
  SUSPENDU: {
    value: 'SUSPENDU',
    label: 'Suspendu',
    color: 'grey',
    icon: 'mdi-pause-circle'
  },
  CLOTURE: {
    value: 'CLOTURE',
    label: 'Clôturé',
    color: 'blue',
    icon: 'mdi-check-circle'
  },
  ARCHIVE: {
    value: 'ARCHIVE',
    label: 'Archivé',
    color: 'grey-darken-2',
    icon: 'mdi-archive'
  }
}

/**
 * Catégories de dossiers juridiques (droit gabonais)
 */
export const DOSSIER_CATEGORIES = {
  CONTENTIEUX: {
    value: 'CONTENTIEUX',
    label: 'Contentieux (civil, pénal, administratif)',
    icon: 'mdi-gavel'
  },
  CONSEIL: {
    value: 'CONSEIL',
    label: 'Conseil juridique / Avis',
    icon: 'mdi-lightbulb'
  },
  RECOUVREMENT: {
    value: 'RECOUVREMENT',
    label: 'Recouvrement de créances',
    icon: 'mdi-currency-usd'
  },
  TRAVAIL: {
    value: 'TRAVAIL',
    label: 'Droit du travail',
    icon: 'mdi-briefcase'
  },
  IMMOBILIER: {
    value: 'IMMOBILIER',
    label: 'Actes immobiliers / Foncier',
    icon: 'mdi-home'
  },
  SUCCESSION: {
    value: 'SUCCESSION',
    label: 'Succession / Partage',
    icon: 'mdi-family-tree'
  },
  MARIAGE: {
    value: 'MARIAGE',
    label: 'Contrat de mariage / Régime matrimonial',
    icon: 'mdi-ring'
  },
  DONATION: {
    value: 'DONATION',
    label: 'Donation / Libéralité',
    icon: 'mdi-gift'
  },
  SOCIETE: {
    value: 'SOCIETE',
    label: 'Constitution / Modification société OHADA',
    icon: 'mdi-domain'
  },
  FAMILLE: {
    value: 'FAMILLE',
    label: 'Divorce, garde, filiation',
    icon: 'mdi-account-multiple'
  },
  COMMERCIAL: {
    value: 'COMMERCIAL',
    label: 'Droit commercial OHADA',
    icon: 'mdi-handshake'
  },
  AUTRE: {
    value: 'AUTRE',
    label: 'Autre',
    icon: 'mdi-folder'
  }
}

/**
 * Types de clients
 */
export const CLIENT_TYPES = {
  PHYSIQUE: {
    value: 'PHYSIQUE',
    label: 'Personne Physique',
    icon: 'mdi-account'
  },
  MORALE: {
    value: 'MORALE',
    label: 'Personne Morale',
    icon: 'mdi-domain'
  }
}

/**
 * Types de pièces d'identité
 */
export const ID_TYPES = {
  CNI: {
    value: 'CNI',
    label: 'Carte Nationale d\'Identité'
  },
  PASSPORT: {
    value: 'PASSPORT',
    label: 'Passeport'
  }
}

/**
 * Niveaux de sensibilité des documents
 */
export const DOCUMENT_SENSITIVITY = {
  PUBLIC: {
    value: 'public',
    label: 'Public',
    color: 'green',
    icon: 'mdi-earth',
    description: 'Accessible à tous les collaborateurs'
  },
  INTERNAL: {
    value: 'internal',
    label: 'Usage Interne',
    color: 'blue',
    icon: 'mdi-office-building',
    description: 'Réservé au personnel du cabinet'
  },
  CONFIDENTIAL: {
    value: 'confidential',
    label: 'Confidentiel',
    color: 'orange',
    icon: 'mdi-lock',
    description: 'Accès restreint (avocat + secrétariat)'
  },
  SECRET: {
    value: 'secret',
    label: 'Secret Professionnel',
    color: 'red',
    icon: 'mdi-shield-lock',
    description: 'Strictement limité à l\'avocat responsable'
  }
}

/**
 * Rôles utilisateurs
 */
export const USER_ROLES = {
  ADMIN: {
    value: 'ADMIN',
    label: 'Administrateur système',
    icon: 'mdi-shield-crown',
    color: 'red'
  },
  AVOCAT: {
    value: 'AVOCAT',
    label: 'Avocat',
    icon: 'mdi-scale-balance',
    color: 'indigo'
  },
  NOTAIRE: {
    value: 'NOTAIRE',
    label: 'Notaire',
    icon: 'mdi-stamp',
    color: 'purple'
  },
  CONSEIL_JURIDIQUE: {
    value: 'CONSEIL_JURIDIQUE',
    label: 'Conseil juridique',
    icon: 'mdi-account-tie',
    color: 'blue'
  },
  STAGIAIRE: {
    value: 'STAGIAIRE',
    label: 'Stagiaire / Collaborateur',
    icon: 'mdi-school',
    color: 'teal'
  },
  SECRETAIRE: {
    value: 'SECRETAIRE',
    label: 'Secrétaire / Clerc',
    icon: 'mdi-desk',
    color: 'orange'
  },
  ASSISTANT: {
    value: 'ASSISTANT',
    label: 'Assistant juridique',
    icon: 'mdi-account-question',
    color: 'grey'
  }
}

/**
 * Types d'événements agenda
 */
export const EVENT_TYPES = {
  AUDIENCE: {
    value: 'AUDIENCE',
    label: 'Audience / Plaidoirie',
    icon: 'mdi-gavel',
    color: 'red'
  },
  RDV: {
    value: 'RDV',
    label: 'Rendez-vous client',
    icon: 'mdi-calendar-account',
    color: 'blue'
  },
  FORMALITE: {
    value: 'FORMALITE',
    label: 'Formalité notariale',
    icon: 'mdi-file-sign',
    color: 'purple'
  },
  CONGE: {
    value: 'CONGE',
    label: 'Congé / Absence',
    icon: 'mdi-beach',
    color: 'green'
  },
  AUTRE: {
    value: 'AUTRE',
    label: 'Autre événement',
    icon: 'mdi-calendar-blank',
    color: 'grey'
  }
}

/**
 * Configuration de pagination
 */
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: parseInt(import.meta.env.VITE_DEFAULT_PAGE_SIZE) || 25,
  PAGE_SIZE_OPTIONS: [10, 25, 50, 100],
  MAX_PAGE_SIZE: 100
}

/**
 * Configuration d'upload
 */
export const UPLOAD_CONFIG = {
  MAX_FILE_SIZE: parseInt(import.meta.env.VITE_MAX_FILE_SIZE) || 100 * 1024 * 1024, // 100 MB
  ALLOWED_FILE_TYPES: (import.meta.env.VITE_ALLOWED_FILE_TYPES || 'pdf,doc,docx,xls,xlsx,jpg,jpeg,png').split(','),
  CHUNK_SIZE: 5 * 1024 * 1024, // 5 MB chunks pour upload progressif
}

/**
 * Configuration des délais
 */
export const TIMEOUTS = {
  DEBOUNCE_SEARCH: 400, // ms
  TOAST_DURATION: 5000, // ms
  API_TIMEOUT: 30000, // ms
  IDLE_TIMEOUT: 30 * 60 * 1000 // 30 minutes
}

/**
 * Messages d'erreur standards
 */
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Impossible de contacter le serveur. Vérifiez votre connexion internet.',
  UNAUTHORIZED: 'Session expirée. Veuillez vous reconnecter.',
  FORBIDDEN: 'Vous n\'avez pas l\'autorisation d\'effectuer cette action.',
  NOT_FOUND: 'Ressource introuvable.',
  SERVER_ERROR: 'Erreur serveur. Veuillez réessayer plus tard.',
  VALIDATION_ERROR: 'Données invalides. Vérifiez les champs du formulaire.',
  FILE_TOO_LARGE: 'Fichier trop volumineux. Taille maximale: 100 MB.',
  INVALID_FILE_TYPE: 'Type de fichier non autorisé.'
}

/**
 * Messages de succès standards
 */
export const SUCCESS_MESSAGES = {
  CREATE: 'Élément créé avec succès',
  UPDATE: 'Modifications enregistrées',
  DELETE: 'Élément supprimé',
  UPLOAD: 'Document téléversé avec succès',
  DOWNLOAD: 'Téléchargement terminé'
}

/**
 * Expressions régulières de validation (Gabon)
 */
export const VALIDATION_PATTERNS = {
  NIF: /^\d{10}$/, // 10 chiffres exactement
  RCCM: /^[A-Z]{2,3}\/\d{4}\/[A-Z]\/\d{5}$/, // Format: GA-LBV-2024-A01-12345
  PHONE_GABON: /^(\+241|00241)?[0-9]{8}$/, // Téléphone gabonais
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, // Email basique
  PROFESSIONAL_ID: /^(BAR|NOT|CJ)\/GAB\/\d{4}\/\d{3}$/ // Carte professionnelle
}

/**
 * Formats de date
 */
export const DATE_FORMATS = {
  DISPLAY: 'DD/MM/YYYY',
  DISPLAY_WITH_TIME: 'DD/MM/YYYY HH:mm',
  API: 'YYYY-MM-DD',
  API_WITH_TIME: 'YYYY-MM-DDTHH:mm:ss',
  LONG: 'dddd D MMMM YYYY',
  SHORT: 'DD/MM/YY'
}

/**
 * Localisation française
 */
export const LOCALE = {
  LANG: 'fr-FR',
  CURRENCY: 'XAF', // Franc CFA
  CURRENCY_SYMBOL: 'FCFA',
  TIMEZONE: 'Africa/Libreville'
}

/**
 * Routes de navigation
 */
export const ROUTES = {
  LOGIN: '/login',
  DASHBOARD: '/',
  CLIENTS: '/clients',
  CLIENT_DETAIL: '/clients/:id',
  DOSSIERS: '/dossiers',
  DOSSIER_DETAIL: '/dossiers/:id',
  DOCUMENTS: '/documents',
  DOCUMENT_DETAIL: '/documents/:id',
  AGENDA: '/agenda',
  USERS: '/users'
}

/**
 * Clés de stockage local
 */
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
  THEME: 'theme',
  SIDEBAR_STATE: 'sidebar_collapsed'
}

/**
 * Helper pour obtenir toutes les options d'une constante
 * @param {Object} constantObject - Objet de constantes
 * @returns {Array} Tableau d'options pour v-select
 */
export function getOptionsFromConstant(constantObject) {
  return Object.values(constantObject).map(item => ({
    value: item.value,
    title: item.label || item.value,
    ...item
  }))
}

export default {
  APP_CONFIG,
  DOSSIER_STATUS,
  DOSSIER_CATEGORIES,
  CLIENT_TYPES,
  ID_TYPES,
  DOCUMENT_SENSITIVITY,
  USER_ROLES,
  EVENT_TYPES,
  PAGINATION,
  UPLOAD_CONFIG,
  TIMEOUTS,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  VALIDATION_PATTERNS,
  DATE_FORMATS,
  LOCALE,
  ROUTES,
  STORAGE_KEYS,
  getOptionsFromConstant
}
