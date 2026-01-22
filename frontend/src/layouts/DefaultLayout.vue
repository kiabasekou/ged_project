<script setup>
import Sidebar from '@/components/layout/Sidebar.vue'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
</script>

<template>
  <v-app>
    <Sidebar />

    <v-main class="bg-grey-lighten-4">
      <Header />

      <v-container fluid class="pa-6">
        <router-view />
      </v-container>

      <Footer />
    </v-main>
  </v-app>
</template>

<style scoped>
.v-main {
  min-height: 100vh;
}
</style>