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
          <h2>品鉴历史</h2>
          <EmptyState
            v-if="notes.length === 0"
            icon="note"
            title="还没有品鉴记录"
            description="新的记录会出现在这里。"
          />
          <article v-for="note in notes" :key="note.id" class="history-row" @click="router.push(`/note/${note.id}`)">
            <div>
              <h3>{{ note.coffee_name }}</h3>
              <p class="subtle">{{ note.origin }} · {{ roastLevelLabel[note.roast_level] }}</p>
            </div>
            <ScoreStars :score="note.overall_score" />
          </article>
        </div>
      </section>
    </template>
  </section>
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { UserPlus } from "lucide-vue-next";
import { computed, nextTick, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { listNotes } from "@/api/note";
import { followUser, getUserProfile, unfollowUser } from "@/api/user";
import EmptyState from "@/components/common/EmptyState.vue";
import ScoreStars from "@/components/common/ScoreStars.vue";
import UserAvatar from "@/components/common/UserAvatar.vue";
import { useUserStore } from "@/stores/useUserStore";
import { roastLevelLabel } from "@/types/enums";
import type { TastingNote } from "@/types/note";
import type { UserProfile } from "@/types/user";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const profile = ref<UserProfile | null>(null);
const notes = ref<TastingNote[]>([]);
const loading = ref(false);
const chartEl = ref<HTMLDivElement | null>(null);

const canFollow = computed(() => {
  return Boolean(userStore.currentUser && profile.value && userStore.currentUser.id !== profile.value.user.id);
});

onMounted(fetchProfile);

async function fetchProfile(): Promise<void> {
  loading.value = true;
  try {
    const userId = Number(route.params.id);
    const results = await Promise.all([getUserProfile(userId), listNotes({ user_id: userId, page: 1, page_size: 20 })]);
    profile.value = results[0];
    notes.value = results[1].items;
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

@media (max-width: 860px) {
  .profile-hero,
  .stats-grid,
  .history-grid {
    grid-template-columns: 1fr;
  }
}
</style>

