<script setup lang="ts">
import { fetchUsersList, fetchMe } from '~/api/users.api'
import type { UserListItem } from '~/api/users.api'

definePageMeta({
  layout: 'default',
})

const { $api } = useNuxtApp()
const config = useRuntimeConfig()

const currentUser = ref<Awaited<ReturnType<typeof fetchMe>> | null>(null)
const users = ref<UserListItem[]>([])
const nextCursor = ref<string | null>(null)
const hasMore = ref(false)
const loading = ref(true)
const loadMoreLoading = ref(false)
const error = ref<string | null>(null)

function avatarFullUrl(avatarUrl: string | null | undefined): string | null {
  if (!avatarUrl) return null
  const base = (config.public.apiBase as string) || ''
  return `${base.replace(/\/$/, '')}/uploads/${avatarUrl}`
}

function userHref(tag: string | null): string {
  if (!tag) return '#'
  if (currentUser.value?.tag === tag) return '/'
  return `/users/${tag}`
}

async function loadInitial() {
  loading.value = true
  error.value = null
  try {
    const [meRes, listRes] = await Promise.allSettled([
      fetchMe($api),
      fetchUsersList($api, { limit: 20 }),
    ])
    if (meRes.status === 'fulfilled') currentUser.value = meRes.value
    const res = listRes.status === 'fulfilled' ? listRes.value : await fetchUsersList($api, { limit: 20 })
    users.value = res.items
    nextCursor.value = res.next_cursor
    hasMore.value = res.has_more
  } catch {
    error.value = 'Не удалось загрузить список'
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (!nextCursor.value || loadMoreLoading.value) return
  loadMoreLoading.value = true
  try {
    const res = await fetchUsersList($api, { limit: 20, cursor: nextCursor.value })
    users.value = [...users.value, ...res.items]
    nextCursor.value = res.next_cursor
    hasMore.value = res.has_more
  } catch {
    useToast().add({ title: 'Ошибка загрузки', color: 'error' })
  } finally {
    loadMoreLoading.value = false
  }
}

onMounted(loadInitial)
</script>

<template>
  <div>
    <h1 class="text-4xl font-bold text-white mb-8">Коллекционеры</h1>

    <div v-if="loading" class="text-gray-400">Загрузка...</div>
    <div v-else-if="error" class="flex flex-col gap-4">
      <p class="text-red-400">{{ error }}</p>
      <UButton variant="soft" @click="loadInitial">Повторить</UButton>
    </div>
    <template v-else>
      <ul class="flex flex-col gap-2">
        <li v-for="u in users" :key="u.tag ?? ''">
          <NuxtLink
            :to="userHref(u.tag)"
            class="flex items-center gap-4 rounded-lg bg-gray-800/50 px-4 py-3 transition-colors hover:bg-gray-800"
          >
            <div
              class="flex size-14 shrink-0 items-center justify-center overflow-hidden rounded-full bg-gray-600"
            >
              <img
                v-if="avatarFullUrl(u.avatar_url)"
                :src="avatarFullUrl(u.avatar_url) ?? ''"
                :alt="u.username ?? 'Аватар'"
                class="size-full object-cover"
              />
              <Icon v-else name="lucide:user" class="size-7 text-gray-400" />
            </div>
            <div class="flex-1 min-w-0">
              <span class="font-medium text-white block truncate">{{ u.username ?? 'Без имени' }}</span>
              <span v-if="u.tag" class="text-gray-400 text-sm">@{{ u.tag }}</span>
            </div>
            <span class="text-gray-400 text-sm shrink-0">
              {{ u.games_count }}
              {{ u.games_count === 1 ? 'игра' : u.games_count < 5 ? 'игры' : 'игр' }}
            </span>
          </NuxtLink>
        </li>
        <li v-if="users.length === 0" class="py-8 text-center text-gray-500">
          Пока никого нет
        </li>
      </ul>

      <div v-if="hasMore" class="mt-6">
        <UButton
          variant="soft"
          color="neutral"
          :loading="loadMoreLoading"
          block
          @click="loadMore"
        >
          Загрузить ещё
        </UButton>
      </div>
    </template>
  </div>
</template>
