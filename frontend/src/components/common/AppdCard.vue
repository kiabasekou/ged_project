<script setup>
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: 'mdi-information'
  },
  color: {
    type: String,
    default: 'indigo-darken-4'
  },
  textColor: {
    type: String,
    default: 'white'
  },
  elevation: {
    type: [String, Number],
    default: 4
  },
  loading: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <v-card
    :elevation="elevation"
    class="overflow-hidden"
  >
    <v-card-title
      class="py-4 text-white font-weight-bold d-flex align-center"
      :class="`bg-${color}`"
    >
      <v-icon :color="textColor" class="mr-3" size="32">
        {{ icon }}
      </v-icon>
      {{ title }}
      <v-spacer />
      <slot name="actions" />
    </v-card-title>

    <v-card-text class="pt-6">
      <div v-if="loading" class="text-center py-8">
        <v-progress-circular indeterminate color="indigo-darken-4" />
      </div>
      <slot v-else />
    </v-card-text>
  </v-card>
</template>