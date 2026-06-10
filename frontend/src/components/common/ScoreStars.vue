<template>
  <el-rate
    :model-value="starValue"
    :max="5"
    allow-half
    :disabled="readonly"
    :colors="colors"
    @change="handleChange"
  />
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    score: number;
    max?: number;
    readonly?: boolean;
  }>(),
  {
    max: 10,
    readonly: true
  }
);

const emit = defineEmits<{
  "update:score": [value: number];
}>();

const colors = ["#9B7A42", "#C48634", "#E0A348"];
const starValue = computed(() => (props.score / props.max) * 5);

function handleChange(value: number): void {
  emit("update:score", Math.round((value / 5) * props.max));
}
</script>

