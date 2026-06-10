<template>
  <div class="empty-state">
    <component :is="iconComponent" class="empty-icon" />
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
import { Bean, Coffee, NotebookText, Star } from "lucide-vue-next";
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    icon?: "coffee" | "bean" | "note" | "star";
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
  if (props.icon === "star") {
    return Star;
  }
  return Coffee;
});
</script>

