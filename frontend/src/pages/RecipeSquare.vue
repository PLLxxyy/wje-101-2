<template>
  <section class="page">
    <div class="recipe-head">
      <div>
        <p class="eyebrow">Brew Recipes</p>
        <h1 class="section-title">配方广场</h1>
      </div>
      <el-button v-if="userStore.isLoggedIn" type="primary" :icon="Plus" @click="openCreate">创建配方</el-button>
    </div>

    <div class="filters panel">
      <el-input v-model="filters.search" clearable />
      <el-input v-model="filters.device" clearable />
      <el-input-number v-model="filters.temp_min" :min="60" :max="100" />
      <el-input-number v-model="filters.temp_max" :min="60" :max="100" />
      <el-button type="primary" :icon="Filter" @click="fetchRecipes">筛选</el-button>
    </div>

    <EmptyState
      v-if="recipes.length === 0"
      icon="coffee"
      title="没有匹配配方"
      description="调整器具或水温范围。"
    />
    <div class="recipe-list">
      <article v-for="recipe in recipes" :key="recipe.id" class="recipe-card">
        <div>
          <h2>{{ recipe.name }}</h2>
          <p class="subtle">{{ recipe.device }} · {{ recipe.water_temp }}℃ · {{ recipe.grind_size }} · {{ recipe.ratio }}</p>
          <p>创建者：{{ recipe.user?.username || "咖啡同好" }}</p>
        </div>
        <div class="recipe-actions">
          <el-button :icon="BookOpen" @click="selectedRecipe = recipe">查看步骤</el-button>
          <el-button v-if="canModify(recipe)" text :icon="Pencil" @click="openEdit(recipe)">编辑</el-button>
          <el-button v-if="canModify(recipe)" text type="danger" :icon="Trash2" @click="removeRecipe(recipe.id)">删除</el-button>
        </div>
      </article>
    </div>

    <el-dialog v-model="detailVisible" title="配方步骤" width="620px">
      <template v-if="selectedRecipe">
        <h2>{{ selectedRecipe.name }}</h2>
        <ol class="step-list">
          <li v-for="step in selectedRecipe.steps" :key="step.step_number">
            <b>{{ step.step_number }}.</b> {{ step.description }}（{{ step.duration_seconds }}秒）
          </li>
        </ol>
      </template>
    </el-dialog>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑配方' : '创建配方'" width="760px">
      <el-form label-position="top">
        <div class="recipe-form-grid">
          <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
          <el-form-item label="器具"><el-input v-model="form.device" /></el-form-item>
          <el-form-item label="水温"><el-input-number v-model="form.water_temp" :min="60" :max="100" /></el-form-item>
          <el-form-item label="研磨度"><el-input v-model="form.grind_size" /></el-form-item>
          <el-form-item label="粉水比"><el-input v-model="form.ratio" /></el-form-item>
        </div>
        <h3>步骤</h3>
        <div v-for="step in form.steps" :key="step.step_number" class="step-editor">
          <el-input-number v-model="step.step_number" :min="1" :max="20" />
          <el-input v-model="step.description" />
          <el-input-number v-model="step.duration_seconds" :min="0" :max="3600" />
        </div>
        <el-button text :icon="Plus" @click="addStep">添加步骤</el-button>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRecipe">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { ElMessage, ElMessageBox } from "element-plus";
import { BookOpen, Filter, Pencil, Plus, Trash2 } from "lucide-vue-next";
import { computed, onMounted, reactive, ref } from "vue";

import { createRecipe, deleteRecipe, listRecipes, updateRecipe } from "@/api/recipe";
import EmptyState from "@/components/common/EmptyState.vue";
import { useUserStore } from "@/stores/useUserStore";
import type { BrewRecipe, BrewStep, RecipePayload } from "@/types/recipe";

const userStore = useUserStore();
const recipes = ref<BrewRecipe[]>([]);
const selectedRecipe = ref<BrewRecipe | null>(null);
const dialogVisible = ref(false);
const editingId = ref<number | null>(null);
const filters = reactive({
  search: "",
  device: "",
  temp_min: 88,
  temp_max: 96
});
const form = reactive<RecipePayload>(emptyRecipe());
const detailVisible = computed({
  get: () => Boolean(selectedRecipe.value),
  set: (value: boolean) => {
    if (!value) {
      selectedRecipe.value = null;
    }
  }
});

onMounted(fetchRecipes);

async function fetchRecipes(): Promise<void> {
  recipes.value = await listRecipes({
    search: filters.search || undefined,
    device: filters.device || undefined,
    temp_min: filters.temp_min,
    temp_max: filters.temp_max
  });
}

function openCreate(): void {
  editingId.value = null;
  copyRecipe(emptyRecipe());
  dialogVisible.value = true;
}

function openEdit(recipe: BrewRecipe): void {
  editingId.value = recipe.id;
  copyRecipe(recipe);
  dialogVisible.value = true;
}

async function saveRecipe(): Promise<void> {
  if (editingId.value) {
    await updateRecipe(editingId.value, form);
    ElMessage.success("配方已更新");
  } else {
    await createRecipe(form);
    ElMessage.success("配方已创建");
  }
  dialogVisible.value = false;
  await fetchRecipes();
}

async function removeRecipe(recipeId: number): Promise<void> {
  await ElMessageBox.confirm("确认删除这个冲煮配方？", "删除配方");
  await deleteRecipe(recipeId);
  await fetchRecipes();
}

function addStep(): void {
  const step: BrewStep = { step_number: form.steps.length + 1, description: "", duration_seconds: 30 };
  form.steps.push(step);
}

function canModify(recipe: BrewRecipe): boolean {
  return Boolean(userStore.currentUser && (recipe.user_id === userStore.currentUser.id || userStore.isAdmin));
}

function copyRecipe(recipe: RecipePayload): void {
  form.name = recipe.name;
  form.device = recipe.device;
  form.water_temp = recipe.water_temp;
  form.grind_size = recipe.grind_size;
  form.ratio = recipe.ratio;
  form.steps = recipe.steps.map((step) => ({
    step_number: step.step_number,
    description: step.description,
    duration_seconds: step.duration_seconds
  }));
}

function emptyRecipe(): RecipePayload {
  return {
    name: "",
    device: "V60",
    water_temp: 92,
    grind_size: "中细",
    ratio: "1:15",
    steps: [{ step_number: 1, description: "闷蒸并分段注水", duration_seconds: 30 }]
  };
}
</script>

<style scoped>
.recipe-head,
.filters,
.recipe-card,
.recipe-actions,
.step-editor {
  display: flex;
  gap: 12px;
  align-items: center;
}

.recipe-head {
  justify-content: space-between;
  margin-bottom: 18px;
}

.eyebrow {
  color: var(--accent);
  font-weight: 800;
}

.filters {
  flex-wrap: wrap;
  padding: 14px;
  margin-bottom: 20px;
  border-radius: 8px;
}

.filters > * {
  width: 180px;
}

.recipe-list {
  display: grid;
  gap: 16px;
}

.recipe-card {
  justify-content: space-between;
  padding: 20px;
}

.recipe-card h2 {
  margin: 0 0 8px;
}

.recipe-actions {
  flex-wrap: wrap;
  justify-content: flex-end;
}

.step-list li {
  margin: 10px 0;
  line-height: 1.7;
}

.recipe-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.step-editor {
  margin-bottom: 10px;
}

@media (max-width: 780px) {
  .recipe-card,
  .recipe-head,
  .recipe-form-grid {
    display: grid;
    grid-template-columns: 1fr;
  }
}
</style>
