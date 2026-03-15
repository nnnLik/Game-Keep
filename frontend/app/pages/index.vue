<script setup lang="ts">
import { TABS } from '~/constants/profile'

const TAB_ACTIVE_CLASSES: Record<string, string> = {
  slate: 'border-slate-500/70 text-slate-300',
  emerald: 'border-emerald-500/70 text-emerald-200',
  teal: 'border-teal-500/70 text-teal-200',
  amber: 'border-amber-500/70 text-amber-200',
  rose: 'border-rose-500/70 text-rose-200',
}
const TAB_ICON_CLASSES: Record<string, string> = {
  slate: 'text-slate-400',
  emerald: 'text-emerald-400',
  teal: 'text-teal-400',
  amber: 'text-amber-400',
  rose: 'text-rose-400',
}
const TAB_BADGE_CLASSES: Record<string, string> = {
  slate: 'bg-slate-500/25 text-slate-300',
  emerald: 'bg-emerald-500/25 text-emerald-300',
  teal: 'bg-teal-500/25 text-teal-300',
  amber: 'bg-amber-500/25 text-amber-300',
  rose: 'bg-rose-500/25 text-rose-300',
}

definePageMeta({
  layout: 'default',
})

const { $api } = useNuxtApp()
const { fetchMe, fetchMyGames } = await import('~/api/users.api')
import type { GameResponse } from '~/api/users.api'

const user = ref<Awaited<ReturnType<typeof fetchMe>> | null>(null)
const games = ref<GameResponse[]>([])
const loading = ref(true)
const gamesLoading = ref(true)
const error = ref<string | null>(null)

type TabId = (typeof TABS)[number]['id']
const activeTab = ref<TabId>('backlog')

const filteredGames = computed(() => {
  if (activeTab.value === 'favorites') {
    return games.value.filter((g) => g.is_favorite)
  }
  return games.value.filter((g) => g.state === activeTab.value)
})

const tabCounts = computed(() => {
  const counts: Record<string, number> = {}
  for (const tab of TABS) {
    if (tab.id === 'favorites') {
      counts[tab.id] = games.value.filter((g) => g.is_favorite).length
    } else {
      counts[tab.id] = games.value.filter((g) => g.state === tab.id).length
    }
  }
  return counts
})

onMounted(async () => {
  try {
    ;[user.value, games.value] = await Promise.all([
      fetchMe($api),
      fetchMyGames($api),
    ])
  } catch (e) {
    error.value = 'Не удалось загрузить профиль'
  } finally {
    loading.value = false
    gamesLoading.value = false
  }
})

function formatRegistrationDate(iso: string) {
  const date = new Date(iso)
  const month = date.toLocaleDateString('ru-RU', { month: 'long' })
  const year = date.getFullYear()
  return `${month} ${year} г.`
}
</script>

<template>
  <div>
    <!-- Tailwind: force inclusion of dynamic tab classes -->
    <div class="sr-only" aria-hidden="true">
      <span class="border-slate-500/70 text-slate-300" /><span class="text-slate-400 bg-slate-500/25" />
      <span class="border-emerald-500/70 text-emerald-200" /><span class="text-emerald-400 bg-emerald-500/25" />
      <span class="border-teal-500/70 text-teal-200" /><span class="text-teal-400 bg-teal-500/25" />
      <span class="border-amber-500/70 text-amber-200" /><span class="text-amber-400 bg-amber-500/25" />
      <span class="border-rose-500/70 text-rose-200" /><span class="text-rose-400 bg-rose-500/25" />
    </div>
    <div v-if="loading" class="text-gray-400">Загрузка...</div>
    <div v-else-if="error" class="text-red-400">{{ error }}</div>
    <template v-else-if="user">
      <!-- Блок информации о пользователе -->
      <div class="mb-10">
        <div
          class="relative h-40 w-full rounded-t-2xl bg-gray-700/50"
          aria-label="Баннер профиля"
        />
        <div
          class="relative -mt-20 flex size-36 shrink-0 items-center justify-center self-start rounded-full border-4 border-gray-950 bg-gray-600"
          aria-label="Аватар"
        >
          <Icon name="lucide:user" class="size-20 text-gray-400" />
        </div>
        <div class="mt-4 flex flex-col gap-1">
          <div class="flex items-baseline gap-2">
            <h1 class="text-2xl font-bold text-white">
              {{ user.username }}
            </h1>
            <span class="text-gray-400">@{{ user.tag }}</span>
          </div>
          <div class="flex items-center gap-2 text-gray-400">
            <Icon name="lucide:calendar" class="size-4 shrink-0" />
            <span>Регистрация: {{ formatRegistrationDate(user.created_at) }}</span>
          </div>
        </div>
      </div>

      <!-- Табы стейтов -->
      <div class="mb-6">
        <div
          class="flex gap-1 border-b border-gray-700"
          role="tablist"
        >
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
      </div>

      <!-- Список игр -->
      <div v-if="gamesLoading" class="text-gray-400">Загрузка игр...</div>
      <ul v-else class="flex flex-col gap-2">
        <li
          v-for="game in filteredGames"
          :key="game.id"
          class="flex items-center gap-4 rounded-lg bg-gray-800/50 px-4 py-3 transition-colors hover:bg-gray-800"
        >
          <!-- Мок картинки -->
          <div
            class="flex size-14 shrink-0 items-center justify-center overflow-hidden rounded bg-gray-600"
            aria-hidden
          >
            <Icon name="lucide:gamepad-2" class="size-7 text-gray-400" />
          </div>
          <span class="font-medium text-white">{{ game.name }}</span>
          <Icon
            v-if="game.is_favorite"
            name="lucide:heart"
            class="ml-auto size-4 shrink-0 fill-red-500 text-red-500"
          />
        </li>
        <li
          v-if="filteredGames.length === 0"
          class="py-8 text-center text-gray-500"
        >
          В этой категории пока нет игр
        </li>
      </ul>
    </template>
  </div>
</template>
