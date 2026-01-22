<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const userFullName = computed(() => {
  return authStore.user?.full_name || authStore.user?.username || 'Utilisateur'
})

const userRole = computed(() => {
  return authStore.user?.role_display || ''
})

const logout = () => {
  authStore.logout()
  router.push('/login')
}

// Menu principal du cabinet — mise à jour avec Agenda & Délais
const menuItems = [
  { title: 'Tableau de bord', icon: 'mdi-view-dashboard', to: '/' },
  { title: 'Dossiers', icon: 'mdi-folder-multiple', to: '/dossiers' },
  {
    title: 'Agenda & Délais',
    icon: 'mdi-calendar-alert',
    to: '/agenda',
    badge: notificationStore.urgentCount,  // Badge dynamique avec nombre de délais critiques
    badgeColor: 'red-darken-2'
  },
  { title: 'Clients', icon: 'mdi-account-multiple', to: '/clients' },
  { title: 'Documents', icon: 'mdi-file-document-multiple', to: '/documents' },
  { title: 'Utilisateurs', icon: 'mdi-account-group', to: '/users', adminOnly: true },
]
</script>

<template>
  <v-navigation-drawer
    permanent
    clipped
    width="280"
    class="bg-indigo-darken-4"
  >
    <!-- Logo et nom du cabinet -->
    <div class="d-flex align-center pa-6">
      <v-img
        src="/src/assets/logo.png"
        max-width="60"
        max-height="60"
        class="mr-4"
      />
      <div>
        <h2 class="text-white font-weight-bold text-h6">Cabinet Kiaba</h2>
        <p class="text-amber-lighten-2 text-caption mb-0">Libreville • Gabon</p>
      </div>
    </div>

    <v-divider class="border-opacity-25 mx-4" color="amber" />

    <!-- Menu principal -->
    <v-list density="comfortable" nav>
      <v-list-item
        v-for="item in menuItems.filter(i => !i.adminOnly || authStore.isAdmin)"
        :key="item.title"
        :to="item.to"
        link
        class="mb-1"
        active-class="bg-amber text-indigo-darken-4"
        rounded="lg"
      >
        <template v-slot:prepend>
          <v-badge
            v-if="item.badge > 0"
            :content="item.badge"
            color="red-darken-2"
            floating
            offset-x="12"
            offset-y="12"
          >
            <v-icon :icon="item.icon" class="text-white mr-3" size="large" />
          </v-badge>
          <v-icon v-else :icon="item.icon" class="text-white mr-3" size="large" />
        </template>

        <v-list-item-title class="text-white font-weight-medium d-flex align-center">
          {{ item.title }}
          <v-chip
            v-if="item.badge > 0"
            size="x-small"
            color="red-darken-2"
            class="ml-3"
            label
          >
            {{ item.badge }} urgence{{ item.badge > 1 ? 's' : '' }}
          </v-chip>
        </v-list-item-title>
      </v-list-item>
    </v-list>

    <!-- Profil utilisateur en bas -->
    <template v-slot:append>
      <div class="pa-4">
        <v-divider class="mb-4 border-opacity-25" color="amber" />
        <div class="text-center text-white">
          <p class="text-caption mb-1">Connecté en tant que</p>
          <p class="font-weight-bold">{{ userFullName }}</p>
          <p class="text-amber-lighten-2 text-caption">{{ userRole }}</p>
          <v-btn
            variant="text"
            block
            class="mt-3"
            color="amber-lighten-2"
            @click="logout"
          >
            <v-icon left>mdi-logout</v-icon>
            Déconnexion
          </v-btn>
        </div>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<style scoped>
.bg-indigo-darken-4 {
  background-color: #1A237E !important;
}
</style>