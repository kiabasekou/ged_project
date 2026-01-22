<script setup>
const props = defineProps({
  size: {
    type: [String, Number],
    default: 64
  },
  color: {
    type: String,
    default: 'indigo-darken-4'
  },
  overlay: {
    type: Boolean,
    default: false
  },
  message: {
    type: String,
    default: 'Chargement en cours...'
  }
})
</script>

<template>
  <div
    class="d-flex flex-column align-center justify-center"
    :class="{ 'position-absolute fill-parent': overlay }"
    style="z-index: 10;"
    v-if="true"
  >
    <v-progress-circular
      :size="size"
      :color="color"
      indeterminate
      class="mb-4"
    />
    <p class="text-subtitle-1 text-grey-darken-2 font-weight-medium">
      {{ message }}
    </p>
  </div>
</template>

<style scoped>
.fill-parent {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  border-radius: inherit;
}
</style>