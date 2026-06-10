<template>
  <section class="page detail-page">
    <el-skeleton v-if="loading" :rows="8" animated />
    <template v-else-if="note">
      <article class="detail-main panel">
        <div class="detail-head">
          <div class="author-row">
            <UserAvatar v-if="note.user" :user="note.user" />
            <div>
              <h1>{{ note.coffee_name }}</h1>
              <p class="subtle">{{ note.user?.username || "咖啡同好" }} · {{ formatDate(note.created_at) }}</p>
            </div>
          </div>
          <div class="detail-actions">
            <el-button :icon="Heart" :type="note.liked_by_me ? 'primary' : 'default'" @click="toggleLike">
              {{ note.likes_count }}
            </el-button>
            <el-button v-if="canModify" :icon="Pencil" @click="openEdit">编辑</el-button>
            <el-button v-if="canModify" :icon="Trash2" type="danger" plain @click="removeNote">删除</el-button>
          </div>
        </div>

        <img class="detail-image" :src="note.image_url || detailImage" alt="咖啡杯与冲煮场景" />
        <div class="taste-grid">
          <div>
            <p class="subtle">{{ note.origin }} · {{ roastLevelLabel[note.roast_level] }} · {{ note.brew_method }}</p>
            <FlavorTags :tags="note.flavor_tags" />
            <p class="notes-text">{{ note.notes_text }}</p>
            <ScoreStars :score="note.overall_score" />
          </div>
          <div ref="chartEl" class="radar"></div>
        </div>

        <section v-if="note.brew_recipe" class="recipe-strip">
          <h3>{{ note.brew_recipe.name }}</h3>
          <p>{{ note.brew_recipe.device }} · {{ note.brew_recipe.water_temp }}℃ · {{ note.brew_recipe.ratio }}</p>
          <ol>
            <li v-for="step in note.brew_recipe.steps" :key="step.step_number">
              {{ step.description }}（{{ step.duration_seconds }}秒）
            </li>
          </ol>
        </section>
      </article>

      <section class="comments panel">
        <h2>评论</h2>
        <div class="comment-compose">
          <el-input v-model="commentDraft" type="textarea" :rows="3" />
          <el-button type="primary" :icon="Send" @click="sendComment">发布评论</el-button>
        </div>
        <EmptyState
          v-if="comments.length === 0"
          icon="coffee"
          title="还没有评论"
          description="分享冲煮建议或风味联想。"
        />
        <div v-for="comment in comments" :key="comment.id" class="comment-row">
          <UserAvatar v-if="comment.user" :user="comment.user" size="small" />
          <div>
            <b>{{ comment.user?.username || "咖啡同好" }}</b>
            <p>{{ comment.content }}</p>
          </div>
          <el-button v-if="canEditComment(comment.user_id)" text type="danger" @click="removeComment(comment.id)">
            删除
          </el-button>
        </div>
      </section>
    </template>

    <el-dialog v-model="editVisible" title="编辑品鉴笔记" width="720px">
      <el-form v-if="editReady" label-position="top">
        <el-form-item label="咖啡名称">
          <el-input v-model="editForm.coffee_name" />
        </el-form-item>
        <el-form-item label="产地">
          <el-input v-model="editForm.origin" />
        </el-form-item>
        <el-form-item label="风味标签">
          <FlavorTags v-model:tags="editForm.flavor_tags" editable />
        </el-form-item>
        <el-form-item label="品鉴描述">
          <el-input v-model="editForm.notes_text" type="textarea" :rows="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { ElMessage, ElMessageBox } from "element-plus";
import { Heart, Pencil, Send, Trash2 } from "lucide-vue-next";
import { computed, nextTick, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { createComment, deleteComment, deleteNote, getNote, likeNote, listComments, unlikeNote, updateNote } from "@/api/note";
import EmptyState from "@/components/common/EmptyState.vue";
import FlavorTags from "@/components/common/FlavorTags.vue";
import ScoreStars from "@/components/common/ScoreStars.vue";
import UserAvatar from "@/components/common/UserAvatar.vue";
import { useUserStore } from "@/stores/useUserStore";
import { RoastLevel, roastLevelLabel } from "@/types/enums";
import type { Comment, NotePayload, TastingNote } from "@/types/note";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const note = ref<TastingNote | null>(null);
const comments = ref<Comment[]>([]);
const loading = ref(true);
const commentDraft = ref("");
const chartEl = ref<HTMLDivElement | null>(null);
const editVisible = ref(false);
const editReady = ref(false);
const detailImage = "https://images.unsplash.com/photo-1442512595331-e89e73853f31?auto=format&fit=crop&w=1200&q=80";
const editForm = reactive<NotePayload>(emptyPayload());

const canModify = computed(() => {
  if (!note.value || !userStore.currentUser) {
    return false;
  }
  return note.value.user_id === userStore.currentUser.id || userStore.isAdmin;
});

onMounted(fetchDetail);

async function fetchDetail(): Promise<void> {
  loading.value = true;
  try {
    const noteId = Number(route.params.id);
    const results = await Promise.all([getNote(noteId), listComments(noteId)]);
    note.value = results[0];
    comments.value = results[1];
    await nextTick();
    renderRadar();
  } finally {
    loading.value = false;
  }
}

function renderRadar(): void {
  if (!chartEl.value || !note.value) {
    return;
  }
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
        data: [
          {
            value: [
              note.value.aroma_score,
              note.value.acidity_score,
              note.value.body_score,
              note.value.overall_score
            ],
            name: "评分"
          }
        ]
      }
    ]
  });
}

