// ============================================================================
// Utilitaires : Validation de fichiers (Fonctions pures)
// Description : Validateurs côté client pour upload de documents juridiques
// Auteur : Maître Ahmed - GED Cabinet Kiaba
// ============================================================================

// ============================================================================
// CONSTANTES DE CONFIGURATION
// ============================================================================

/**
 * Extensions de fichiers autorisées
 * Conformes aux standards du cabinet juridique gabonais
 */
export const ALLOWED_EXTENSIONS = [
  '.pdf',   // Documents Adobe
  '.docx',  // Microsoft Word (moderne)
  '.doc',   // Microsoft Word (legacy)
  '.xlsx',  // Microsoft Excel (moderne)
  '.xls',   // Microsoft Excel (legacy)
  '.pptx',  // Microsoft PowerPoint
  '.ppt',   // PowerPoint (legacy)
  '.txt',   // Texte brut
  '.rtf',   // Rich Text Format
  '.odt',   // OpenDocument Text
  '.ods',   // OpenDocument Spreadsheet
  '.odp',   // OpenDocument Presentation
  '.jpg',   // Image JPEG
  '.jpeg',  // Image JPEG
  '.png',   // Image PNG
  '.gif',   // Image GIF
  '.bmp',   // Image Bitmap
  '.tiff',  // Image TIFF
  '.zip',   // Archive ZIP
  '.rar',   // Archive RAR
  '.7z',    // Archive 7-Zip
  '.msg',   // Email Outlook
  '.eml'    // Email standard
]

/**
 * Types MIME autorisés avec leurs extensions correspondantes
 */
export const ALLOWED_MIME_TYPES = {
  '.pdf': 'application/pdf',
  '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  '.doc': 'application/msword',
  '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  '.xls': 'application/vnd.ms-excel',
  '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  '.ppt': 'application/vnd.ms-powerpoint',
  '.txt': 'text/plain',
  '.rtf': 'application/rtf',
  '.odt': 'application/vnd.oasis.opendocument.text',
  '.ods': 'application/vnd.oasis.opendocument.spreadsheet',
  '.odp': 'application/vnd.oasis.opendocument.presentation',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.gif': 'image/gif',
  '.bmp': 'image/bmp',
  '.tiff': 'image/tiff',
  '.zip': 'application/zip',
  '.rar': 'application/x-rar-compressed',
  '.7z': 'application/x-7z-compressed',
  '.msg': 'application/vnd.ms-outlook',
  '.eml': 'message/rfc822'
}

/**
 * Taille maximale de fichier (100 MB)
 * Conforme aux limitations serveur Django
 */
export const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100 MB

/**
 * Taille recommandée maximale pour upload rapide (10 MB)
 */
export const RECOMMENDED_MAX_SIZE = 10 * 1024 * 1024 // 10 MB

// ============================================================================
// FONCTIONS DE VALIDATION PURES
// ============================================================================

/**
 * Extrait l'extension d'un nom de fichier
 * 
 * @param {string} filename - Nom du fichier
 * @returns {string} Extension en minuscules avec le point (ex: '.pdf')
 * 
 * @example
 * getFileExtension('contrat.PDF') // '.pdf'
 * getFileExtension('mémoire.defense.docx') // '.docx'
 */
export function getFileExtension(filename) {
  if (!filename || typeof filename !== 'string') {
    return ''
  }
  
  const lastDotIndex = filename.lastIndexOf('.')
  
  if (lastDotIndex === -1 || lastDotIndex === 0) {
    return '' // Pas d'extension ou fichier caché Unix
  }
  
  return filename.substring(lastDotIndex).toLowerCase()
}

/**
 * Valide la taille d'un fichier
 * 
 * @param {File} file - Fichier à valider
 * @param {number} maxSize - Taille maximale en octets
 * @returns {Object} { valid: boolean, error: string|null }
 */
export function validateFileSize(file, maxSize = MAX_FILE_SIZE) {
  if (!file || !(file instanceof File)) {
    return { valid: false, error: "Objet fichier invalide" }
  }

  if (file.size === 0) {
    return { valid: false, error: "Le fichier est vide (0 octet)" }
  }

  if (file.size > maxSize) {
    const maxSizeMB = Math.round(maxSize / (1024 * 1024))
    const actualSizeMB = (file.size / (1024 * 1024)).toFixed(2)
    
    return { 
      valid: false, 
      error: `Fichier trop volumineux (${actualSizeMB} MB). Maximum autorisé: ${maxSizeMB} MB` 
    }
  }

  return { valid: true, error: null }
}

