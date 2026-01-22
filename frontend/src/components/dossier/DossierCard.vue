<script setup>
const props = defineProps({
  dossier: {
    type: Object,
    required: true
  }
})

const isOverdue = computed(() => {
  if (!props.dossier.critical_deadline) return false
  return new Date(props.dossier.critical_deadline) < new Date()
})

const getStatusColor = (status) => {
  const colors = {
    OUVERT: 'indigo',
    ATTENTE: 'orange',
    CLOTURE: 'green',
    ARCHIVE: 'grey-darken-2'
  }
  return colors[status] || 'blue-grey'
}
</script>

<template>
  <v-card
    elevation="6"
    class="pa-4 transition-swing"
    hover
    @click="$router.push(`/dossiers/${dossier.id}`)"
    style="cursor: pointer;"
  >
    <v-card-title class="d-flex align-center">
      <v-icon size="32" color="indigo-darken-4" class="mr-3">
        mdi-folder-multiple
      </v-icon>
      <div class="flex-grow-1">
        <div class="text-h6 font-weight-bold text-indigo-darken-4">
          {{ dossier.reference_code }}
        </div>
        <div class="text-body-1">{{ dossier.title }}</div>
      </div>
      <v-chip :color="getStatusColor(dossier.status)" small>
        {{ dossier.status }}
      </v-chip>
    </v-card-title>

    <v-card-text class="pt-4">
      <p class="mb-1">
        <strong>Client :</strong> {{ dossier.client_name || dossier.client?.display_name }}
      </p>
      <p class="mb-1">
        <strong>Responsable :</strong> {{ dossier.responsible_name || dossier.responsible?.full_name }}
      </p>
      <p class="mb-1">
        <strong>Catégorie :</strong> {{ dossier.category }}
      </p>
      <p class="mb-1">
        <strong>Ouverture :</strong> {{ new Date(dossier.opening_date).toLocaleDateString('fr-GA') }}
      </p>
      <p v-if="dossier.critical_deadline" class="mb-0">
        <strong>Délai critique :</strong>
        <span :class="{ 'red--text font-weight-bold': isOverdue }">
          {{ new Date(dossier.critical_deadline).toLocaleDateString('fr-GA') }}
        </span>
        <v-icon v-if="isOverdue" small color="red" class="ml-1">mdi-alert</v-icon>
      </p>
    </v-card-text>

    <v-card-actions class="justify-space-between">
      <v-chip small color="amber-lighten-4">
        {{ dossier.document_count || 0 }} document{{ dossier.document_count > 1 ? 's' : '' }}
      </v-chip>
      <v-btn icon small>
        <v-icon color="indigo">mdi-arrow-right</v-icon>
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped>
.transition-swing {
  transition: all 0.3s ease;
}
.transition-swing:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
}
</style>