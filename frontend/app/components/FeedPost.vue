<script setup lang="ts">
import type { FeedPost } from '~/api/feed.api'
import type { CommentResponse } from '~/api/games.api'
import { TABS } from '~/constants'

const props = defineProps<{
  post: FeedPost
  avatarFullUrl: (url: string | null | undefined) => string | null
  formatDate: (iso: string) => string
  formatCommentDate: (iso: string) => string
  onCommentSubmit?: (gameId: number, text: string) => Promise<void>
}>()

const emit = defineEmits<{
  vote: [post: FeedPost, isLike: boolean]
  commentSubmit: [gameId: number, text: string]
  loadMoreComments: [gameId: number]
}>()

const newCommentText = ref('')
const submitting = ref(false)

async function submitComment() {
  const text = newCommentText.value.trim()
  if (!text || submitting.value) return
  submitting.value = true
  try {
    if (props.onCommentSubmit) {
      await props.onCommentSubmit(props.post.game.id, text)
      newCommentText.value = ''
    } else {
      emit('commentSubmit', props.post.game.id, text)
      newCommentText.value = ''
    }
  } finally {
    submitting.value = false
  }
}

function stateLabel(stateId: string): string {
  return TABS.find((t) => t.id === stateId)?.label ?? stateId
}
</script>

