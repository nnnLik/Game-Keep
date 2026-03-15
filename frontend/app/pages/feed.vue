<script setup lang="ts">
import {
  fetchFeed,
  voteActivity,
  type FeedPost,
} from '~/api/feed.api'
import { createComment, fetchComments, voteComment } from '~/api/games.api'

definePageMeta({
  layout: 'default',
})

const { $api } = useNuxtApp()
const toast = useToast()
const config = useRuntimeConfig()

const posts = ref<FeedPost[]>([])
const loading = ref(true)
const loadingMore = ref(false)
const nextCursor = ref<number | null>(null)
const sentinelRef = ref<HTMLElement | null>(null)

function avatarFullUrl(avatarUrl: string | null | undefined): string | null {
  if (!avatarUrl) return null
  const base = (config.public.apiBase as string) || ''
  return `${base.replace(/\/$/, '')}/uploads/${avatarUrl}`
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

async function loadFeed(cursor?: number | null) {
  if (cursor == null && posts.value.length > 0) return
  if (cursor != null) loadingMore.value = true
  else loading.value = true
  try {
    const res = await fetchFeed($api, { cursor: cursor ?? undefined, limit: 20 })
    if (cursor != null) {
      posts.value.push(...res.items)
    } else {
      posts.value = res.items
    }
    nextCursor.value = res.next_cursor
  } catch (e) {
    toast.add({ title: 'Не удалось загрузить ленту', color: 'error' })
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

async function onVote(post: FeedPost, isLike: boolean) {
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

async function refreshPostComments(post: FeedPost) {
  try {
    const comments = await fetchComments($api, post.game.id)
    post.comments = comments.slice(0, 3)
    post.comments_total = comments.length
  } catch {
    // ignore
  }
}

async function onCommentSubmit(
  gameId: number,
  text: string,
  parentId?: number | null
) {
  try {
    await createComment($api, gameId, text, parentId)
    const post = posts.value.find((p) => p.game.id === gameId)
    if (post) await refreshPostComments(post)
  } catch (e) {
    const err = e as { data?: { detail?: string } }
    toast.add({
      title: 'Ошибка',
      description: err?.data?.detail ?? 'Не удалось отправить комментарий',
      color: 'error',
    })
  }
}

async function onCommentVote(
  gameId: number,
  commentId: number,
  isLike: boolean
) {
  try {
    await voteComment($api, gameId, commentId, isLike)
    const post = posts.value.find((p) => p.game.id === gameId)
    if (post) await refreshPostComments(post)
  } catch {
    toast.add({ title: 'Ошибка голоса', color: 'error' })
  }
}

function handleIntersect(entries: IntersectionObserverEntry[]) {
  if (!entries[0]?.isIntersecting || loadingMore.value || !nextCursor.value) return
  loadFeed(nextCursor.value)
}

onMounted(() => {
  loadFeed()
})

let observer: IntersectionObserver | null = null
let observed = false
onMounted(() => {
  observer = new IntersectionObserver(handleIntersect, {
    root: null,
    rootMargin: '100px',
    threshold: 0,
  })
  watch(
    [() => sentinelRef.value, loading],
    () => {
      nextTick(() => {
        if (sentinelRef.value && observer && !observed) {
          observer.observe(sentinelRef.value)
          observed = true
        }
      })
    },
    { immediate: true }
  )
})
onUnmounted(() => {
  observer?.disconnect()
})
</script>

<template>
  <div>
    <h1 class="mb-2 text-3xl font-bold text-white">Лента</h1>
    <p class="mb-8 text-gray-400">
      Хронология действий коллекционеров
    </p>

    <div v-if="loading" class="py-12 text-center text-gray-400">
      Загрузка...
    </div>

    <div v-else class="flex flex-col gap-6">
      <FeedPost
        v-for="post in posts"
        :key="post.id"
        :post="post"
        :avatar-full-url="avatarFullUrl"
        :format-date="formatDate"
        :format-comment-date="formatCommentDate"
        :on-comment-submit="onCommentSubmit"
        :on-comment-vote="onCommentVote"
        @vote="onVote"
      />

      <div
        v-if="loadingMore"
        class="py-8 text-center text-gray-400"
      >
        Загрузка...
      </div>

      <div
        ref="sentinelRef"
        class="h-4"
        aria-hidden="true"
      />

      <div
        v-if="!loading && posts.length === 0"
        class="py-16 text-center text-gray-500"
      >
        Пока нет записей в ленте. Добавьте игру или отметьте избранное.
      </div>
    </div>
  </div>
</template>
