import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";

import { useUserStore } from "@/stores/useUserStore";
import { UserRole } from "@/types/enums";
import { getAccessToken } from "@/utils/storage";

const routes: RouteRecordRaw[] = [
  { path: "/", name: "home", component: () => import("@/pages/Home.vue") },
  { path: "/login", name: "login", component: () => import("@/pages/Login.vue") },
  {
    path: "/note/create",
    name: "note-create",
    component: () => import("@/pages/NoteCreate.vue"),
    meta: { requiresAuth: true }
  },
  { path: "/note/:id", name: "note-detail", component: () => import("@/pages/NoteDetail.vue") },
  { path: "/beans", name: "beans", component: () => import("@/pages/BeanLibrary.vue") },
  { path: "/profile/:id", name: "profile", component: () => import("@/pages/Profile.vue") },
  { path: "/recipes", name: "recipes", component: () => import("@/pages/RecipeSquare.vue") }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
});

router.beforeEach(async (to) => {
  const userStore = useUserStore();
  const token = getAccessToken();
  if (token && !userStore.currentUser) {
    try {
      await userStore.loadCurrentUser();
    } catch {
      userStore.logout();
    }
  }
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  const roles = to.meta.roles as UserRole[] | undefined;
  if (roles && userStore.currentUser && !roles.includes(userStore.currentUser.role)) {
    return { name: "home" };
  }
  return true;
});

export default router;

