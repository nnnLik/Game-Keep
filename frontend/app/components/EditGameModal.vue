<script setup lang="ts">
import {
  DEFAULT_GAME_STATE,
  GAME_NAME_PLACEHOLDER,
  STEAM_URL_PLACEHOLDER,
  TABS,
  V_MODEL_UPDATE,
  buildSteamAppUrl,
} from '~/constants'
import type { CreateGamePayload } from '~/api/users.api'
import type { GameDetailResponse } from '~/api/games.api'
import { updateGame } from '~/api/users.api'

const props = defineProps<{
  modelValue: boolean
  game: GameDetailResponse | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  updated: [game: GameDetailResponse]
}>()

const { $api } = useNuxtApp()

const STATE_OPTIONS = TABS.filter((t) => t.id !== 'favorites')

const form = reactive<
  CreateGamePayload & {
    genres: { id: string; description: string }[]
    developers: string[]
    publishers: string[]
  }
>({
  name: '',
  image_url: null as string | null,
  steam_app_id: null as string | null,
  state: DEFAULT_GAME_STATE,
  genres: [],
  developers: [],
  publishers: [],
  release_date: null as string | null,
  note: null as string | null,
  date_started: null as string | null,
  date_finished: null as string | null,
  hours_played: null as number | null,
})

const steamUrl = ref('')
const showCustomGenreInput = ref(false)
const customGenreInput = ref('')
const submitting = ref(false)
const error = ref<string | null>(null)

watch(
  () => [props.modelValue, props.game] as const,
  ([open, game]) => {
    if (open && game) {
      steamUrl.value = game.steam_app_id
        ? buildSteamAppUrl(game.steam_app_id)
        : ''
      form.name = game.name
      form.image_url = game.image_url ?? null
      form.steam_app_id = game.steam_app_id ?? null
      form.state = game.state
      form.genres = game.genres?.map((g) => ({ id: g.id, description: g.description })) ?? []
      form.developers = game.developers ?? []
      form.publishers = game.publishers ?? []
      form.release_date = game.release_date ?? null
      form.note = game.note ?? null
      form.date_started = game.date_started ?? null
      form.date_finished = game.date_finished ?? null
      form.hours_played = game.hours_played ?? null
      error.value = null
    }
  }
)

function close() {
  emit(V_MODEL_UPDATE, false)
}

function addCustomGenre() {
  const val = customGenreInput.value.trim()
  if (val.length < 3 || val.length > 10) return
  const exists = form.genres.some((g) => g.description.toLowerCase() === val.toLowerCase())
  if (exists) return
  form.genres.push({ id: `custom-${Date.now()}`, description: val })
  customGenreInput.value = ''
  showCustomGenreInput.value = false
}

function removeGenre(index: number) {
  form.genres.splice(index, 1)
}

