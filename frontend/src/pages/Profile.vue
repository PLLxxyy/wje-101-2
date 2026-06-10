<template>
  <section class="page profile-page">
    <el-skeleton v-if="loading" :rows="8" animated />
    <template v-else-if="profile">
      <section class="profile-hero panel">
        <UserAvatar :user="profile.user" size="large" />
        <div>
          <h1>{{ profile.user.username }}</h1>
          <p>{{ profile.user.bio || "这位用户还没有填写简介" }}</p>
          <p class="subtle">关注 {{ profile.stats.following_count }} · 粉丝 {{ profile.stats.follower_count }}</p>
        </div>
        <el-button
          v-if="canFollow"
          :type="profile.stats.is_following ? 'default' : 'primary'"
          :icon="UserPlus"
          @click="toggleFollow"
        >
          {{ profile.stats.is_following ? "取消关注" : "关注" }}
        </el-button>
      </section>

      <section class="stats-grid">
        <div class="stat panel">
          <span>品鉴次数</span>
          <strong>{{ profile.stats.note_count }}</strong>
        </div>
        <div class="stat panel">
          <span>平均综合分</span>
          <strong>{{ profile.stats.average_score }}</strong>
        </div>
        <div class="stat panel">
          <span>偏好产地</span>
          <strong>{{ profile.stats.top_origins.join("、") || "暂无" }}</strong>
        </div>
      </section>

      <section class="history-grid">
        <div class="panel chart-panel">
          <h2>评分画像</h2>
          <div ref="chartEl" class="profile-chart"></div>
        </div>
        <div class="panel history-panel">
          <el-tabs v-model="activeTab" class="profile-tabs">
            <el-tab-pane label="品鉴笔记" name="notes">
              <EmptyState
                v-if="notes.length === 0"
                icon="note"
                title="还没有品鉴记录"
                description="新的记录会出现在这里。"
              />
              <article
                v-for="note in notes"
                :key="note.id"
                class="history-row"
                @click="router.push(`/note/${note.id}`)"
              >
                <div>
                  <h3>{{ note.coffee_name }}</h3>
                  <p class="subtle">{{ note.origin }} · {{ roastLevelLabel[note.roast_level] }}</p>
                </div>
                <ScoreStars :score="note.overall_score" />
              </article>
            </el-tab-pane>
            <el-tab-pane label="收藏" name="favorites">
              <EmptyState
                v-if="favorites.length === 0"
                icon="star"
                title="还没有收藏"
                description="收藏喜欢的笔记会出现在这里。"
              />
              <article
                v-for="note in favorites"
                :key="note.id"
                class="history-row"
                @click="router.push(`/note/${note.id}`)"
              >
                <div>
                  <h3>{{ note.coffee_name }}</h3>
                  <p class="subtle">{{ note.origin }} · {{ roastLevelLabel[note.roast_level] }}</p>
                </div>
                <ScoreStars :score="note.overall_score" />
              </article>
            </el-tab-pane>
            <el-tab-pane label="冲煮配方" name="recipes">
              <EmptyState
                v-if="recipes.length === 0"
                icon="coffee"
                title="还没有冲煮配方"
                description="新的配方会出现在这里。"
              />
              <article v-for="recipe in recipes" :key="recipe.id" class="recipe-card">
                <div>
                  <h3>{{ recipe.name }}</h3>
                  <p class="subtle">
                    {{ recipe.device }} · {{ recipe.water_temp }}℃ · {{ recipe.grind_size }} · {{ recipe.ratio }}
                  </p>
                </div>
                <el-button :icon="BookOpen" @click.stop="selectedRecipe = recipe">查看步骤</el-button>
              </article>
            </el-tab-pane>
          </el-tabs>
        </div>
      </section>

      <el-dialog v-model="detailVisible" title="配方步骤" width="620px">
        <template v-if="selectedRecipe">
          <h2>{{ selectedRecipe.name }}</h2>
          <p class="subtle">
            {{ selectedRecipe.device }} · {{ selectedRecipe.water_temp }}℃ · {{ selectedRecipe.grind_size }} ·
            {{ selectedRecipe.ratio }}
          </p>
          <ol class="step-list">
            <li v-for="step in selectedRecipe.steps" :key="step.step_number">
              <b>{{ step.step_number }}.</b> {{ step.description }}（{{ step.duration_seconds }}秒）
            </li>
          </ol>
        </template>
      </el-dialog>
    </template>
  </section>
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { BookOpen, UserPlus } from "lucide-vue-next";
import { computed, nextTick, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { listNotes } from "@/api/note";
import { listRecipes } from "@/api/recipe";
import { followUser, getUserFavorites, getUserProfile, unfollowUser } from "@/api/user";
import EmptyState from "@/components/common/EmptyState.vue";
import ScoreStars from "@/components/common/ScoreStars.vue";
import UserAvatar from "@/components/common/UserAvatar.vue";
import { useUserStore } from "@/stores/useUserStore";
import { roastLevelLabel } from "@/types/enums";
import type { TastingNote } from "@/types/note";
import type { BrewRecipe } from "@/types/recipe";
import type { UserProfile } from "@/types/user";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const profile = ref<UserProfile | null>(null);
const notes = ref<TastingNote[]>([]);
const recipes = ref<BrewRecipe[]>([]);
const favorites = ref<TastingNote[]>([]);
const loading = ref(false);
const chartEl = ref<HTMLDivElement | null>(null);
const activeTab = ref("notes");
const selectedRecipe = ref<BrewRecipe | null>(null);
const detailVisible = computed({
  get: () => Boolean(selectedRecipe.value),
  set: (value: boolean) => {
    if (!value) {
      selectedRecipe.value = null;
    }
  }
});

const canFollow = computed(() => {
  return Boolean(userStore.currentUser && profile.value && userStore.currentUser.id !== profile.value.user.id);
});

onMounted(fetchProfile);

async function fetchProfile(): Promise<void> {
  loading.value = true;
  try {
    const userId = Number(route.params.id);
    const results = await Promise.all([
      getUserProfile(userId),
      listNotes({ user_id: userId, page: 1, page_size: 20 }),
      listRecipes({ user_id: String(userId) }),
      getUserFavorites(userId, { page: 1, page_size: 20 })
    ]);
    profile.value = results[0];
    notes.value = results[1].items;
    recipes.value = results[2];
    favorites.value = results[3].items;
    await nextTick();
    renderChart();
  } finally {
    loading.value = false;
  }
}

function renderChart(): void {
  if (!chartEl.value || !profile.value) {
    return;
  }
  const scores = profile.value.stats.radar_scores;
  echarts.init(chartEl.value).setOption({
    radar: {
      indicator: [
        { name: "香气", max: 10 },
        { name: "酸度", max: 10 },
        { name: "醇厚", max: 10 },
        { name: "综合", max: 10 }
      ]
    },
    series: [
      {
        type: "radar",
        areaStyle: { opacity: 0.2 },
        data: [{ value: [scores.aroma, scores.acidity, scores.body, scores.overall], name: "平均评分" }]
      }
    ]
  });
}

async function toggleFollow(): Promise<void> {
  if (!profile.value) {
    return;
  }
  if (!userStore.isLoggedIn) {
    await router.push("/login");
    return;
  }
  if (profile.value.stats.is_following) {
    await unfollowUser(profile.value.user.id);
    profile.value.stats.is_following = false;
    profile.value.stats.follower_count -= 1;
  } else {
    await followUser(profile.value.user.id);
    profile.value.stats.is_following = true;
    profile.value.stats.follower_count += 1;
  }
}
</script>

<style scoped>
.profile-hero {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 18px;
  align-items: center;
  padding: 24px;
  border-radius: 8px;
}

.profile-hero h1 {
  margin: 0 0 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin: 18px 0;
}

.stat {
  display: grid;
  gap: 8px;
  padding: 18px;
  border-radius: 8px;
}

.stat strong {
  font-size: 28px;
}

.history-grid {
  display: grid;
  grid-template-columns: 380px minmax(0, 1fr);
  gap: 18px;
}

.chart-panel,
.history-panel {
  padding: 20px;
  border-radius: 8px;
}

.profile-chart {
  min-height: 330px;
}

.profile-tabs :deep(.el-tabs__header) {
  margin: 0 0 16px;
}

.history-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 0;
  border-top: 1px solid var(--line);
  cursor: pointer;
}

.history-row h3 {
  margin: 0 0 6px;
}

.recipe-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 14px 0;
  border-top: 1px solid var(--line);
}

.recipe-card h3 {
  margin: 0 0 6px;
}

.step-list li {
  margin: 10px 0;
  line-height: 1.7;
}

@media (max-width: 860px) {
  .profile-hero,
  .stats-grid,
  .history-grid {
    grid-template-columns: 1fr;
  }

  .recipe-card {
    display: grid;
    grid-template-columns: 1fr;
  }
}
</style>