<template>
  <article
    class="overflow-hidden rounded-xl border border-gray-700/50 bg-gray-800/30"
  >
    <!-- Header: author + action text -->
    <div class="flex items-center gap-3 p-4">
      <NuxtLink
        v-if="post.author.tag"
        :to="`/users/${post.author.tag}`"
        class="flex size-10 shrink-0 overflow-hidden rounded-full bg-gray-600 transition hover:ring-2 hover:ring-emerald-500/50"
      >
        <img
          v-if="avatarFullUrl(post.author.avatar_url)"
          :src="avatarFullUrl(post.author.avatar_url) ?? ''"
          :alt="post.author.username ?? ''"
          class="size-full object-cover"
        />
        <Icon v-else name="lucide:user" class="m-auto size-5 text-gray-400" />
      </NuxtLink>
      <div v-else class="flex size-10 shrink-0 overflow-hidden rounded-full bg-gray-600">
        <Icon name="lucide:user" class="m-auto size-5 text-gray-400" />
      </div>
      <div class="min-w-0 flex-1">
        <p class="text-sm text-gray-300">
          <NuxtLink
            v-if="post.author.tag"
            :to="`/users/${post.author.tag}`"
            class="font-medium text-white hover:text-emerald-400"
          >
            {{ post.author.username ?? 'Удалённый пользователь' }}
          </NuxtLink>
          <span v-else class="font-medium text-white">
            {{ post.author.username ?? 'Удалённый пользователь' }}
          </span>
          <template v-if="post.author.tag"> @{{ post.author.tag }} </template>
          <template v-if="post.action_type === 'game_created'">
            добавил игру
            <NuxtLink
              :to="`/games/${post.game.id}`"
              class="font-medium text-white hover:text-emerald-400"
            >
              {{ post.game.name }}
            </NuxtLink>
            в {{ stateLabel(post.game.state) }}
          </template>
          <template v-else-if="post.action_type === 'favorite_added'">
            пометил
            <NuxtLink
              :to="`/games/${post.game.id}`"
              class="font-medium text-white hover:text-emerald-400"
            >
              {{ post.game.name }}
            </NuxtLink>
            в Избранное
          </template>
          <template v-else-if="post.action_type === 'favorite_removed'">
            убрал
            <NuxtLink
              :to="`/games/${post.game.id}`"
              class="font-medium text-white hover:text-emerald-400"
            >
              {{ post.game.name }}
            </NuxtLink>
            из Избранного
          </template>
        </p>
        <p class="mt-0.5 text-xs text-gray-500">{{ formatDate(post.created_at) }}</p>
      </div>
    </div>

    <!-- Image for game_created -->
    <div
      v-if="post.action_type === 'game_created'"
      class="border-t border-gray-700/50"
    >
      <NuxtLink
        :to="`/games/${post.game.id}`"
        class="flex aspect-video items-center justify-center overflow-hidden bg-gray-700/80"
      >
        <img
          v-if="post.game.image_url"
          :src="post.game.image_url"
          :alt="post.game.name"
          class="h-full w-full object-cover"
        />
        <Icon v-else name="lucide:gamepad-2" class="size-16 text-gray-500" />
      </NuxtLink>
    </div>

    <!-- Comments preview for game_created -->
    <div
      v-if="post.action_type === 'game_created' && (post.comments?.length || post.comments_total)"
      class="border-t border-gray-700/50 p-4"
    >
      <div class="space-y-3">
        <GameCommentItem
          v-for="c in post.comments"
          :key="c.id"
          :comment="c"
          :depth="0"
          :avatar-full-url="avatarFullUrl"
          :format-comment-date="formatCommentDate"
          @vote="() => {}"
          @reply="() => {}"
        />
        <NuxtLink
          v-if="post.comments_total != null && post.comments_total > (post.comments?.length ?? 0)"
          :to="`/games/${post.game.id}`"
          class="inline-block text-sm text-emerald-400 hover:text-emerald-300"
        >
          Показать ещё ({{ post.comments_total - (post.comments?.length ?? 0) }})
        </NuxtLink>
      </div>
    </div>

    <!-- Comment form for game_created -->
    <div
      v-if="post.action_type === 'game_created'"
      class="border-t border-gray-700/50 p-4"
    >
      <div class="flex flex-col gap-2">
        <textarea
          v-model="newCommentText"
          placeholder="Написать комментарий (макс. 200 символов)"
          maxlength="200"
          rows="2"
          class="w-full rounded-lg border border-gray-600 bg-gray-700/50 px-3 py-2 text-sm text-white placeholder-gray-500 focus:border-emerald-500 focus:outline-none"
        />
        <div class="flex items-center justify-between">
          <span class="text-xs text-gray-500">{{ newCommentText.length }}/200</span>
          <UButton
            size="xs"
            color="primary"
            :disabled="!newCommentText.trim() || submitting"
            @click="submitComment"
          >
            {{ submitting ? '...' : 'Отправить' }}
          </UButton>
        </div>
      </div>
    </div>

    <!-- Vote buttons -->
    <div class="flex items-center gap-2 border-t border-gray-700/50 px-4 py-3">
      <button
        type="button"
        class="flex items-center gap-1 rounded-md px-2 py-1 text-sm transition"
        :class="[
          post.current_user_voted.liked
            ? 'bg-emerald-500/25 text-emerald-400 hover:bg-emerald-500/35'
            : 'text-gray-400 hover:bg-gray-600/50 hover:text-emerald-400',
        ]"
        @click="emit('vote', post, true)"
      >
        <Icon
          name="lucide:thumbs-up"
          :class="['size-4', post.current_user_voted.liked ? 'fill-current' : '']"
        />
        <span :class="post.current_user_voted.liked ? 'font-semibold' : ''">
          {{ post.like_count }}
        </span>
      </button>
      <button
        type="button"
        class="flex items-center gap-1 rounded-md px-2 py-1 text-sm transition"
        :class="[
          post.current_user_voted.disliked
            ? 'bg-rose-500/25 text-rose-400 hover:bg-rose-500/35'
            : 'text-gray-400 hover:bg-gray-600/50 hover:text-rose-400',
        ]"
        @click="emit('vote', post, false)"
      >
        <Icon
          name="lucide:thumbs-down"
          :class="['size-4', post.current_user_voted.disliked ? 'fill-current' : '']"
        />
        <span :class="post.current_user_voted.disliked ? 'font-semibold' : ''">
          {{ post.dislike_count }}
        </span>
      </button>
    </div>
  </article>
</template>
