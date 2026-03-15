<script setup lang="ts">
import {
  DEFAULT_GAME_STATE,
  TAB_ACTIVE_CLASSES,
  TAB_BADGE_CLASSES,
  TAB_ICON_CLASSES,
  TABS,
} from '~/constants'
import {
  fetchActivity,
  voteActivity,
  type FeedPost,
} from '~/api/feed.api'
import { createComment, fetchComments, voteComment } from '~/api/games.api'
import { fetchProfileByTag } from '~/api/users.api'
import type { ProfileByTagResponse } from '~/api/users.api'

definePageMeta({
  layout: 'default',
})

const route = useRoute()
const tag = computed(() => String(route.params.tag))
const { $api } = useNuxtApp()
const toast = useToast()

const profile = ref<ProfileByTagResponse | null>(null)
const activityPosts = ref<FeedPost[]>([])
const activityLoading = ref(false)
const activityLoadingMore = ref(false)
const activityNextCursor = ref<number | null>(null)
const activitySentinelRef = ref<HTMLElement | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

type SectionId = 'activities' | 'games'
const activeSection = ref<SectionId>('games')

type TabId = (typeof TABS)[number]['id']
const activeTab = ref<TabId>(DEFAULT_GAME_STATE)

const filteredGames = computed(() => {
  if (!profile.value) return []
  if (activeTab.value === 'favorites') {
    return profile.value.games.filter((g) => g.is_favorite)
  }
  return profile.value.games.filter((g) => g.state === activeTab.value)
})

const tabCounts = computed(() => {
  const counts: Record<string, number> = {}
  if (!profile.value) return counts
  for (const t of TABS) {
    if (t.id === 'favorites') {
      counts[t.id] = profile.value.games.filter((g) => g.is_favorite).length
    } else {
      counts[t.id] = profile.value.games.filter((g) => g.state === t.id).length
    }
  }
  return counts
})

const config = useRuntimeConfig()

function avatarFullUrl(avatarUrl: string | null | undefined): string | null {
  if (!avatarUrl) return null
  const base = (config.public.apiBase as string) || ''
  return `${base.replace(/\/$/, '')}/uploads/${avatarUrl}`
}

function bannerFullUrl(bannerUrl: string | null | undefined): string | null {
  if (!bannerUrl) return null
  const base = (config.public.apiBase as string) || ''
  return `${base.replace(/\/$/, '')}/uploads/${bannerUrl}`
}

function formatRegistrationDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  const date = new Date(iso)
  const month = date.toLocaleDateString('ru-RU', { month: 'long' })
  const year = date.getFullYear()
  return `${month} ${year} г.`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
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

async function loadActivity(cursor?: number | null) {
  if (cursor == null && activityPosts.value.length > 0) return
  if (cursor != null) activityLoadingMore.value = true
  else activityLoading.value = true
  try {
    const res = await fetchActivity($api, tag.value, {
      cursor: cursor ?? undefined,
      limit: 20,
    })
    if (cursor != null) {
      activityPosts.value.push(...res.items)
    } else {
      activityPosts.value = res.items
    }
    activityNextCursor.value = res.next_cursor
  } catch (e) {
    toast.add({ title: 'Не удалось загрузить активности', color: 'error' })
  } finally {
    activityLoading.value = false
    activityLoadingMore.value = false
  }
}

function onActivityTabClick() {
  if (activityPosts.value.length === 0 && !activityLoading.value) {
    loadActivity()
  }
}

async function onActivityVote(post: FeedPost, isLike: boolean) {
  try {
    await voteActivity($api, post.id, isLike)
    const hadLike = post.current_user_voted.liked
    const hadDislike = post.current_user_voted.disliked
    if (isLike) {
      if (hadLike) {
        post.current_user_voted.liked = false
        post.like_count = Math.max(0, post.like_count - 1)
      } else {
        if (hadDislike) {
          post.current_user_voted.disliked = false
          post.dislike_count = Math.max(0, post.dislike_count - 1)
        }
        post.current_user_voted.liked = true
        post.like_count += 1
      }
    } else {
      if (hadDislike) {
        post.current_user_voted.disliked = false
        post.dislike_count = Math.max(0, post.dislike_count - 1)
      } else {
        if (hadLike) {
          post.current_user_voted.liked = false
          post.like_count = Math.max(0, post.like_count - 1)
        }
        post.current_user_voted.disliked = true
        post.dislike_count += 1
      }
    }
  } catch {
    toast.add({ title: 'Ошибка голоса', color: 'error' })
  }
}

