/**
 * Validateurs stricts pour upload de documents - Frontend Vue.js
 * Réplique la logique de validation du backend côté client
 */

export const ALLOWED_EXTENSIONS = [
  '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt',
  '.txt', '.rtf', '.odt', '.ods', '.odp',
  '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
  '.zip', '.rar', '.7z', '.msg', '.eml'
]

export const ALLOWED_MIME_TYPES = {
  '.pdf': 'application/pdf',
  '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  '.doc': 'application/msword',
  '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  '.xls': 'application/vnd.ms-excel',
  '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  '.txt': 'text/plain',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.gif': 'image/gif',
  '.zip': 'application/zip'
}

export const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100 MB

/**
 * Valide un fichier avant upload
 * @param {File} file - Fichier à valider
 * @returns {Object} { valid: boolean, error: string|null }
 */
export function validateFile(file) {
  // 1. Vérifier que c'est bien un objet File
  if (!(file instanceof File)) {
    return { valid: false, error: "Objet fichier invalide" }
  }

  // 2. Vérifier la taille
  if (file.size > MAX_FILE_SIZE) {
    const maxSizeMB = Math.round(MAX_FILE_SIZE / (1024 * 1024))
    return { 
      valid: false, 
      error: `Fichier trop volumineux. Maximum autorisé: ${maxSizeMB} MB` 
    }
  }

  if (file.size === 0) {
    return { valid: false, error: "Le fichier est vide" }
  }

  // 3. Extraire et vérifier l'extension
  const extension = getFileExtension(file.name)
  
  if (!ALLOWED_EXTENSIONS.includes(extension)) {
    return { 
      valid: false, 
      error: `Extension '${extension}' non autorisée. Extensions acceptées: ${ALLOWED_EXTENSIONS.join(', ')}` 
    }
  }

  // 4. Vérifier le type MIME
  const expectedMimeType = ALLOWED_MIME_TYPES[extension]
  
  if (expectedMimeType && file.type !== expectedMimeType) {
    // Tolérance pour certains navigateurs qui détectent mal les MIME types
    const tolerantExtensions = ['.docx', '.xlsx', '.pptx']
    
    if (!tolerantExtensions.includes(extension)) {
      return { 
        valid: false, 
        error: `Type MIME incohérent. Extension ${extension} attendue: ${expectedMimeType}, reçu: ${file.type}` 
      }
    }
  }

  return { valid: true, error: null }
}

/**
 * Valide plusieurs fichiers
 * @param {FileList|Array<File>} files - Liste de fichiers
 * @returns {Object} { valid: boolean, errors: Array<string> }
 */
export function validateFiles(files) {
  const errors = []
  
  Array.from(files).forEach((file, index) => {
    const result = validateFile(file)
    if (!result.valid) {
      errors.push(`Fichier ${index + 1} (${file.name}): ${result.error}`)
    }
  })

  return {
    valid: errors.length === 0,
    errors
  }
}

/**
 * Extrait l'extension d'un nom de fichier
 * @param {string} filename - Nom du fichier
 * @returns {string} Extension en minuscules (ex: '.pdf')
 */
export function getFileExtension(filename) {
  const lastDotIndex = filename.lastIndexOf('.')
  if (lastDotIndex === -1) return ''
  return filename.substring(lastDotIndex).toLowerCase()
}

/**
 * Formate la taille d'un fichier en format lisible
 * @param {number} bytes - Taille en octets
 * @returns {string} Taille formatée (ex: "2.5 MB")
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 o'
  
  const units = ['o', 'Ko', 'Mo', 'Go', 'To']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

/**
 * Génère un aperçu visuel d'un fichier image
 * @param {File} file - Fichier image
 * @returns {Promise<string>} Data URL de l'image
 */
export function generateImagePreview(file) {
  return new Promise((resolve, reject) => {
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    const extension = getFileExtension(file.name)
    
    if (!imageExtensions.includes(extension)) {
      reject(new Error("Le fichier n'est pas une image"))
      return
    }
    
    const reader = new FileReader()
    
    reader.onload = (e) => {
      resolve(e.target.result)
    }
    
    reader.onerror = () => {
      reject(new Error("Erreur de lecture du fichier"))
    }
    
    reader.readAsDataURL(file)
  })
}

/**
 * Vérifie les magic bytes d'un fichier (détection basique)
 * @param {File} file - Fichier à vérifier
 * @returns {Promise<boolean>} True si les magic bytes correspondent
 */
