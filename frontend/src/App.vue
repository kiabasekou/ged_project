<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

onMounted(async () => {
  if (authStore.isAuthenticated) {
    try {
      await authStore.fetchMe()
      await notificationStore.fetchOverdueDossiers()
    } catch (err) {
      authStore.logout()
      router.push('/login')
    }
  }
})
</script>

<template>
  <!-- wrapper principal -->
  <v-app>
    <!-- zone où s’affichent les pages du router -->
    <router-view />
  </v-app>
</template>