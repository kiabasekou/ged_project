// ============================================================================
// Service : File Preview Service
// Description : Génération de prévisualisations pour différents types de fichiers
// Auteur : Maître Ahmed - GED Cabinet Kiaba
// ============================================================================

/**
 * Génère une prévisualisation base64 d'une image
 * 
 * @param {File} file - Fichier image
 * @returns {Promise<string>} Data URL base64
 * @throws {Error} Si le fichier n'est pas une image ou si la lecture échoue
 * 
 * @example
 * const preview = await generateImagePreview(imageFile)
 * // preview = "data:image/jpeg;base64,..."
 */
export async function generateImagePreview(file) {
  return new Promise((resolve, reject) => {
    if (!file.type.startsWith('image/')) {
      reject(new Error('Le fichier n\'est pas une image'))
      return
    }

    const reader = new FileReader()
    
    reader.onload = (e) => {
      resolve(e.target.result)
    }
    
    reader.onerror = () => {
      reject(new Error('Erreur lors de la lecture du fichier'))
    }
    
    reader.readAsDataURL(file)
  })
}

/**
 * Génère une miniature redimensionnée d'une image
 * 
 * @param {File} file - Fichier image
 * @param {number} maxWidth - Largeur maximale
 * @param {number} maxHeight - Hauteur maximale
 * @returns {Promise<string>} Data URL de la miniature
 */
export async function generateThumbnail(file, maxWidth = 200, maxHeight = 200) {
  return new Promise((resolve, reject) => {
    if (!file.type.startsWith('image/')) {
      reject(new Error('Le fichier n\'est pas une image'))
      return
    }

    const reader = new FileReader()
    
    reader.onload = (e) => {
      const img = new Image()
      
      img.onload = () => {
        // Calcul des dimensions
        let width = img.width
        let height = img.height
        
        if (width > height) {
          if (width > maxWidth) {
            height = height * (maxWidth / width)
            width = maxWidth
          }
        } else {
          if (height > maxHeight) {
            width = width * (maxHeight / height)
            height = maxHeight
          }
        }
        
        // Création du canvas
        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height
        
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)
        
        resolve(canvas.toDataURL(file.type))
      }
      
      img.onerror = () => {
        reject(new Error('Erreur lors du chargement de l\'image'))
      }
      
      img.src = e.target.result
    }
    
    reader.onerror = () => {
      reject(new Error('Erreur lors de la lecture du fichier'))
    }
    
    reader.readAsDataURL(file)
  })
}

/**
 * Extrait le texte d'un fichier texte
 * 
 * @param {File} file - Fichier texte
 * @param {number} maxChars - Nombre maximum de caractères à extraire
 * @returns {Promise<string>} Contenu textuel
 */
export async function extractTextPreview(file, maxChars = 1000) {
  return new Promise((resolve, reject) => {
    const allowedTypes = ['text/plain', 'text/html', 'text/csv']
    
    if (!allowedTypes.includes(file.type)) {
      reject(new Error('Le fichier n\'est pas un fichier texte supporté'))
      return
    }

    const reader = new FileReader()
    
    reader.onload = (e) => {
      let text = e.target.result
      
      if (text.length > maxChars) {
        text = text.substring(0, maxChars) + '...'
      }
      
      resolve(text)
    }
    
    reader.onerror = () => {
      reject(new Error('Erreur lors de la lecture du fichier'))
    }
    
    reader.readAsText(file)
  })
}

/**
 * Extrait les métadonnées EXIF d'une image (si disponibles)
 * Note: Nécessite une bibliothèque externe pour un support complet
 * Cette version basique extrait uniquement les données natives du navigateur
 * 
 * @param {File} file - Fichier image
 * @returns {Promise<Object>} Métadonnées
 */
export async function extractImageMetadata(file) {
  return new Promise((resolve, reject) => {
    if (!file.type.startsWith('image/')) {
      reject(new Error('Le fichier n\'est pas une image'))
      return
    }

    const reader = new FileReader()
    
    reader.onload = (e) => {
      const img = new Image()
      
      img.onload = () => {
        const metadata = {
          width: img.width,
          height: img.height,
          aspectRatio: (img.width / img.height).toFixed(2),
          fileSize: file.size,
          fileName: file.name,
          mimeType: file.type,
          lastModified: new Date(file.lastModified)
        }
        
        resolve(metadata)
      }
      
      img.onerror = () => {
        reject(new Error('Erreur lors du chargement de l\'image'))
      }
      
      img.src = e.target.result
    }
    
    reader.onerror = () => {
      reject(new Error('Erreur lors de la lecture du fichier'))
    }
    
    reader.readAsDataURL(file)
  })
}

