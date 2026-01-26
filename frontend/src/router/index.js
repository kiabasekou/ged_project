// frontend/src/router/index.js - VERSION COMPLÈTE AVEC NOUVELLES ROUTES

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Auth/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      // Dashboard
      {
        path: '', 
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue')
      },
      
      // Dossiers
      {
        path: 'dossiers',
        name: 'DossierList',
        component: () => import('@/views/Dossier/DossierListView.vue')
      },
      {
        path: 'dossiers/:id',
        name: 'DossierDetail',
        component: () => import('@/views/Dossier/DossierDetailView.vue'),
        props: true
      },
      
      // Clients
      {
        path: 'clients',
        name: 'ClientList',
        component: () => import('@/views/Client/ClientListView.vue')
      },
      {
        path: 'clients/create',
        name: 'ClientCreate',
        component: () => import('@/views/Client/ClientCreateView.vue')
      },
      {
        path: 'clients/:id',
        name: 'ClientDetail',
        component: () => import('@/views/Client/ClientDetailView.vue'),
        props: true
      },
      
      // Documents - NOUVEAU
      {
        path: 'documents/upload',
        name: 'DocumentUpload',
        component: () => import('@/views/Document/DocumentUploadView.vue'),
        meta: { 
          title: 'Ajouter un document',
          requiresAuth: true 
        }
      },
      
      // Agenda
      {
        path: 'agenda',
        name: 'Agenda',
        component: () => import('@/views/AgendaView.vue')
      },
      // Événements - NOUVEAU
      {
        path: 'agenda/create',
        name: 'EventCreate',
        component: () => import('@/views/Agenda/EventCreateView.vue'),
        meta: { 
          title: 'Nouvel événement',
          requiresAuth: true 
        }
      },
      {
        path: 'documents',
        name: 'DocumentList',
        component: () => import('@/views/Document/DocumentListView.vue'),
        meta: { 
          title: 'Documents',
          requiresAuth: true 
        }
      },
      {
        path: 'documents/:id',
        name: 'DocumentDetail',
        component: () => import('@/views/Document/DocumentDetailView.vue'),
        props: true,
        meta: { 
          title: 'Détail du document',
          requiresAuth: true 
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: { name: 'Dashboard' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Garde de navigation
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Vérifier si token existe mais user pas encore chargé
  if (!authStore.user && localStorage.getItem('token')) {
    try {
      await authStore.fetchCurrentUser()
    } catch (error) {
      console.error('Erreur chargement utilisateur:', error)
    }
  }

  const isAuthenticated = authStore.isAuthenticated
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)

  if (requiresAuth && !isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router