/**
 * Valide l'extension d'un fichier
 * 
 * @param {File} file - Fichier à valider
 * @param {Array<string>} allowedExtensions - Extensions autorisées
 * @returns {Object} { valid: boolean, error: string|null, extension: string }
 */
export function validateExtension(file, allowedExtensions = ALLOWED_EXTENSIONS) {
  if (!file || !(file instanceof File)) {
    return { valid: false, error: "Objet fichier invalide", extension: '' }
  }

  const extension = getFileExtension(file.name)
  
  if (!extension) {
    return { 
      valid: false, 
      error: "Le fichier n'a pas d'extension", 
      extension: '' 
    }
  }

  if (!allowedExtensions.includes(extension)) {
    return { 
      valid: false, 
      error: `Extension '${extension}' non autorisée. Extensions acceptées: ${allowedExtensions.join(', ')}`,
      extension 
    }
  }

  return { valid: true, error: null, extension }
}

/**
 * Valide le type MIME d'un fichier
 * 
 * @param {File} file - Fichier à valider
 * @returns {Object} { valid: boolean, error: string|null, warning: string|null }
 */
export function validateMimeType(file) {
  if (!file || !(file instanceof File)) {
    return { valid: false, error: "Objet fichier invalide", warning: null }
  }

  const extension = getFileExtension(file.name)
  const expectedMimeType = ALLOWED_MIME_TYPES[extension]
  
  // Si pas de MIME type attendu, on accepte (extension déjà validée avant)
  if (!expectedMimeType) {
    return { valid: true, error: null, warning: null }
  }

  // Certains navigateurs détectent mal les MIME types des fichiers Office
  const tolerantExtensions = ['.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt']
  
  if (file.type !== expectedMimeType) {
    if (tolerantExtensions.includes(extension)) {
      // Tolérance pour Office : on accepte mais on avertit
      return { 
        valid: true, 
        error: null,
        warning: `Type MIME incohérent mais accepté (extension Office): attendu ${expectedMimeType}, reçu ${file.type}` 
      }
    } else {
      return { 
        valid: false, 
        error: `Type MIME incohérent. Extension ${extension} attendue: ${expectedMimeType}, reçu: ${file.type || 'vide'}`,
        warning: null
      }
    }
  }

  return { valid: true, error: null, warning: null }
}

/**
 * Valide le nom du fichier (caractères spéciaux interdits)
 * 
 * @param {File} file - Fichier à valider
 * @returns {Object} { valid: boolean, error: string|null }
 */
