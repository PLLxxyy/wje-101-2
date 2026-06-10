<template>
  <button class="avatar-button" type="button" @click="goProfile">
    <el-avatar :size="sizeMap[size]" :src="user.avatar || undefined">
      {{ initial }}
    </el-avatar>
  </button>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";

import type { User } from "@/types/user";

const props = withDefaults(
  defineProps<{
    user: User;
    size?: "small" | "medium" | "large";
  }>(),
  {
    size: "medium"
  }
);

const router = useRouter();
const sizeMap = {
  small: 30,
  medium: 40,
  large: 76
};
const initial = computed(() => props.user.username.slice(0, 1).toUpperCase());

function goProfile(): void {
  router.push(`/profile/${props.user.id}`);
}
</script>

