<script setup>
const props = defineProps({
  folders: {
    type: Array,
    required: true
  },
  selectedFolderId: {
    type: [Number, String, null],
    default: null
  }
})

const emit = defineEmits(['folder-selected'])

const selected = ref(props.selectedFolderId ? [props.selectedFolderId] : [])

watch(selected, (newVal) => {
  emit('folder-selected', newVal[0] || null)
})
</script>

<template>
  <v-treeview
    :items="folders"
    item-key="id"
    item-title="name"
    item-children="subfolders"
    open-on-click
    activatable
    v-model:selected="selected"
    active-class="bg-amber-lighten-4 text-indigo-darken-4"
    rounded
    density="comfortable"
  >
    <template v-slot:prepend="{ item, open }">
      <v-icon color="indigo-darken-2">
        {{ open || item.subfolders?.length > 0 ? 'mdi-folder-open' : 'mdi-folder' }}
      </v-icon>
    </template>

    <template v-slot:append="{ item }">
      <v-chip size="x-small" color="grey-lighten-2" v-if="item.document_count > 0">
        {{ item.document_count }}
      </v-chip>
    </template>

    <template v-slot:title="{ item }">
      <span class="font-weight-medium">{{ item.name }}</span>
    </template>
  </v-treeview>
</template>