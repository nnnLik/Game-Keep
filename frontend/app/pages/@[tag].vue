<script setup lang="ts">
import {
  DEFAULT_GAME_STATE,
  TAB_ACTIVE_CLASSES,
  TAB_BADGE_CLASSES,
  TAB_ICON_CLASSES,
  TABS,
} from '~/constants'
import { fetchProfileByTag } from '~/api/users.api'
import type { ProfileByTagResponse } from '~/api/users.api'

definePageMeta({
  layout: 'default',
})

const route = useRoute()
const tag = computed(() => String(route.params.tag))
const { $api } = useNuxtApp()

const profile = ref<ProfileByTagResponse | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

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
        to="/"
        class="inline-flex items-center gap-2 text-gray-400 transition hover:text-white"
      >
        <Icon name="lucide:arrow-left" class="size-4" />
        Назад
      </NuxtLink>
    </div>

    <div v-if="loading" class="text-gray-400">Загрузка...</div>
    <div v-else-if="error" class="text-red-400">{{ error }}</div>
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
        <div class="flex gap-1 border-b border-gray-700" role="tablist">
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
