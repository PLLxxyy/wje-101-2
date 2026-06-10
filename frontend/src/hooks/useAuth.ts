import { computed } from "vue";
import { useRouter } from "vue-router";

import { loginUser, refreshToken as requestRefresh, registerUser, type RegisterPayload } from "@/api/user";
import { useUserStore } from "@/stores/useUserStore";

export function useAuth() {
  const userStore = useUserStore();
  const router = useRouter();

  async function login(email: string, password: string): Promise<void> {
    const token = await loginUser({ email, password });
    userStore.setAuth(token.user, token.access_token, token.refresh_token);
  }

  async function register(username: string, email: string, password: string): Promise<void> {
    const payload: RegisterPayload = { username, email, password, avatar: null, bio: null };
    await registerUser(payload);
    await login(email, password);
  }

  function logout(): void {
    userStore.logout();
    router.push("/");
  }

  async function refreshToken(): Promise<void> {
    if (!userStore.refreshToken) {
      return;
    }
    const token = await requestRefresh(userStore.refreshToken);
    userStore.setAuth(token.user, token.access_token, token.refresh_token);
  }

  return {
    login,
    register,
    logout,
    refreshToken,
    currentUser: computed(() => userStore.currentUser),
    isLoggedIn: computed(() => userStore.isLoggedIn),
    isAdmin: computed(() => userStore.isAdmin)
  };
}

