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
      {
        path: '', 
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue')
      },
      {
        path: 'dossiers',
        name: 'DossierList',
        component: () => import('@/views/Dossier/DossierListView.vue')
      },
      // CORRECTION : Retrait du slash initial pour cohérence
      {
        path: 'agenda',
        name: 'Agenda',
        component: () => import('@/views/AgendaView.vue')
      },
      // CORRECTION : On s'assure que :id respecte un format UUID pour ne pas matcher "create"
      {
        path: 'dossiers/:id',
        name: 'DossierDetail',
        component: () => import('@/views/Dossier/DossierDetailView.vue'),
        props: true
      },
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

// Garde de navigation renforcée
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 1% Best Practice : Attendre que le store soit initialisé (si vous avez une méthode init)
  // ou vérifier manuellement le token si le store est vide
  if (!authStore.user && localStorage.getItem('token')) {
    // Optionnel : await authStore.fetchCurrentUser()
  }

  const isAuthenticated = authStore.isAuthenticated
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } }) // On garde en mémoire où l'utilisateur voulait aller
  } else if (to.name === 'Login' && isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router