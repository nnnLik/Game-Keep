<script setup lang="ts">
import { TABS } from '~/constants'
import {
  fetchGame,
  fetchComments,
  createComment,
  voteComment,
} from '~/api/games.api'
import type {
  GameDetailResponse,
  CommentResponse,
} from '~/api/games.api'
import { fetchMe } from '~/api/users.api'

definePageMeta({
  layout: 'default',
})

const route = useRoute()
const gameId = computed(() => Number(route.params.id))
const { $api } = useNuxtApp()
const toast = useToast()

const game = ref<GameDetailResponse | null>(null)
const currentUser = ref<Awaited<ReturnType<typeof fetchMe>> | null>(null)
const comments = ref<CommentResponse[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const newCommentText = ref('')
const replyToId = ref<number | null>(null)
const submitting = ref(false)
const commentsLoading = ref(false)

const config = useRuntimeConfig()

const backHref = computed(() => {
  if (!game.value?.owner?.tag) return '/'
  const isOwn = currentUser.value?.tag === game.value.owner.tag
  return isOwn ? '/' : `/@${game.value.owner.tag}`
})

const stateLabel = computed(() => {
  if (!game.value) return ''
  const tab = TABS.find((t) => t.id === game.value!.state)
  return tab?.label ?? game.value.state
})

function avatarFullUrl(avatarUrl: string | null | undefined): string | null {
  if (!avatarUrl) return null
  const base = (config.public.apiBase as string) || ''
  return `${base.replace(/\/$/, '')}/uploads/${avatarUrl}`
}

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

function formatCommentDate(iso: string): string {
  return new Date(iso).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function loadComments() {
  if (!currentUser.value) return
  commentsLoading.value = true
  try {
    comments.value = await fetchComments($api, gameId.value)
  } catch {
    comments.value = []
  } finally {
    commentsLoading.value = false
  }
}

async function submitComment() {
  if (!currentUser.value || !game.value) return
  const text = newCommentText.value.trim()
  if (!text || text.length > 200) return
  submitting.value = true
  try {
    await createComment($api, gameId.value, text, replyToId.value)
    newCommentText.value = ''
    replyToId.value = null
    await loadComments()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    toast.add({
      title: 'Ошибка',
      description: err?.data?.detail ?? 'Не удалось отправить комментарий',
      color: 'error',
    })
  } finally {
    submitting.value = false
  }
}

async function onVote(comment: CommentResponse, isLike: boolean) {
  if (!currentUser.value) return
  try {
    await voteComment($api, gameId.value, comment.id, isLike)
    await loadComments()
  } catch {
    toast.add({ title: 'Ошибка голоса', color: 'error' })
  }
}

function startReply(id: number) {
  replyToId.value = id
}

function cancelReply() {
  replyToId.value = null
}

onMounted(async () => {
  try {
    const [gameRes, meRes] = await Promise.allSettled([
      fetchGame($api, gameId.value),
      fetchMe($api),
    ])
    if (gameRes.status === 'fulfilled') {
      game.value = gameRes.value
    } else {
      const err = gameRes.reason as { statusCode?: number }
      if (err?.statusCode === 404) {
        error.value = 'Игра не найдена'
      } else {
        error.value = 'Не удалось загрузить игру'
      }
    }
    if (meRes.status === 'fulfilled') {
      currentUser.value = meRes.value
    }
    if (currentUser.value) {
      await loadComments()
    }
  } catch {
    error.value = 'Не удалось загрузить игру'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div v-if="loading" class="text-gray-400">Загрузка...</div>
    <div v-else-if="error" class="text-red-400">{{ error }}</div>
    <template v-else-if="game">
      <NuxtLink
        :to="backHref"
        class="mb-4 inline-flex items-center gap-2 text-gray-400 transition hover:text-white"
      >
        <Icon name="lucide:arrow-left" class="size-4" />
        Назад
      </NuxtLink>

      <div class="flex flex-col gap-6">
        <div class="flex flex-col gap-4 sm:flex-row">
          <div
            class="flex size-32 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-gray-700 sm:size-40"
          >
            <img
              v-if="game.image_url"
              :src="game.image_url"
              :alt="game.name"
              class="h-full w-full object-cover"
            />
            <Icon
              v-else
              name="lucide:gamepad-2"
              class="size-16 text-gray-500"
            />
          </div>
          <div class="flex flex-1 flex-col gap-2">
            <h1 class="text-2xl font-bold text-white">{{ game.name }}</h1>
            <div class="flex flex-wrap items-center gap-2">
              <span
                class="rounded-full bg-gray-700/80 px-3 py-1 text-sm text-gray-300"
              >
                {{ stateLabel }}
              </span>
              <Icon
                v-if="game.is_favorite"
                name="lucide:heart"
                class="size-4 fill-red-500 text-red-500"
              />
              <span class="flex items-center gap-1 text-sm text-gray-400">
                <Icon name="lucide:eye" class="size-4" />
                {{ game.view_count }} просмотров
              </span>
            </div>
            <div v-if="game.genres?.length" class="flex flex-wrap gap-1">
              <span
                v-for="g in game.genres"
                :key="g.id"
                class="rounded bg-gray-700/50 px-2 py-0.5 text-xs text-gray-300"
              >
                {{ g.description }}
              </span>
            </div>
            <div v-if="game.developers?.length" class="text-sm text-gray-400">
              Разработчик: {{ game.developers.join(', ') }}
            </div>
            <div v-if="game.publishers?.length" class="text-sm text-gray-400">
              Издатель: {{ game.publishers.join(', ') }}
            </div>
            <div v-if="game.release_date" class="text-sm text-gray-400">
              Релиз: {{ game.release_date }}
            </div>
          </div>
        </div>

        <div
          v-if="game.note"
          class="rounded-lg bg-gray-800/50 p-4 text-gray-300"
        >
          <h2 class="mb-2 text-sm font-medium text-gray-400">Заметка</h2>
          <p class="whitespace-pre-wrap">{{ game.note }}</p>
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <div class="rounded-lg bg-gray-800/50 p-4">
            <h2 class="mb-2 text-sm font-medium text-gray-400">Даты</h2>
            <div class="space-y-1 text-sm text-gray-300">
              <p>Начало: {{ formatDate(game.date_started) }}</p>
              <p>Завершение: {{ formatDate(game.date_finished) }}</p>
            </div>
          </div>
          <div
            v-if="game.hours_played != null"
            class="rounded-lg bg-gray-800/50 p-4"
          >
            <h2 class="mb-2 text-sm font-medium text-gray-400">Время</h2>
            <p class="text-gray-300">{{ game.hours_played }} ч</p>
          </div>
        </div>

        <div
          v-if="game.owner"
          class="flex items-center gap-3 rounded-lg bg-gray-800/50 p-4"
        >
          <div
            class="flex size-10 shrink-0 items-center justify-center overflow-hidden rounded-full bg-gray-600"
          >
            <img
              v-if="avatarFullUrl(game.owner.avatar_url)"
              :src="avatarFullUrl(game.owner.avatar_url) ?? ''"
              :alt="game.owner.username ?? 'Аватар'"
              class="size-full object-cover"
            />
            <Icon v-else name="lucide:user" class="size-5 text-gray-400" />
          </div>
          <div>
            <p class="font-medium text-white">
              {{ game.owner.username ?? 'Удалённый пользователь' }}
            </p>
            <p v-if="game.owner.tag" class="text-sm text-gray-400">
              @{{ game.owner.tag }}
            </p>
          </div>
        </div>

        <!-- Комментарии -->
        <div class="rounded-lg bg-gray-800/50 p-4">
          <h2 class="mb-4 text-lg font-medium text-white">Комментарии</h2>
          <div v-if="!currentUser" class="py-4 text-center text-gray-400">
            Войдите, чтобы видеть и оставлять комментарии
          </div>
          <template v-else>
            <div v-if="commentsLoading" class="py-4 text-gray-400">
              Загрузка комментариев...
            </div>
            <div v-else class="space-y-4">
              <GameCommentItem
                v-for="c in comments"
                :key="c.id"
                :comment="c"
                :depth="0"
                :avatar-full-url="avatarFullUrl"
                :format-comment-date="formatCommentDate"
                @vote="onVote"
                @reply="startReply"
              />
              <div v-if="comments.length === 0" class="py-4 text-center text-gray-500">
                Пока нет комментариев
              </div>
            </div>

            <div class="mt-4">
              <p v-if="replyToId" class="mb-2 text-sm text-gray-400">
                Ответ на комментарий
                <button
                  type="button"
                  class="text-white underline"
                  @click="cancelReply"
                >
                  отмена
                </button>
              </p>
              <textarea
                v-model="newCommentText"
                placeholder="Написать комментарий (макс. 200 символов)"
                maxlength="200"
                rows="3"
                class="w-full rounded-lg border border-gray-600 bg-gray-700/50 px-3 py-2 text-white placeholder-gray-500 focus:border-emerald-500 focus:outline-none"
              />
              <div class="mt-2 flex items-center justify-between">
                <span class="text-sm text-gray-500">
                  {{ newCommentText.length }}/200
                </span>
                <UButton
                  size="sm"
                  color="primary"
                  :loading="submitting"
                  :disabled="!newCommentText.trim()"
                  @click="submitComment"
                >
                  Отправить
                </UButton>
              </div>
            </div>
          </template>
        </div>
      </div>
    </template>
  </div>
</template>