export async function verifyMagicBytes(file) {
  const extension = getFileExtension(file.name)
  
  // Signatures de fichiers (magic bytes)
  const signatures = {
    '.pdf': [0x25, 0x50, 0x44, 0x46], // %PDF
    '.zip': [0x50, 0x4B, 0x03, 0x04], // PK (utilisé par docx, xlsx, pptx)
    '.jpg': [0xFF, 0xD8, 0xFF],
    '.png': [0x89, 0x50, 0x4E, 0x47],
    '.gif': [0x47, 0x49, 0x46, 0x38]
  }
  
  // Extensions basées sur ZIP
  const zipBasedExtensions = ['.docx', '.xlsx', '.pptx', '.odt', '.ods']
  
  let expectedSignature
  
  if (zipBasedExtensions.includes(extension)) {
    expectedSignature = signatures['.zip']
  } else {
    expectedSignature = signatures[extension]
  }
  
  // Si pas de signature définie, on accepte
  if (!expectedSignature) {
    return true
  }
  
  try {
    const arrayBuffer = await file.slice(0, expectedSignature.length).arrayBuffer()
    const bytes = new Uint8Array(arrayBuffer)
    
    return expectedSignature.every((byte, index) => bytes[index] === byte)
  } catch (error) {
    console.error('Erreur vérification magic bytes:', error)
    return false
  }
}

/**
 * Classe de validation complète avec vérifications asynchrones
 */
export class FileValidator {
  constructor(file) {
    this.file = file
    this.errors = []
  }

  /**
   * Lance toutes les validations
   * @returns {Promise<Object>} { valid: boolean, errors: Array<string> }
   */
  async validate() {
    this.errors = []

    // Validation basique synchrone
    const basicValidation = validateFile(this.file)
    if (!basicValidation.valid) {
      this.errors.push(basicValidation.error)
      return { valid: false, errors: this.errors }
    }

    // Validation des magic bytes (asynchrone)
    const magicBytesValid = await verifyMagicBytes(this.file)
    if (!magicBytesValid) {
      this.errors.push(
        `Le fichier ne semble pas être un ${getFileExtension(this.file.name)} valide`
      )
    }

    return {
      valid: this.errors.length === 0,
      errors: this.errors
    }
  }

  /**
   * Récupère les informations du fichier
   * @returns {Object} Métadonnées du fichier
   */
  getFileInfo() {
    return {
      name: this.file.name,
      size: this.file.size,
      sizeFormatted: formatFileSize(this.file.size),
      type: this.file.type,
      extension: getFileExtension(this.file.name),
      lastModified: new Date(this.file.lastModified)
    }
  }
}

/**
 * Hook Vue 3 Composition API pour validation de fichiers
 * @returns {Object} Méthodes et état de validation
 */
export function useFileValidation() {
  const { ref, reactive } = require('vue')
  
  const validationState = reactive({
    isValidating: false,
    errors: [],
    validFiles: []
  })

  const validateSingleFile = async (file) => {
    validationState.isValidating = true
    validationState.errors = []
    
    try {
      const validator = new FileValidator(file)
      const result = await validator.validate()
      
      if (!result.valid) {
        validationState.errors = result.errors
        return false
      }
      
      validationState.validFiles = [file]
      return true
    } finally {
      validationState.isValidating = false
    }
  }

  const validateMultipleFiles = async (files) => {
    validationState.isValidating = true
    validationState.errors = []
    validationState.validFiles = []
    
    try {
      const results = await Promise.all(
        Array.from(files).map(async (file) => {
          const validator = new FileValidator(file)
          const result = await validator.validate()
          return { file, ...result }
        })
      )
      
      const invalidResults = results.filter(r => !r.valid)
      
      if (invalidResults.length > 0) {
        validationState.errors = invalidResults.flatMap(r => r.errors)
        return false
      }
      
      validationState.validFiles = results.map(r => r.file)
      return true
    } finally {
      validationState.isValidating = false
    }
  }

  return {
    validationState,
    validateSingleFile,
    validateMultipleFiles
  }
}

export default {
  validateFile,
  validateFiles,
  getFileExtension,
  formatFileSize,
  generateImagePreview,
  verifyMagicBytes,
  FileValidator,
  useFileValidation,
  ALLOWED_EXTENSIONS,
  ALLOWED_MIME_TYPES,
  MAX_FILE_SIZE
}
