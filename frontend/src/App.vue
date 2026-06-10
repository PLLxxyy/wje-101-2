<template>
  <el-config-provider>
    <div class="app-shell">
      <header class="topbar">
        <RouterLink to="/" class="brand">
          <Coffee class="brand-icon" />
          <span>咖啡品鉴社区</span>
        </RouterLink>
        <nav class="nav-links">
          <RouterLink to="/">首页</RouterLink>
          <RouterLink to="/beans">豆种库</RouterLink>
          <RouterLink to="/recipes">配方广场</RouterLink>
        </nav>
        <div class="topbar-actions">
          <el-button :icon="Search" circle aria-label="搜索" @click="focusSearch" />
          <el-button v-if="isLoggedIn" type="primary" :icon="PenLine" @click="router.push('/note/create')">
            写笔记
          </el-button>
          <UserAvatar v-if="currentUser" :user="currentUser" size="small" />
          <el-button v-if="isLoggedIn" text @click="logout">退出</el-button>
          <el-button v-else type="primary" plain @click="router.push('/login')">登录</el-button>
        </div>
      </header>
      <main>
        <RouterView />
      </main>
      <ErrorToast />
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { Coffee, PenLine, Search } from "lucide-vue-next";
import { storeToRefs } from "pinia";
import { useRouter } from "vue-router";

import ErrorToast from "@/components/common/ErrorToast.vue";
import UserAvatar from "@/components/common/UserAvatar.vue";
import { useAuth } from "@/hooks/useAuth";
import { useUserStore } from "@/stores/useUserStore";

const router = useRouter();
const userStore = useUserStore();
const { currentUser, isLoggedIn } = storeToRefs(userStore);
const { logout } = useAuth();

function focusSearch(): void {
  const element = document.querySelector<HTMLInputElement>("[data-global-search]");
  if (element) {
    element.focus();
  }
}
</script>

