<template>
  <section class="login-page">
    <div class="login-art">
      <img :src="loginImage" alt="咖啡师制作咖啡" />
    </div>
    <div class="login-panel panel">
      <p class="eyebrow">Member Access</p>
      <h1>进入咖啡品鉴社区</h1>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="登录" name="login">
          <el-form label-position="top" @submit.prevent>
            <el-form-item label="邮箱"><el-input v-model="loginForm.email" /></el-form-item>
            <el-form-item label="密码"><el-input v-model="loginForm.password" type="password" show-password /></el-form-item>
            <el-button type="primary" size="large" :loading="loading" @click="submitLogin">登录</el-button>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-form label-position="top" @submit.prevent>
            <el-form-item label="用户名"><el-input v-model="registerForm.username" /></el-form-item>
            <el-form-item label="邮箱"><el-input v-model="registerForm.email" /></el-form-item>
            <el-form-item label="密码"><el-input v-model="registerForm.password" type="password" show-password /></el-form-item>
            <el-button type="primary" size="large" :loading="loading" @click="submitRegister">注册并登录</el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <div class="preset">
        <b>预置账号</b>
        <span>barista_wang / Coffee@2026</span>
        <span>coffee_lover / Coffee@2026</span>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuth } from "@/hooks/useAuth";

const router = useRouter();
const route = useRoute();
const { login, register } = useAuth();
const activeTab = ref("login");
const loading = ref(false);
const loginImage = "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=1000&q=80";
const loginForm = reactive({ email: "wang@coffee.com", password: "Coffee@2026" });
const registerForm = reactive({ username: "", email: "", password: "" });

async function submitLogin(): Promise<void> {
  loading.value = true;
  try {
    await login(loginForm.email, loginForm.password);
    ElMessage.success("登录成功");
    await router.push(String(route.query.redirect || "/"));
  } finally {
    loading.value = false;
  }
}

async function submitRegister(): Promise<void> {
  loading.value = true;
  try {
    await register(registerForm.username, registerForm.email, registerForm.password);
    ElMessage.success("注册成功");
    await router.push(String(route.query.redirect || "/"));
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page {
  display: grid;
  grid-template-columns: minmax(280px, 0.9fr) minmax(320px, 480px);
  gap: clamp(22px, 5vw, 54px);
  align-items: center;
  max-width: 1120px;
  margin: 0 auto;
}

.login-art img {
  width: 100%;
  height: clamp(360px, 70vh, 620px);
  object-fit: cover;
  border-radius: 8px;
}

.login-panel {
  padding: clamp(22px, 4vw, 36px);
  border-radius: 8px;
}

.login-panel h1 {
  margin-top: 0;
  font-size: clamp(30px, 5vw, 46px);
}

.eyebrow {
  color: var(--accent);
  font-weight: 800;
}

.preset {
  display: grid;
  gap: 6px;
  margin-top: 22px;
  color: var(--muted);
  font-size: 14px;
}

@media (max-width: 860px) {
  .login-page {
    grid-template-columns: 1fr;
  }
}
</style>

