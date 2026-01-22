<script setup>
import { computed } from 'vue'
import { useNotificationStore } from '@/stores/notification'

const notificationStore = useNotificationStore()

const badgeContent = computed(() => {
  return notificationStore.count > 99 ? '99+' : notificationStore.count
})
</script>

<template>
  <v-badge
    :content="badgeContent"
    color="red-darken-2"
    dot
    floating
    offset-x="10"
    offset-y="10"
    :model-value="notificationStore.hasOverdue"
  >
    <v-btn
      icon
      variant="text"
      @click="notificationStore.toggleDrawer"
      title="Notifications délais critiques"
    >
      <v-icon color="indigo-darken-4" size="28">
        mdi-bell-outline
      </v-icon>
    </v-btn>
  </v-badge>
</template>