async function refreshActivityPostComments(post: FeedPost) {
  try {
    const comments = await fetchComments($api, post.game.id)
    post.comments = comments.slice(0, 3)
    post.comments_total = comments.length
  } catch {
    // ignore
  }
}

async function onActivityCommentSubmit(
  gameId: number,
  text: string,
  parentId?: number | null
) {
  try {
    await createComment($api, gameId, text, parentId)
    const post = activityPosts.value.find((p) => p.game.id === gameId)
    if (post) await refreshActivityPostComments(post)
  } catch (e) {
    const err = e as { data?: { detail?: string } }
    toast.add({
      title: 'Ошибка',
      description: err?.data?.detail ?? 'Не удалось отправить комментарий',
      color: 'error',
    })
  }
}

async function onActivityCommentVote(
  gameId: number,
  commentId: number,
  isLike: boolean
) {
  try {
    await voteComment($api, gameId, commentId, isLike)
    const post = activityPosts.value.find((p) => p.game.id === gameId)
    if (post) await refreshActivityPostComments(post)
  } catch {
    toast.add({ title: 'Ошибка голоса', color: 'error' })
  }
}

function handleActivityIntersect(entries: IntersectionObserverEntry[]) {
  if (!entries[0]?.isIntersecting || activityLoadingMore.value || !activityNextCursor.value) return
  loadActivity(activityNextCursor.value)
}

let activityObserver: IntersectionObserver | null = null

onMounted(() => {
  activityObserver = new IntersectionObserver(handleActivityIntersect, {
    root: null,
    rootMargin: '100px',
    threshold: 0,
  })
  watch(
    [() => activitySentinelRef.value, () => activeSection.value],
    () => {
      nextTick(() => {
        if (
          activeSection.value === 'activities' &&
          activitySentinelRef.value &&
          activityObserver
        ) {
          activityObserver.observe(activitySentinelRef.value)
        }
      })
    },
    { immediate: true }
  )
})

onUnmounted(() => {
  activityObserver?.disconnect()
})

