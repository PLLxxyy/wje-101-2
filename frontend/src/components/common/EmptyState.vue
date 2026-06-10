<template>
  <div class="empty-state">
    <component :is="iconComponent" class="empty-icon" />
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
import { Bean, Coffee, NotebookText } from "lucide-vue-next";
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    icon?: "coffee" | "bean" | "note";
    title: string;
    description: string;
  }>(),
  {
    icon: "coffee"
  }
);

const iconComponent = computed(() => {
  if (props.icon === "bean") {
    return Bean;
  }
  if (props.icon === "note") {
    return NotebookText;
  }
  return Coffee;
});
</script>

