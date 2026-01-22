<script setup>
const props = defineProps({
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'info', 'warning', 'error'].includes(value)
  },
  title: {
    type: String,
    default: ''
  },
  dense: {
    type: Boolean,
    default: false
  },
  dismissible: {
    type: Boolean,
    default: false
  }
})

const model = defineModel({ default: true })

const icons = {
  success: 'mdi-check-circle',
  info: 'mdi-information',
  warning: 'mdi-alert',
  error: 'mdi-alert-circle'
}

const colors = {
  success: 'green',
  info: 'indigo',
  warning: 'amber-darken-2',
  error: 'red'
}
</script>

<template>
  <v-alert
    v-model="model"
    :type="type"
    :title="title"
    :density="dense ? 'compact' : 'default'"
    :color="colors[type]"
    variant="tonal"
    border="start"
    :closable="dismissible"
    class="mb-4"
  >
    <template v-slot:prepend>
      <v-icon size="32" class="mr-3">
        {{ icons[type] }}
      </v-icon>
    </template>

    <slot />

    <template v-slot:close="{ close }">
      <v-btn icon small @click="close">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </template>
  </v-alert>
</template>