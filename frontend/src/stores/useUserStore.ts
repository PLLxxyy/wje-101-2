import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { getCurrentUser } from "@/api/user";
import { UserRole } from "@/types/enums";
import type { User } from "@/types/user";
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "@/utils/storage";

export const useUserStore = defineStore("user", () => {
  const currentUser = ref<User | null>(null);
  const accessToken = ref<string | null>(getAccessToken());
  const refreshToken = ref<string | null>(getRefreshToken());

  const isLoggedIn = computed(() => Boolean(accessToken.value));
  const isAdmin = computed(() => currentUser.value?.role === UserRole.Admin);

  function setAuth(user: User, access: string, refresh: string): void {
    currentUser.value = user;
    accessToken.value = access;
    refreshToken.value = refresh;
    setTokens(access, refresh);
  }

  function setUser(user: User): void {
    currentUser.value = user;
  }

  function logout(): void {
    currentUser.value = null;
    accessToken.value = null;
    refreshToken.value = null;
    clearTokens();
  }

  async function loadCurrentUser(): Promise<User | null> {
    if (!accessToken.value) {
      return null;
    }
    currentUser.value = await getCurrentUser();
    return currentUser.value;
  }

  return {
    currentUser,
    accessToken,
    refreshToken,
    isLoggedIn,
    isAdmin,
    setAuth,
    setUser,
    logout,
    loadCurrentUser
  };
});

