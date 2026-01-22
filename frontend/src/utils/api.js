// src/utils/api.js

import axios from '@/plugins/axios'

const API = {
  // Auth
  auth: {
    me: () => axios.get('/users/me/'),
    login: (credentials) => axios.post('/auth/login/', credentials), // À créer côté Django
    logout: () => axios.post('/auth/logout/')
  },

  // Users
  users: {
    list: (params) => axios.get('/users/', { params }),
    detail: (id) => axios.get(`/users/${id}/`),
    updateProfile: (data) => axios.patch('/users/update-profile/', data),
    acceptPrivacy: (id) => axios.post(`/users/${id}/accept-privacy/`)
  },

  // Clients
  clients: {
    list: (params) => axios.get('/clients/', { params }),
    detail: (id) => axios.get(`/clients/${id}/`),
    create: (data) => axios.post('/clients/', data),
    update: (id, data) => axios.patch(`/clients/${id}/`, data),
    stats: () => axios.get('/clients/stats/'),
    grantConsent: (id) => axios.post(`/clients/${id}/grant-consent/`)
  },

  // Dossiers
  dossiers: {
    list: (params) => axios.get('/dossiers/', { params }),
    detail: (id) => axios.get(`/dossiers/${id}/`),
    create: (data) => axios.post('/dossiers/', data),
    update: (id, data) => axios.patch(`/dossiers/${id}/`, data),
    cloturer: (id) => axios.post(`/dossiers/${id}/cloturer/`),
    archiver: (id) => axios.post(`/dossiers/${id}/archiver/`),
    stats: () => axios.get('/dossiers/stats/'),
    folders: (id) => axios.get(`/dossiers/${id}/folders/`)
  },

  // Documents
  documents: {
    list: (params) => axios.get('/documents/', { params }),
    detail: (id) => axios.get(`/documents/${id}/`),
    upload: (formData, onProgress) => axios.post('/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
    }),
    download: (id) => `${import.meta.env.VITE_API_BASE_URL}/documents/${id}/download/`,
    newVersion: (id, formData) => axios.post(`/documents/${id}/nouvelle-version/`, formData),
    versions: (id) => axios.get(`/documents/${id}/versions/`)
  },

  // Folders (arborescence)
  folders: {
    list: (params) => axios.get('/documents/folders/', { params })
  }
}

export default API