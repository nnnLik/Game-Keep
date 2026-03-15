<script setup lang="ts">
import type { CommentResponse } from '~/api/games.api'

defineProps<{
  comment: CommentResponse
  depth: number
  avatarFullUrl: (url: string | null | undefined) => string | null
  formatCommentDate: (iso: string) => string
}>()

const emit = defineEmits<{
  vote: [comment: CommentResponse, isLike: boolean]
  reply: [id: number]
}>()
</script>

<template>
  <div
    class="rounded-lg p-3"
    :class="depth === 0 ? 'bg-gray-700/50' : 'bg-gray-700/30'"
  >
    <div class="flex gap-3">
      <div
        class="flex shrink-0 overflow-hidden rounded-full bg-gray-600"
        :class="depth === 0 ? 'size-8' : 'size-6'"
      >
        <img
          v-if="avatarFullUrl(comment.author.avatar_url)"
          :src="avatarFullUrl(comment.author.avatar_url) ?? ''"
          :alt="comment.author.username ?? ''"
          class="size-full object-cover"
        />
        <Icon v-else name="lucide:user" class="m-auto text-gray-400" :class="depth === 0 ? 'size-4' : 'size-3'" />
      </div>
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2" :class="depth === 0 ? 'text-sm' : 'text-xs'">
          <span class="font-medium text-white">
            {{ comment.author.username ?? 'Удалённый пользователь' }}
          </span>
          <span v-if="comment.author.tag" class="text-gray-400">
            @{{ comment.author.tag }}
          </span>
          <span class="text-gray-500">
            {{ formatCommentDate(comment.created_at) }}
          </span>
        </div>
        <p class="mt-1 whitespace-pre-wrap text-gray-300" :class="depth === 0 ? '' : 'text-sm'">
          {{ comment.text }}
        </p>
        <div class="mt-2 flex items-center gap-4" :class="depth === 0 ? '' : 'gap-3'">
          <button
            type="button"
            class="flex items-center gap-1 text-gray-400 transition hover:text-emerald-400"
            :class="[
              depth === 0 ? 'text-sm' : 'text-xs',
              { 'text-emerald-400': comment.current_user_voted.liked },
            ]"
            @click="emit('vote', comment, true)"
          >
            <Icon
              name="lucide:thumbs-up"
              :class="[
                depth === 0 ? 'size-4' : 'size-3',
                comment.current_user_voted.liked ? 'fill-current' : '',
              ]"
            />
            {{ comment.like_count }}
          </button>
          <button
            type="button"
            class="flex items-center gap-1 text-gray-400 transition hover:text-rose-400"
            :class="[
              depth === 0 ? 'text-sm' : 'text-xs',
              { 'text-rose-400': comment.current_user_voted.disliked },
            ]"
            @click="emit('vote', comment, false)"
          >
            <Icon
              name="lucide:thumbs-down"
              :class="[
                depth === 0 ? 'size-4' : 'size-3',
                comment.current_user_voted.disliked ? 'fill-current' : '',
              ]"
            />
            {{ comment.dislike_count }}
          </button>
          <button
            type="button"
            class="text-gray-400 transition hover:text-white"
            :class="depth === 0 ? 'text-sm' : 'text-xs'"
            @click="emit('reply', comment.id)"
          >
            Ответить
          </button>
        </div>
        <div
          v-if="comment.children.length"
          class="mt-3 space-y-3 border-l-2 border-gray-600 pl-4"
        >
          <GameCommentItem
            v-for="child in comment.children"
            :key="child.id"
            :comment="child"
            :depth="depth + 1"
            :avatar-full-url="avatarFullUrl"
            :format-comment-date="formatCommentDate"
            @vote="(c, like) => emit('vote', c, like)"
            @reply="(id) => emit('reply', id)"
          />
        </div>
      </div>
    </div>
  </div>
</template>
