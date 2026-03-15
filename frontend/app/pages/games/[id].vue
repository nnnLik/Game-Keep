<script setup lang="ts">
import { TABS } from '~/constants'
import { fetchGame } from '~/api/games.api'
import type { GameDetailResponse } from '~/api/games.api'
import { fetchMe } from '~/api/users.api'

definePageMeta({
  layout: 'default',
})

const route = useRoute()
const gameId = computed(() => Number(route.params.id))
const { $api } = useNuxtApp()

const game = ref<GameDetailResponse | null>(null)
const currentUser = ref<Awaited<ReturnType<typeof fetchMe>> | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

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
      </div>
    </template>
  </div>
</template>