export function validateFileName(file) {
  if (!file || !(file instanceof File)) {
    return { valid: false, error: "Objet fichier invalide" }
  }

  // Caractères interdits dans les noms de fichiers (Windows + Linux + sécurité)
  const invalidChars = /[<>:"/\\|?*\x00-\x1F]/g
  const fileName = file.name
  
  if (invalidChars.test(fileName)) {
    const foundChars = fileName.match(invalidChars)
    return { 
      valid: false, 
      error: `Le nom du fichier contient des caractères invalides: ${foundChars.join(', ')}` 
    }
  }

  // Vérifier la longueur du nom
  if (fileName.length > 255) {
    return { 
      valid: false, 
      error: "Le nom du fichier est trop long (maximum 255 caractères)" 
    }
  }

  // Vérifier les noms réservés Windows
  const reservedNames = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1', 'LPT2']
  const baseNameUpper = fileName.split('.')[0].toUpperCase()
  
  if (reservedNames.includes(baseNameUpper)) {
    return { 
      valid: false, 
      error: `Le nom "${baseNameUpper}" est réservé par le système` 
    }
  }

  return { valid: true, error: null }
}

/**
 * Validation complète d'un fichier (fonction principale)
 * 
 * @param {File} file - Fichier à valider
 * @returns {Object} { valid: boolean, error: string|null, warnings: Array<string> }
 * 
 * @example
 * const result = validateFile(file)
 * if (!result.valid) {
 *   console.error(result.error)
 * }
 * if (result.warnings.length > 0) {
 *   console.warn(result.warnings)
 * }
 */
export function validateFile(file) {
  const warnings = []
  
  // 1. Vérifier que c'est bien un objet File
  if (!file || !(file instanceof File)) {
    return { valid: false, error: "Objet fichier invalide", warnings }
  }

  // 2. Valider la taille
  const sizeResult = validateFileSize(file)
  if (!sizeResult.valid) {
    return { valid: false, error: sizeResult.error, warnings }
  }
  
  // Avertissement si fichier volumineux
  if (file.size > RECOMMENDED_MAX_SIZE) {
    warnings.push('Fichier volumineux : le téléversement peut prendre du temps')
  }

  // 3. Valider l'extension
  const extensionResult = validateExtension(file)
  if (!extensionResult.valid) {
    return { valid: false, error: extensionResult.error, warnings }
  }

  // 4. Valider le type MIME
  const mimeResult = validateMimeType(file)
  if (!mimeResult.valid) {
    return { valid: false, error: mimeResult.error, warnings }
  }
  if (mimeResult.warning) {
    warnings.push(mimeResult.warning)
  }

  // 5. Valider le nom du fichier
  const nameResult = validateFileName(file)
  if (!nameResult.valid) {
    return { valid: false, error: nameResult.error, warnings }
  }

  return { valid: true, error: null, warnings }
}

/**
 * Valide plusieurs fichiers
 * 
 * @param {FileList|Array<File>} files - Liste de fichiers
 * @returns {Object} { valid: boolean, errors: Array<string>, warnings: Array<string> }
 */
export function validateFiles(files) {
  const errors = []
  const warnings = []
  
  Array.from(files).forEach((file, index) => {
    const result = validateFile(file)
    
    if (!result.valid) {
      errors.push(`Fichier ${index + 1} (${file.name}): ${result.error}`)
    }
    
    if (result.warnings && result.warnings.length > 0) {
      result.warnings.forEach(warning => {
        warnings.push(`Fichier ${index + 1} (${file.name}): ${warning}`)
      })
    }
  })

  return {
    valid: errors.length === 0,
    errors,
    warnings
  }
}

/**
 * Formate une taille de fichier en unités lisibles
 * 
 * @param {number} bytes - Taille en octets
 * @param {number} decimals - Nombre de décimales
 * @returns {string} Taille formatée (ex: "1.5 MB")
 */
export function formatFileSize(bytes, decimals = 2) {
  if (bytes === 0) return '0 octet'
  
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['octets', 'Ko', 'Mo', 'Go', 'To']
  
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

/**
 * Vérifie si un fichier dépasse la taille recommandée
 * 
 * @param {File} file - Fichier à vérifier
 * @returns {boolean}
 */
export function isLargeFile(file) {
  return file.size > RECOMMENDED_MAX_SIZE
}

/**
 * Obtient une description lisible d'une extension
 * 
 * @param {string} extension - Extension (avec ou sans point)
 * @returns {string} Description
 */
export function getExtensionDescription(extension) {
  const ext = extension.toLowerCase().replace('.', '')
  
  const descriptions = {
    pdf: 'Document PDF',
    doc: 'Document Word (ancien format)',
    docx: 'Document Word',
    xls: 'Tableur Excel (ancien format)',
    xlsx: 'Tableur Excel',
    ppt: 'Présentation PowerPoint (ancien format)',
    pptx: 'Présentation PowerPoint',
    txt: 'Fichier texte',
    rtf: 'Document RTF',
    odt: 'Document OpenDocument',
    ods: 'Tableur OpenDocument',
    jpg: 'Image JPEG',
    jpeg: 'Image JPEG',
    png: 'Image PNG',
    gif: 'Image GIF',
    zip: 'Archive ZIP',
    rar: 'Archive RAR'
  }
  
  return descriptions[ext] || `Fichier ${extension}`
}

// Export par défaut de toutes les fonctions
export default {
  // Constantes
  ALLOWED_EXTENSIONS,
  ALLOWED_MIME_TYPES,
  MAX_FILE_SIZE,
  RECOMMENDED_MAX_SIZE,
  
  // Fonctions de validation
  validateFile,
  validateFiles,
  validateFileSize,
  validateExtension,
  validateMimeType,
  validateFileName,
  
  // Utilitaires
  getFileExtension,
  formatFileSize,
  isLargeFile,
  getExtensionDescription
}
