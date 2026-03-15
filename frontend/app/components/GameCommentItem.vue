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
      <NuxtLink
        v-if="comment.author.tag"
        :to="`/users/${comment.author.tag}`"
        class="flex shrink-0 overflow-hidden rounded-full bg-gray-600 transition hover:ring-2 hover:ring-emerald-500/50"
        :class="depth === 0 ? 'size-8' : 'size-6'"
      >
        <img
          v-if="avatarFullUrl(comment.author.avatar_url)"
          :src="avatarFullUrl(comment.author.avatar_url) ?? ''"
          :alt="comment.author.username ?? ''"
          class="size-full object-cover"
        />
        <Icon v-else name="lucide:user" class="m-auto text-gray-400" :class="depth === 0 ? 'size-4' : 'size-3'" />
      </NuxtLink>
      <div
        v-else
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
          <NuxtLink
            v-if="comment.author.tag"
            :to="`/users/${comment.author.tag}`"
            class="group inline-flex items-center gap-2 font-medium text-white transition hover:text-emerald-400"
          >
            {{ comment.author.username ?? 'Удалённый пользователь' }}
            <span class="text-gray-400 transition group-hover:text-emerald-400">@{{ comment.author.tag }}</span>
          </NuxtLink>
          <span v-else class="font-medium text-white">
            {{ comment.author.username ?? 'Удалённый пользователь' }}
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
            class="flex items-center gap-1 rounded-md px-2 py-1 transition"
            :class="[
              depth === 0 ? 'text-sm' : 'text-xs',
              comment.current_user_voted.liked
                ? 'bg-emerald-500/25 text-emerald-400 hover:bg-emerald-500/35'
                : 'text-gray-400 hover:bg-gray-600/50 hover:text-emerald-400',
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
            <span :class="comment.current_user_voted.liked ? 'font-semibold' : ''">
              {{ comment.like_count }}
            </span>
          </button>
          <button
            type="button"
            class="flex items-center gap-1 rounded-md px-2 py-1 transition"
            :class="[
              depth === 0 ? 'text-sm' : 'text-xs',
              comment.current_user_voted.disliked
                ? 'bg-rose-500/25 text-rose-400 hover:bg-rose-500/35'
                : 'text-gray-400 hover:bg-gray-600/50 hover:text-rose-400',
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
            <span :class="comment.current_user_voted.disliked ? 'font-semibold' : ''">
              {{ comment.dislike_count }}
            </span>
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