onMounted(async () => {
  try {
    profile.value = await fetchProfileByTag($api, tag.value)
  } catch (e: unknown) {
    const err = e as { statusCode?: number }
    if (err?.statusCode === 404) {
      error.value = 'Пользователь не найден'
    } else {
      error.value = 'Не удалось загрузить профиль'
    }
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="mb-4">
      <NuxtLink
        to="/collectors"
        class="inline-flex items-center gap-2 text-gray-400 transition hover:text-white"
      >
        <Icon name="lucide:arrow-left" class="size-4" />
        Назад к коллекционерам
      </NuxtLink>
    </div>

    <div v-if="loading" class="text-gray-400">Загрузка...</div>
    <div v-else-if="error" class="flex flex-col gap-4">
      <p class="text-red-400">{{ error }}</p>
      <NuxtLink to="/collectors" class="text-emerald-400 hover:underline">
        Вернуться к коллекционерам
      </NuxtLink>
    </div>
    <template v-else-if="profile">
      <div class="mb-10">
        <div
          class="relative h-40 w-full rounded-t-2xl bg-gray-700/50 bg-cover bg-center"
          :style="
            bannerFullUrl(profile.banner_url)
              ? { backgroundImage: `url(${bannerFullUrl(profile.banner_url)})` }
              : {}
          "
          aria-label="Баннер профиля"
        />
        <div
          class="relative -mt-20 flex size-36 shrink-0 items-center justify-center overflow-hidden self-start rounded-full border-4 border-gray-950 bg-gray-600"
          aria-label="Аватар"
        >
          <img
            v-if="avatarFullUrl(profile.avatar_url)"
            :src="avatarFullUrl(profile.avatar_url) ?? ''"
            :alt="profile.username ?? 'Аватар'"
            class="size-full object-cover"
          />
          <Icon v-else name="lucide:user" class="size-20 text-gray-400" />
        </div>
        <div class="mt-4 flex flex-col gap-1">
          <div class="flex items-baseline gap-2">
            <h1 class="text-2xl font-bold text-white">
              {{ profile.username ?? 'Удалённый пользователь' }}
            </h1>
            <span v-if="profile.tag" class="text-gray-400">@{{ profile.tag }}</span>
          </div>
          <div
            v-if="profile.created_at"
            class="flex items-center gap-2 text-gray-400"
          >
            <Icon name="lucide:calendar" class="size-4 shrink-0" />
            <span>Регистрация: {{ formatRegistrationDate(profile.created_at) }}</span>
          </div>
        </div>
      </div>

      <div class="mb-6">
        <div class="mb-4 flex gap-1 border-b border-gray-700" role="tablist">
          <button
            type="button"
            role="tab"
            :aria-selected="activeSection === 'activities'"
            class="flex items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium transition-colors"
            :class="
              activeSection === 'activities'
                ? 'border-emerald-500/70 text-emerald-200'
                : 'border-transparent text-gray-400 hover:text-gray-300'
            "
            @click="activeSection = 'activities'; onActivityTabClick()"
          >
            <Icon name="lucide:activity" class="size-4 shrink-0" />
            <span>Активности</span>
          </button>
          <button
            type="button"
            role="tab"
            :aria-selected="activeSection === 'games'"
            class="flex items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium transition-colors"
            :class="
              activeSection === 'games'
                ? 'border-emerald-500/70 text-emerald-200'
                : 'border-transparent text-gray-400 hover:text-gray-300'
            "
            @click="activeSection = 'games'"
          >
            <Icon name="lucide:gamepad-2" class="size-4 shrink-0" />
            <span>Игры</span>
          </button>
        </div>

        <div v-if="activeSection === 'activities'" class="flex flex-col gap-6">
          <div v-if="activityLoading" class="py-12 text-center text-gray-400">
            Загрузка...
          </div>
          <template v-else>
            <FeedPost
              v-for="post in activityPosts"
              :key="post.id"
              :post="post"
              :avatar-full-url="avatarFullUrl"
              :format-date="formatDate"
              :format-comment-date="formatCommentDate"
              :on-comment-submit="onActivityCommentSubmit"
              :on-comment-vote="onActivityCommentVote"
              @vote="onActivityVote"
            />
            <div
              v-if="activityLoadingMore"
              class="py-8 text-center text-gray-400"
            >
              Загрузка...
            </div>
            <div
              ref="activitySentinelRef"
              class="h-4"
              aria-hidden="true"
            />
            <div
              v-if="!activityLoading && activityPosts.length === 0"
              class="py-16 text-center text-gray-500"
            >
              Пока нет активностей
            </div>
          </template>
        </div>

        <template v-else>
          <div class="mb-4 flex gap-1 border-b border-gray-700" role="tablist">
            <button
              v-for="tab in TABS"
              :key="tab.id"
              type="button"
              role="tab"
              :aria-selected="activeTab === tab.id"
              class="flex items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium transition-colors"
              :class="
                activeTab === tab.id
                  ? TAB_ACTIVE_CLASSES[tab.colorKey]
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              "
              @click="activeTab = tab.id"
            >
              <Icon
                :name="tab.icon"
                class="size-4 shrink-0"
                :class="activeTab === tab.id ? TAB_ICON_CLASSES[tab.colorKey] : ''"
              />
              <span>{{ tab.label }}</span>
              <span
                class="rounded-full px-2 py-0.5 text-xs"
                :class="
                  activeTab === tab.id
                    ? TAB_BADGE_CLASSES[tab.colorKey]
                    : 'bg-gray-700/80 text-gray-400'
                "
              >
                {{ tabCounts[tab.id] }}
              </span>
            </button>
          </div>

          <ul class="flex flex-col gap-2">
        <li v-for="game in filteredGames" :key="game.id">
          <NuxtLink
            :to="`/games/${game.id}`"
            class="flex items-center gap-4 rounded-lg bg-gray-800/50 px-4 py-3 transition-colors hover:bg-gray-800"
          >
            <div
              class="flex size-14 shrink-0 items-center justify-center overflow-hidden rounded bg-gray-600"
              aria-hidden
            >
              <img
                v-if="game.image_url"
                :src="game.image_url"
                :alt="game.name"
                class="h-full w-full object-cover"
              />
              <Icon v-else name="lucide:gamepad-2" class="size-7 text-gray-400" />
            </div>
            <span class="font-medium text-white">{{ game.name }}</span>
            <Icon
              v-if="game.is_favorite"
              name="lucide:heart"
              class="ml-auto size-4 shrink-0 fill-red-500 text-red-500"
            />
          </NuxtLink>
        </li>
        <li v-if="filteredGames.length === 0" class="py-8 text-center text-gray-500">
          В этой категории пока нет игр
        </li>
      </ul>
        </template>
      </div>
    </template>
  </div>
</template>
