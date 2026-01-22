<script setup>
import { ref } from 'vue'
import GlobalSearch from '@/components/common/GlobalSearch.vue'
import NotificationBadge from '@/components/common/NotificationBadge.vue'
import NotificationCenter from '@/components/common/NotificationCenter.vue'

const drawer = ref(true) // Contrôle la sidebar sur mobile

const toggleDrawer = () => {
  drawer.value = !drawer.value
}
</script>

<template>
  <v-app-bar
    color="white"
    elevation="2"
    height="70"
  >
    <!-- Bouton menu mobile -->
    <v-app-bar-nav-icon
      @click.stop="toggleDrawer"
      class="d-md-none"
    />

    <v-spacer />

    <!-- Barre de recherche globale -->
    <GlobalSearch class="mx-4" />

    <!-- Badge notifications -->
    <NotificationBadge class="mr-4" />

    <!-- Bouton aide -->
    <v-btn icon variant="text" title="Aide">
      <v-icon color="indigo-darken-4">mdi-help-circle-outline</v-icon>
    </v-btn>
  </v-app-bar>

  <!-- Centre de notifications -->
  <NotificationCenter />
</template>