// src/utils/format.js

/**
 * Utilitaires de formatage pour l'interface cabinet
 * Adapté au contexte gabonais (dates, numéros, etc.)
 */

/**
 * Formate une date au format gabonais/français : 20/01/2026
 */
export const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-GA', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

/**
 * Formate une date avec heure : 20/01/2026 15:45
 */
export const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateTimeString('fr-GA', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Formate la taille d'un fichier (octets → Ko, Mo, Go)
 */
export const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 octet'
  const sizes = ['octets', 'Ko', 'Mo', 'Go', 'To']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  const value = parseFloat((bytes / Math.pow(1024, i)).toFixed(2))
  return `${value} ${sizes[i]}`
}

/**
 * Formate un numéro de téléphone gabonais (ex: +241 01 23 45 67)
 */
export const formatPhone = (phone) => {
  if (!phone) return '-'
  // Supprime tous les caractères non numériques sauf +
  const cleaned = phone.replace(/[^\d+]/g, '')
  if (cleaned.startsWith('241')) {
    return `+241 ${cleaned.slice(3, 5)} ${cleaned.slice(5, 7)} ${cleaned.slice(7, 9)} ${cleaned.slice(9)}`
  }
  return phone
}

/**
 * Formate un nom complet (Prénom NOM ou NOM Prénom selon préférence)
 */
export const formatFullName = (firstName, lastName) => {
  if (!firstName && !lastName) return 'Non renseigné'
  return `${firstName || ''} ${lastName || ''}`.trim()
}

/**
 * Capitalise la première lettre d'une chaîne
 */
export const capitalize = (str) => {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

/**
 * Formate une référence dossier (ex: GAB-2026-0001 → en gras et couleur)
 * À utiliser dans des templates Vue
 */
export const highlightReference = (ref) => {
  return `<strong class="text-indigo-darken-3">${ref}</strong>`
}

export default {
  formatDate,
  formatDateTime,
  formatFileSize,
  formatPhone,
  formatFullName,
  capitalize,
  highlightReference
}