async function submit() {
  const name = form.name.trim()
  if (!name) {
    error.value = 'Название обязательно'
    return
  }
  if (!props.game) return
  submitting.value = true
  error.value = null
  try {
    const updated = await updateGame($api, props.game.id, {
      name,
      image_url: form.image_url || undefined,
      steam_app_id: form.steam_app_id || undefined,
      state: form.state,
      is_favorite: props.game.is_favorite,
      genres: form.genres?.length ? form.genres : undefined,
      developers: form.developers?.length ? form.developers : undefined,
      publishers: form.publishers?.length ? form.publishers : undefined,
      release_date: form.release_date || undefined,
      note: form.note || undefined,
      date_started: form.date_started || undefined,
      date_finished: form.date_finished || undefined,
      hours_played:
        form.hours_played != null && !Number.isNaN(form.hours_played)
          ? form.hours_played
          : undefined,
    })
    emit('updated', { ...props.game, ...updated })
    close()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err?.data?.detail ?? 'Не удалось сохранить'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="modelValue && game"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      @click.self="close"
    >
      <div class="fixed inset-0 bg-black/60" aria-hidden="true" @click="close" />
      <div
        class="relative z-10 w-full max-w-6xl max-h-[90vh] overflow-y-auto rounded-xl bg-gray-900 p-6 shadow-xl"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-game-title"
        @click.stop
      >
        <h2 id="edit-game-title" class="mb-4 text-xl font-semibold text-white">
          Редактировать игру
        </h2>

        <form class="flex flex-col gap-4" @submit.prevent="submit">
          <div class="grid grid-cols-1 gap-4 md:grid-cols-[minmax(160px,200px)_1fr]">
            <div class="flex flex-col gap-3">
              <div
                class="aspect-[460/215] w-full overflow-hidden rounded-lg bg-gray-700"
              >
                <img
                  v-if="form.image_url"
                  :src="form.image_url"
                  alt="Обложка"
                  class="h-full w-full object-contain"
                  @error="form.image_url = null"
                >
                <div
                  v-else
                  class="flex h-full w-full items-center justify-center"
                >
                  <Icon name="lucide:image" class="size-12 text-gray-500" />
                </div>
              </div>
              <div>
                <label for="edit-steam-url" class="mb-1 block text-xs text-gray-500">
                  Ссылка Steam
                </label>
                <input
                  id="edit-steam-url"
                  v-model="steamUrl"
                  type="url"
                  :placeholder="STEAM_URL_PLACEHOLDER"
                  class="w-full rounded-lg border border-gray-600 bg-gray-800 px-4 py-2 text-sm text-white placeholder-gray-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                >
              </div>
            </div>
            <div class="flex flex-col gap-4">
              <div>
                <label for="edit-game-name" class="mb-1 block text-xs text-gray-500">
                  Название
                </label>
                <input
                  id="edit-game-name"
                  v-model="form.name"
                  type="text"
                  :placeholder="GAME_NAME_PLACEHOLDER"
                  class="w-full rounded-lg border border-gray-600 bg-gray-800 px-4 py-2 text-white placeholder-gray-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                  autocomplete="off"
                >
              </div>
              <div>
                <span class="mb-1 block text-xs text-gray-500">Жанры</span>
                <div class="flex flex-wrap items-center gap-1">
                  <span
                    v-for="(g, idx) in form.genres"
                    :key="g.id"
                    class="inline-flex items-center gap-1 rounded bg-gray-700 px-2 py-0.5 text-xs text-gray-300"
                  >
                    {{ g.description }}
                    <button
                      type="button"
                      class="hover:text-white"
                      aria-label="Удалить"
                      @click="removeGenre(idx)"
                    >
                      <Icon name="lucide:x" class="size-3" />
                    </button>
                  </span>
                  <template v-if="showCustomGenreInput">
                    <input
                      v-model="customGenreInput"
                      type="text"
                      placeholder="3–10 символов"
                      maxlength="10"
                      class="w-24 rounded border border-gray-600 bg-gray-800 px-2 py-0.5 text-xs text-white placeholder-gray-500 focus:border-emerald-500 focus:outline-none"
                      @keydown.enter.prevent="addCustomGenre"
                    >
                    <button
                      type="button"
                      class="rounded bg-emerald-600 px-2 py-0.5 text-xs text-white hover:bg-emerald-500"
                      @click="addCustomGenre"
                    >
                      Добавить
                    </button>
                  </template>
                  <button
                    v-else
                    type="button"
                    class="flex size-6 items-center justify-center rounded bg-gray-700 text-gray-400 hover:bg-gray-600 hover:text-white"
                    aria-label="Добавить жанр"
                    @click="showCustomGenreInput = true"
                  >
                    <Icon name="lucide:plus" class="size-3" />
                  </button>
                </div>
              </div>
              <div v-if="form.release_date">
                <span class="mb-1 block text-xs text-gray-500">Дата выхода</span>
                <p class="text-sm text-gray-300">{{ form.release_date }}</p>
              </div>
              <div v-if="form.developers?.length">
                <span class="mb-1 block text-xs text-gray-500">Разработчик</span>
                <p class="text-sm text-gray-300">{{ form.developers.join(', ') }}</p>
              </div>
              <div v-if="form.publishers?.length">
                <span class="mb-1 block text-xs text-gray-500">Издатель</span>
                <p class="text-sm text-gray-300">{{ form.publishers.join(', ') }}</p>
              </div>
              <div>
                <label for="edit-game-state" class="mb-1 block text-xs text-gray-500">
                  Статус
                </label>
                <select
                  id="edit-game-state"
                  v-model="form.state"
                  class="w-full rounded-lg border border-gray-600 bg-gray-800 px-4 py-2 text-white focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                >
                  <option
                    v-for="opt in STATE_OPTIONS"
                    :key="opt.id"
                    :value="opt.id"
                  >
                    {{ opt.label }}
                  </option>
                </select>
              </div>
              <div>
                <label for="edit-game-note" class="mb-1 block text-xs text-gray-500">
                  Заметка
                </label>
                <textarea
                  id="edit-game-note"
                  v-model="form.note"
                  rows="3"
                  maxlength="500"
                  placeholder="Заметка или отзыв"
                  class="w-full rounded-lg border border-gray-600 bg-gray-800 px-4 py-2 text-sm text-white placeholder-gray-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                />
              </div>
              <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <div>
                  <label for="edit-date-started" class="mb-1 block text-xs text-gray-500">
                    Начал играть
                  </label>
                  <input
                    id="edit-date-started"
                    v-model="form.date_started"
                    type="date"
                    class="w-full rounded-lg border border-gray-600 bg-gray-800 px-4 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                  >
                </div>
                <div>
                  <label for="edit-date-finished" class="mb-1 block text-xs text-gray-500">
                    Закончил играть
                  </label>
                  <input
                    id="edit-date-finished"
                    v-model="form.date_finished"
                    type="date"
                    class="w-full rounded-lg border border-gray-600 bg-gray-800 px-4 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                  >
                </div>
              </div>
              <div>
                <label for="edit-hours-played" class="mb-1 block text-xs text-gray-500">
                  Часов сыграно
                </label>
                <input
                  id="edit-hours-played"
                  v-model.number="form.hours_played"
                  type="number"
                  step="0.1"
                  min="0"
                  placeholder="0"
                  class="w-full rounded-lg border border-gray-600 bg-gray-800 px-4 py-2 text-sm text-white placeholder-gray-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                >
              </div>
            </div>
          </div>

          <p v-if="error" class="text-sm text-red-400">{{ error }}</p>
          <div class="flex justify-end gap-2">
            <button
              type="button"
              class="rounded-lg px-4 py-2 text-gray-400 hover:text-white"
              @click="close"
            >
              Отмена
            </button>
            <button
              type="submit"
              :disabled="submitting"
              class="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
            >
              {{ submitting ? 'Сохранение...' : 'Сохранить' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>
