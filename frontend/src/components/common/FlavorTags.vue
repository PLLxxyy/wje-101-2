<template>
  <div class="flavor-tags">
    <el-tag
      v-for="tag in localTags"
      :key="tag"
      class="flavor-tag"
      :closable="editable"
      @close="removeTag(tag)"
    >
      {{ tag }}
    </el-tag>
    <div v-if="editable" class="tag-editor">
      <el-input
        v-model="draft"
        size="small"
        class="tag-input"
        @keyup.enter="addTag"
      />
      <el-button size="small" text @click="addTag">添加</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
  tags: string[];
  editable?: boolean;
}>();

const emit = defineEmits<{
  "update:tags": [value: string[]];
}>();

const draft = ref("");
const localTags = computed(() => props.tags);

function addTag(): void {
  const tag = draft.value.trim();
  if (!tag || props.tags.includes(tag)) {
    draft.value = "";
    return;
  }
  const next = props.tags.concat(tag);
  emit("update:tags", next);
  draft.value = "";
}

function removeTag(tag: string): void {
  emit(
    "update:tags",
    props.tags.filter((item) => item !== tag)
  );
}
</script>

