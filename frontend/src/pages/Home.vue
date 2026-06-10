<template>
  <section class="page home-page">
    <div class="hero-band">
      <div>
        <p class="eyebrow">Tasting Journal</p>
        <h1 class="section-title">把每一杯咖啡的香气、酸质和余韵留下来</h1>
        <p class="subtle">记录品鉴，复盘冲煮，发现社区里正在被讨论的产区与豆种。</p>
      </div>
      <img :src="heroImage" alt="手冲咖啡器具与咖啡豆" />
    </div>

    <div class="home-layout">
      <section class="feed">
        <div class="filters panel">
          <el-input v-model="search" data-global-search clearable class="search-input" @keyup.enter="fetchNotes">
            <template #prefix><Search :size="17" /></template>
          </el-input>
          <el-select v-model="roastLevel" clearable class="filter-select" @change="fetchNotes">
            <el-option label="浅烘" value="light" />
            <el-option label="中烘" value="medium" />
            <el-option label="深烘" value="dark" />
          </el-select>
          <el-input v-model="origin" clearable class="filter-select" @keyup.enter="fetchNotes" />
          <el-button type="primary" :icon="SlidersHorizontal" @click="fetchNotes">筛选</el-button>
        </div>

        <EmptyState
          v-if="!loading && notes.length === 0"
          icon="note"
          title="还没有匹配的品鉴笔记"
          description="换一个筛选条件，或者写下第一杯咖啡的体验。"
        />
        <article v-for="note in notes" :key="note.id" class="note-card feed-card">
          <img :src="note.image_url || cardImage" alt="咖啡品鉴照片" />
          <div class="card-body">
            <div class="card-meta">
              <UserAvatar v-if="note.user" :user="note.user" size="small" />
              <span>{{ note.user?.username || "咖啡同好" }}</span>
              <span>{{ formatDate(note.created_at) }}</span>
            </div>
            <h2 @click="router.push(`/note/${note.id}`)">{{ note.coffee_name }}</h2>
            <p class="subtle">{{ note.origin }} · {{ roastLevelLabel[note.roast_level] }} · {{ note.brew_method }}</p>
            <FlavorTags :tags="note.flavor_tags" />
            <p class="note-text">{{ note.notes_text }}</p>
            <div class="card-actions">
              <ScoreStars :score="note.overall_score" />
              <el-button text :icon="Heart" @click="toggleLike(note)">
                {{ note.likes_count }}
              </el-button>
              <el-button text :icon="MessageCircle" @click="router.push(`/note/${note.id}`)">
                {{ note.comments_count }}
              </el-button>
            </div>
          </div>
        </article>
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="fetchNotes"
        />
      </section>

      <aside class="sidebar">
        <section class="panel side-panel">
          <h3>热门笔记</h3>
          <button v-for="note in popular" :key="note.id" type="button" class="rank-row" @click="router.push(`/note/${note.id}`)">
            <span>{{ note.coffee_name }}</span>
            <strong>{{ note.likes_count }}</strong>
          </button>
        </section>
        <section class="panel side-panel">
          <h3>推荐豆种</h3>
          <div v-for="bean in beans" :key="bean.id" class="bean-row">
            <b>{{ bean.name }}</b>
            <span>{{ bean.origin }}</span>
          </div>
        </section>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { Heart, MessageCircle, Search, SlidersHorizontal } from "lucide-vue-next";
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { listBeans } from "@/api/bean";
import { likeNote, listNotes, listPopularNotes, unlikeNote } from "@/api/note";
import EmptyState from "@/components/common/EmptyState.vue";
import FlavorTags from "@/components/common/FlavorTags.vue";
import ScoreStars from "@/components/common/ScoreStars.vue";
import UserAvatar from "@/components/common/UserAvatar.vue";
import { useUserStore } from "@/stores/useUserStore";
import { roastLevelLabel } from "@/types/enums";
import type { CoffeeBean } from "@/types/bean";
import type { TastingNote } from "@/types/note";

const router = useRouter();
const userStore = useUserStore();
const notes = ref<TastingNote[]>([]);
const popular = ref<TastingNote[]>([]);
const beans = ref<CoffeeBean[]>([]);
const loading = ref(false);
const page = ref(1);
const pageSize = 6;
const total = ref(0);
const roastLevel = ref("");
const origin = ref("");
const search = ref("");
const heroImage = "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1200&q=80";
const cardImage = "https://images.unsplash.com/photo-1517701604599-bb29b565090c?auto=format&fit=crop&w=900&q=80";

onMounted(async () => {
  await Promise.all([fetchNotes(), fetchSidebar()]);
});

async function fetchNotes(): Promise<void> {
  loading.value = true;
  try {
    const result = await listNotes({
      page: page.value,
      page_size: pageSize,
      roast_level: roastLevel.value || undefined,
      origin: origin.value || undefined,
      search: search.value || undefined
    });
    notes.value = result.items;
    total.value = result.total;
  } finally {
    loading.value = false;
  }
}

async function fetchSidebar(): Promise<void> {
  const results = await Promise.all([listPopularNotes(5), listBeans({})]);
  popular.value = results[0];
  beans.value = results[1].slice(0, 4);
}

async function toggleLike(note: TastingNote): Promise<void> {
  if (!userStore.isLoggedIn) {
    await router.push("/login");
    return;
  }
  if (note.liked_by_me) {
    await unlikeNote(note.id);
    note.likes_count -= 1;
    note.liked_by_me = false;
  } else {
    await likeNote(note.id);
    note.likes_count += 1;
    note.liked_by_me = true;
  }
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", { month: "short", day: "numeric" }).format(new Date(value));
}
</script>

<style scoped>
.hero-band {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(260px, 0.85fr);
  gap: clamp(24px, 5vw, 56px);
  align-items: end;
  margin-bottom: 32px;
}

.hero-band img {
  width: 100%;
  height: 270px;
  object-fit: cover;
  border-radius: 8px;
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--accent);
  font-weight: 800;
}

.home-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 28px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 14px;
  margin-bottom: 18px;
  border-radius: 8px;
}

.search-input {
  min-width: 260px;
  flex: 1;
}

.filter-select {
  width: 170px;
}

.feed-card {
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 18px;
  padding: 14px;
  margin-bottom: 16px;
}

.feed-card img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 6px;
}

.card-body h2 {
  margin: 8px 0;
  cursor: pointer;
}

.card-meta,
.card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.card-meta {
  color: var(--muted);
  font-size: 13px;
}

.note-text {
  color: #4d3a2a;
  line-height: 1.7;
}

.sidebar {
  display: grid;
  gap: 18px;
  align-content: start;
}

.side-panel {
  padding: 18px;
  border-radius: 8px;
}

.rank-row {
  display: flex;
  width: 100%;
  justify-content: space-between;
  padding: 10px 0;
  border: 0;
  border-bottom: 1px solid var(--line);
  background: transparent;
  color: var(--ink);
  text-align: left;
  cursor: pointer;
}

.bean-row {
  display: grid;
  gap: 4px;
  padding: 10px 0;
  border-bottom: 1px solid var(--line);
}

@media (max-width: 980px) {
  .home-layout,
  .hero-band {
    grid-template-columns: 1fr;
  }

  .feed-card {
    grid-template-columns: 1fr;
  }
}
</style>