/**
 * Vérifie si un fichier est une image
 * 
 * @param {File} file - Fichier à vérifier
 * @returns {boolean}
 */
export function isImage(file) {
  return file.type.startsWith('image/')
}

/**
 * Vérifie si un fichier est un document
 * 
 * @param {File} file - Fichier à vérifier
 * @returns {boolean}
 */
export function isDocument(file) {
  const documentTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain'
  ]
  
  return documentTypes.includes(file.type)
}

/**
 * Obtient l'icône appropriée pour un type de fichier
 * 
 * @param {string} extension - Extension du fichier (avec ou sans point)
 * @returns {string} Nom de l'icône Material Design Icons
 */
export function getFileIcon(extension) {
  // Nettoyer l'extension
  const ext = extension.toLowerCase().replace('.', '')
  
  const iconMap = {
    // Documents
    pdf: 'mdi-file-pdf-box',
    doc: 'mdi-file-word',
    docx: 'mdi-file-word',
    xls: 'mdi-file-excel',
    xlsx: 'mdi-file-excel',
    ppt: 'mdi-file-powerpoint',
    pptx: 'mdi-file-powerpoint',
    txt: 'mdi-file-document-outline',
    
    // Images
    jpg: 'mdi-file-image',
    jpeg: 'mdi-file-image',
    png: 'mdi-file-image',
    gif: 'mdi-file-image',
    svg: 'mdi-file-image',
    
    // Archives
    zip: 'mdi-folder-zip',
    rar: 'mdi-folder-zip',
    '7z': 'mdi-folder-zip',
    
    // Emails
    msg: 'mdi-email',
    eml: 'mdi-email',
    
    // Défaut
    default: 'mdi-file'
  }
  
  return iconMap[ext] || iconMap.default
}

/**
 * Obtient la couleur associée à un type de fichier
 * 
 * @param {string} extension - Extension du fichier
 * @returns {string} Classe de couleur Vuetify
 */
export function getFileColor(extension) {
  const ext = extension.toLowerCase().replace('.', '')
  
  const colorMap = {
    pdf: 'red',
    doc: 'blue',
    docx: 'blue',
    xls: 'green',
    xlsx: 'green',
    ppt: 'orange',
    pptx: 'orange',
    jpg: 'purple',
    jpeg: 'purple',
    png: 'purple',
    gif: 'purple',
    txt: 'grey',
    zip: 'brown',
    default: 'grey-darken-1'
  }
  
  return colorMap[ext] || colorMap.default
}

/**
 * Convertit un fichier en ArrayBuffer (utile pour le chiffrement)
 * 
 * @param {File} file - Fichier à convertir
 * @returns {Promise<ArrayBuffer>}
 */
export async function fileToArrayBuffer(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = (e) => {
      resolve(e.target.result)
    }
    
    reader.onerror = () => {
      reject(new Error('Erreur lors de la lecture du fichier'))
    }
    
    reader.readAsArrayBuffer(file)
  })
}

/**
 * Calcule le hash SHA-256 d'un fichier (côté client)
 * Note: Nécessite Web Crypto API (disponible en HTTPS uniquement)
 * 
 * @param {File} file - Fichier à hasher
 * @returns {Promise<string>} Hash en hexadécimal
 */
export async function calculateFileHash(file) {
  try {
    const arrayBuffer = await fileToArrayBuffer(file)
    const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer)
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
    
    return hashHex
  } catch (error) {
    console.error('Erreur calcul hash:', error)
    throw new Error('Impossible de calculer le hash du fichier')
  }
}

export default {
  generateImagePreview,
  generateThumbnail,
  extractTextPreview,
  extractImageMetadata,
  isImage,
  isDocument,
  getFileIcon,
  getFileColor,
  fileToArrayBuffer,
  calculateFileHash
}
