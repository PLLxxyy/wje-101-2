<template>
  <section class="page">
    <div class="page-heading">
      <p class="eyebrow">New Tasting</p>
      <h1 class="section-title">创建品鉴笔记</h1>
    </div>

    <el-form class="note-form" label-position="top" @submit.prevent>
      <div class="form-column panel">
        <h2>咖啡与评分</h2>
        <el-form-item label="从豆种库带入">
          <el-select v-model="selectedBeanId" filterable clearable @change="applyBean">
            <el-option v-for="bean in beans" :key="bean.id" :label="bean.name" :value="bean.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="咖啡名称">
          <el-input v-model="form.coffee_name" />
        </el-form-item>
        <el-form-item label="产地">
          <el-input v-model="form.origin" />
        </el-form-item>
        <el-form-item label="烘焙度">
          <el-select v-model="form.roast_level">
            <el-option label="浅烘" :value="RoastLevel.Light" />
            <el-option label="中烘" :value="RoastLevel.Medium" />
            <el-option label="深烘" :value="RoastLevel.Dark" />
          </el-select>
        </el-form-item>
        <el-form-item label="风味标签">
          <FlavorTags v-model:tags="form.flavor_tags" editable />
        </el-form-item>
        <div class="score-grid">
          <label v-for="item in scoreFields" :key="item.key">
            <span>{{ item.label }} {{ form[item.key] }}</span>
            <el-slider v-model="form[item.key]" :min="1" :max="10" />
          </label>
        </div>
      </div>

      <div class="form-column panel">
        <h2>冲煮与描述</h2>
        <el-form-item label="冲煮方式">
          <el-input v-model="form.brew_method" />
        </el-form-item>
        <el-form-item label="关联配方">
          <el-select v-model="form.brew_recipe_id" clearable>
            <el-option v-for="recipe in recipes" :key="recipe.id" :label="recipe.name" :value="recipe.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="配图 URL">
          <el-input v-model="imageUrl" />
        </el-form-item>
        <el-form-item label="品鉴描述">
          <el-input v-model="form.notes_text" type="textarea" :rows="8" />
        </el-form-item>
        <el-button type="primary" size="large" :loading="submitting" @click="submit">
          发布笔记
        </el-button>
      </div>
    </el-form>
  </section>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { listBeans } from "@/api/bean";
import { createNote } from "@/api/note";
import { listRecipes } from "@/api/recipe";
import FlavorTags from "@/components/common/FlavorTags.vue";
import { RoastLevel } from "@/types/enums";
import type { CoffeeBean } from "@/types/bean";
import type { NotePayload } from "@/types/note";
import type { BrewRecipe } from "@/types/recipe";

type ScoreKey = "aroma_score" | "acidity_score" | "body_score" | "overall_score";

const router = useRouter();
const beans = ref<CoffeeBean[]>([]);
const recipes = ref<BrewRecipe[]>([]);
const selectedBeanId = ref<number | null>(null);
const imageUrl = ref("");
const submitting = ref(false);
const scoreFields: { key: ScoreKey; label: string }[] = [
  { key: "aroma_score", label: "香气" },
  { key: "acidity_score", label: "酸度" },
  { key: "body_score", label: "醇厚度" },
  { key: "overall_score", label: "综合" }
];

const form = reactive<NotePayload>({
  coffee_name: "",
  origin: "",
  roast_level: RoastLevel.Light,
  flavor_tags: ["柑橘"],
  aroma_score: 7,
  acidity_score: 7,
  body_score: 7,
  overall_score: 7,
  brew_method: "V60 手冲",
  brew_recipe_id: null,
  coffee_bean_id: null,
  notes_text: "",
  image_url: null
});

onMounted(async () => {
  const results = await Promise.all([listBeans({}), listRecipes({ user_id: "me" })]);
  beans.value = results[0];
  recipes.value = results[1];
});

function applyBean(value: number | null): void {
  if (!value) {
    form.coffee_bean_id = null;
    return;
  }
  const bean = beans.value.find((item) => item.id === value);
  if (!bean) {
    return;
  }
  form.coffee_name = bean.name;
  form.origin = bean.origin;
  form.flavor_tags = bean.flavor_tags;
  form.coffee_bean_id = bean.id;
}

async function submit(): Promise<void> {
  if (!form.coffee_name || !form.origin || !form.notes_text || form.flavor_tags.length === 0) {
    ElMessage.warning("请补齐咖啡名称、产地、风味标签和品鉴描述");
    return;
  }
  submitting.value = true;
  try {
    form.image_url = imageUrl.value.trim() || null;
    const note = await createNote(form);
    ElMessage.success("品鉴笔记已发布");
    await router.push(`/note/${note.id}`);
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.page-heading {
  max-width: 760px;
  margin-bottom: 22px;
}

.eyebrow {
  color: var(--accent);
  font-weight: 800;
}

.note-form {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 22px;
}

.form-column {
  padding: clamp(18px, 3vw, 28px);
  border-radius: 8px;
}

.form-column h2 {
  margin-top: 0;
}

.score-grid {
  display: grid;
  gap: 16px;
}

.score-grid span {
  display: inline-block;
  margin-bottom: 6px;
  font-weight: 700;
}

@media (max-width: 860px) {
  .note-form {
    grid-template-columns: 1fr;
  }
}
</style>

