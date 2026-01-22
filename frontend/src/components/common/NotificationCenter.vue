<script setup>
import { computed } from 'vue'
import { useNotificationStore } from '@/stores/notification'
import { useRouter } from 'vue-router'
import { formatDate } from '@/utils/format'

const notificationStore = useNotificationStore()
const router = useRouter()

const daysOverdue = (deadline) => {
  const diff = Math.floor((new Date() - new Date(deadline)) / (1000 * 60 * 60 * 24))
  return diff
}

const goToDossier = (id) => {
  notificationStore.closeDrawer()
  router.push(`/dossiers/${id}`)
}
</script>

<template>
  <v-navigation-drawer
    v-model="notificationStore.drawer"
    location="right"
    temporary
    width="420"
    class="bg-grey-lighten-4"
  >
    <v-card elevation="0" class="fill-height d-flex flex-column">
      <v-card-title class="text-h6 bg-indigo-darken-4 text-white py-4 d-flex align-center">
        <v-icon left color="white">mdi-bell-alert</v-icon>
        Délais critiques
        <v-spacer />
        <v-chip color="amber" small>
          {{ notificationStore.count }} alerte{{ notificationStore.count > 1 ? 's' : '' }}
        </v-chip>
        <v-btn icon @click="notificationStore.closeDrawer" class="ml-4">
          <v-icon color="white">mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text class="flex-grow-1 overflow-y-auto pa-0">
        <template v-if="notificationStore.loading">
          <div class="text-center py-12">
            <v-progress-circular indeterminate color="indigo-darken-4" />
          </div>
        </template>

        <template v-else-if="notificationStore.count === 0">
          <div class="text-center py-12">
            <v-icon size="80" color="green">mdi-check-circle</v-icon>
            <p class="text-h6 mt-4 text-green-darken-2">Aucun délai dépassé</p>
            <p class="text-grey-darken-1">Tout est sous contrôle !</p>
          </div>
        </template>

        <template v-else>
          <v-list density="compact">
            <v-list-item
              v-for="d in notificationStore.overdueDossiers"
              :key="d.id"
              @click="goToDossier(d.id)"
              class="border-b"
              active-class="bg-red-lighten-5"
            >
              <template v-slot:prepend>
                <v-avatar color="red-darken-2" size="40">
                  <span class="text-white font-weight-bold">
                    {{ daysOverdue(d.critical_deadline) }}
                  </span>
                </v-avatar>
              </template>

              <v-list-item-title class="font-weight-medium">
                [{{ d.reference_code }}] {{ d.title }}
              </v-list-item-title>

              <v-list-item-subtitle>
                <div>Client : {{ d.client_name }}</div>
                <div class="text-red-darken-2">
                  Délai dépassé depuis {{ daysOverdue(d.critical_deadline) }} jour{{ daysOverdue(d.critical_deadline) > 1 ? 's' : '' }}
                  ({{ formatDate(d.critical_deadline) }})
                </div>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </template>
      </v-card-text>

      <v-card-actions class="pa-4 bg-white">
        <v-btn
          block
          color="indigo-darken-4"
          variant="flat"
          @click="notificationStore.fetchOverdueDossiers"
        >
          <v-icon left>mdi-refresh</v-icon>
          Actualiser
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-navigation-drawer>
</template>