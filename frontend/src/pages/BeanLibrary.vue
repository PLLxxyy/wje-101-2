<template>
  <section class="page">
    <div class="library-head">
      <div>
        <p class="eyebrow">Bean Library</p>
        <h1 class="section-title">豆种库</h1>
      </div>
      <el-button v-if="userStore.isAdmin" type="primary" :icon="Plus" @click="openCreate">新增豆种</el-button>
    </div>

    <div class="filters panel">
      <el-input v-model="filters.search" clearable @keyup.enter="fetchBeans" />
      <el-input v-model="filters.origin" clearable />
      <el-select v-model="filters.process" clearable>
        <el-option v-for="item in processOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <el-input v-model="filters.flavor" clearable />
      <el-button type="primary" :icon="Filter" @click="fetchBeans">筛选</el-button>
    </div>

    <EmptyState
      v-if="!loading && beans.length === 0"
      icon="bean"
      title="没有匹配豆种"
      description="调整产地、处理法或风味条件。"
    />
    <div class="bean-grid">
      <article v-for="bean in beans" :key="bean.id" class="bean-card">
        <h2>{{ bean.name }}</h2>
        <p class="subtle">{{ bean.origin }} · {{ processMethodLabel[bean.process_method] }}</p>
        <FlavorTags :tags="bean.flavor_tags" />
        <p>{{ bean.description }}</p>
        <div v-if="userStore.isAdmin" class="admin-actions">
          <el-button text :icon="Pencil" @click="openEdit(bean)">编辑</el-button>
          <el-button text type="danger" :icon="Trash2" @click="removeBean(bean.id)">删除</el-button>
        </div>
      </article>
    </div>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑豆种' : '新增豆种'" width="640px">
      <el-form label-position="top">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="产地"><el-input v-model="form.origin" /></el-form-item>
        <el-form-item label="处理法">
          <el-select v-model="form.process_method">
            <el-option v-for="item in processOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="风味标签"><FlavorTags v-model:tags="form.flavor_tags" editable /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="4" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveBean">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { ElMessage, ElMessageBox } from "element-plus";
import { Filter, Pencil, Plus, Trash2 } from "lucide-vue-next";
import { onMounted, reactive, ref } from "vue";

import { createBean, deleteBean, listBeans, updateBean } from "@/api/bean";
import EmptyState from "@/components/common/EmptyState.vue";
import FlavorTags from "@/components/common/FlavorTags.vue";
import { useUserStore } from "@/stores/useUserStore";
import { ProcessMethod, processMethodLabel } from "@/types/enums";
import type { BeanPayload, CoffeeBean } from "@/types/bean";

const userStore = useUserStore();
const beans = ref<CoffeeBean[]>([]);
const loading = ref(false);
const dialogVisible = ref(false);
const editingId = ref<number | null>(null);
const filters = reactive({
  search: "",
  origin: "",
  process: "",
  flavor: ""
});
const form = reactive<BeanPayload>(emptyBean());
const processOptions = [
  { label: "水洗", value: ProcessMethod.Washed },
  { label: "日晒", value: ProcessMethod.Natural },
  { label: "蜜处理", value: ProcessMethod.Honey },
  { label: "厌氧发酵", value: ProcessMethod.Anaerobic }
];

onMounted(fetchBeans);

async function fetchBeans(): Promise<void> {
  loading.value = true;
  try {
    beans.value = await listBeans({
      search: filters.search || undefined,
      origin: filters.origin || undefined,
      process: filters.process || undefined,
      flavor: filters.flavor || undefined
    });
  } finally {
    loading.value = false;
  }
}

function openCreate(): void {
  editingId.value = null;
  copyBean(emptyBean());
  dialogVisible.value = true;
}

function openEdit(bean: CoffeeBean): void {
  editingId.value = bean.id;
  copyBean(bean);
  dialogVisible.value = true;
}

async function saveBean(): Promise<void> {
  if (editingId.value) {
    await updateBean(editingId.value, form);
    ElMessage.success("豆种已更新");
  } else {
    await createBean(form);
    ElMessage.success("豆种已新增");
  }
  dialogVisible.value = false;
  await fetchBeans();
}

async function removeBean(beanId: number): Promise<void> {
  await ElMessageBox.confirm("确认删除这个豆种？", "删除豆种");
  await deleteBean(beanId);
  await fetchBeans();
}

function copyBean(bean: BeanPayload): void {
  form.name = bean.name;
  form.origin = bean.origin;
  form.process_method = bean.process_method;
  form.flavor_tags = bean.flavor_tags.slice();
  form.description = bean.description;
}

function emptyBean(): BeanPayload {
  return {
    name: "",
    origin: "",
    process_method: ProcessMethod.Washed,
    flavor_tags: ["柑橘"],
    description: ""
  };
}
</script>

<style scoped>
.library-head,
.filters,
.admin-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.library-head {
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
  width: 190px;
}

.bean-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 18px;
}

.bean-card {
  padding: 20px;
}

.bean-card h2 {
  margin: 0 0 8px;
}

.bean-card p {
  line-height: 1.7;
}

.admin-actions {
  justify-content: flex-end;
}
</style>