async function toggleLike(): Promise<void> {
  if (!note.value) {
    return;
  }
  if (!userStore.isLoggedIn) {
    await router.push("/login");
    return;
  }
  if (note.value.liked_by_me) {
    await unlikeNote(note.value.id);
    note.value.likes_count -= 1;
    note.value.liked_by_me = false;
  } else {
    await likeNote(note.value.id);
    note.value.likes_count += 1;
    note.value.liked_by_me = true;
  }
}

async function sendComment(): Promise<void> {
  if (!note.value || !commentDraft.value.trim()) {
    return;
  }
  if (!userStore.isLoggedIn) {
    await router.push("/login");
    return;
  }
  const comment = await createComment(note.value.id, commentDraft.value.trim());
  comments.value.push(comment);
  commentDraft.value = "";
}

function openEdit(): void {
  if (!note.value) {
    return;
  }
  copyNoteToForm(note.value);
  editReady.value = true;
  editVisible.value = true;
}

async function saveEdit(): Promise<void> {
  if (!note.value) {
    return;
  }
  note.value = await updateNote(note.value.id, editForm);
  editVisible.value = false;
  ElMessage.success("笔记已更新");
  await nextTick();
  renderRadar();
}

async function removeNote(): Promise<void> {
  if (!note.value) {
    return;
  }
  await ElMessageBox.confirm("删除后无法恢复，确认删除这篇笔记？", "删除笔记");
  await deleteNote(note.value.id);
  await router.push("/");
}

async function removeComment(commentId: number): Promise<void> {
  await deleteComment(commentId);
  comments.value = comments.value.filter((item) => item.id !== commentId);
}

function canEditComment(userId: number): boolean {
  return Boolean(userStore.currentUser && (userStore.currentUser.id === userId || userStore.isAdmin));
}

function copyNoteToForm(source: TastingNote): void {
  editForm.coffee_name = source.coffee_name;
  editForm.origin = source.origin;
  editForm.roast_level = source.roast_level;
  editForm.flavor_tags = source.flavor_tags.slice();
  editForm.aroma_score = source.aroma_score;
  editForm.acidity_score = source.acidity_score;
  editForm.body_score = source.body_score;
  editForm.overall_score = source.overall_score;
  editForm.brew_method = source.brew_method;
  editForm.brew_recipe_id = source.brew_recipe_id;
  editForm.coffee_bean_id = source.coffee_bean_id;
  editForm.notes_text = source.notes_text;
  editForm.image_url = source.image_url;
}

function emptyPayload(): NotePayload {
  return {
    coffee_name: "",
    origin: "",
    roast_level: RoastLevel.Light,
    flavor_tags: [],
    aroma_score: 7,
    acidity_score: 7,
    body_score: 7,
    overall_score: 7,
    brew_method: "",
    brew_recipe_id: null,
    coffee_bean_id: null,
    notes_text: "",
    image_url: null
  };
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", { dateStyle: "medium" }).format(new Date(value));
}
</script>

<style scoped>
.detail-main,
.comments {
  padding: clamp(18px, 3vw, 30px);
  border-radius: 8px;
}

.detail-head,
.author-row,
.detail-actions,
.comment-row,
.comment-compose {
  display: flex;
  gap: 14px;
  align-items: center;
}

.detail-head {
  justify-content: space-between;
}

.author-row h1 {
  margin: 0;
}

.detail-image {
  width: 100%;
  height: clamp(260px, 38vw, 430px);
  margin: 20px 0;
  object-fit: cover;
  border-radius: 8px;
}

.taste-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 24px;
}

.notes-text {
  line-height: 1.85;
}

.radar {
  min-height: 320px;
}

.recipe-strip {
  margin-top: 20px;
  padding: 18px;
  border-left: 4px solid var(--accent);
  background: rgba(191, 111, 34, 0.08);
}

.comments {
  margin-top: 22px;
}

.comment-compose {
  align-items: flex-start;
  margin-bottom: 18px;
}

.comment-row {
  align-items: flex-start;
  padding: 14px 0;
  border-top: 1px solid var(--line);
}

.comment-row p {
  margin: 6px 0 0;
}

@media (max-width: 840px) {
  .taste-grid,
  .detail-head {
    grid-template-columns: 1fr;
    display: grid;
  }

  .detail-actions {
    flex-wrap: wrap;
  }
}
</style>

