<script setup lang="ts">
import {
  CreateGameErrors,
  DEFAULT_GAME_STATE,
  GAME_NAME_PLACEHOLDER,
  IMAGE_URL_PLACEHOLDER,
  STEAM_APP_URL_REGEX,
  STEAM_URL_OPTIONAL_LABEL,
  STEAM_URL_PLACEHOLDER,
  TABS,
  V_MODEL_UPDATE,
  buildSteamAppUrl,
  isValidSteamAppUrl,
} from '~/constants'
import type { CreateGamePayload } from '~/api/users.api'
import { createGame, fetchSteamGame } from '~/api/users.api'

const props = defineProps<{
  modelValue: boolean
  initialDraft?: Partial<CreateGamePayload> & { steam_url?: string; step?: number } | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  draft: [data: Partial<CreateGamePayload> & { steam_url?: string; step?: number }]
  created: []
}>()

const { $api } = useNuxtApp()

const STATE_OPTIONS = TABS.filter((t) => t.id !== 'favorites')

const step = ref(1)
const steamUrl = ref('')
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

const showCustomGenreInput = ref(false)
const customGenreInput = ref('')

const fetching = ref(false)
const submitting = ref(false)
const error = ref<string | null>(null)

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      if (props.initialDraft) {
        steamUrl.value =
          props.initialDraft.steam_url ??
          (props.initialDraft.steam_app_id
            ? buildSteamAppUrl(props.initialDraft.steam_app_id)
            : '')
        form.name = props.initialDraft.name ?? ''
        form.image_url = props.initialDraft.image_url ?? null
        form.steam_app_id = props.initialDraft.steam_app_id ?? null
        form.state = props.initialDraft.state ?? DEFAULT_GAME_STATE
        form.genres = props.initialDraft.genres ?? []
        form.developers = props.initialDraft.developers ?? []
        form.publishers = props.initialDraft.publishers ?? []
        form.release_date = props.initialDraft.release_date ?? null
        form.note = props.initialDraft.note ?? null
        form.date_started = props.initialDraft.date_started ?? null
        form.date_finished = props.initialDraft.date_finished ?? null
        form.hours_played = props.initialDraft.hours_played ?? null
        step.value = props.initialDraft.step ?? 1
      } else {
        steamUrl.value = ''
        form.name = ''
        form.image_url = null
        form.steam_app_id = null
        form.state = DEFAULT_GAME_STATE
        form.genres = []
        form.developers = []
        form.publishers = []
        form.release_date = null
        form.note = null
        form.date_started = null
        form.date_finished = null
        form.hours_played = null
        step.value = 1
      }
      error.value = null
    }
  }
)

function close() {
  emit(V_MODEL_UPDATE, false)
}

function closeWithDraft() {
  const hasData =
    steamUrl.value.trim() ||
    form.name.trim() ||
    form.image_url ||
    form.steam_app_id
  if (hasData) {
    emit('draft', {
      steam_url: steamUrl.value.trim() || undefined,
      name: form.name.trim() || undefined,
      image_url: form.image_url || undefined,
      steam_app_id: form.steam_app_id ?? undefined,
      state: form.state,
      genres: form.genres.length ? form.genres : undefined,
      developers: form.developers.length ? form.developers : undefined,
      publishers: form.publishers.length ? form.publishers : undefined,
      release_date: form.release_date ?? undefined,
      note: form.note ?? undefined,
      date_started: form.date_started ?? undefined,
      date_finished: form.date_finished ?? undefined,
      hours_played: form.hours_played ?? undefined,
      step: step.value,
    })
  }
  close()
}

function handleEscape(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    closeWithDraft()
  }
}

async function goToStep2() {
  const url = steamUrl.value.trim()
  if (!url) {
    step.value = 2
    error.value = null
    return
  }
  if (!isValidSteamAppUrl(url)) {
    error.value = CreateGameErrors.STEAM_URL_INVALID
    return
  }
  fetching.value = true
  error.value = null
  try {
    const data = await fetchSteamGame($api, url)
    form.name = data.name
    form.image_url = data.image_url
    form.steam_app_id = data.steam_app_id
    form.genres = data.genres ?? []
    form.developers = data.developers ?? []
    form.publishers = data.publishers ?? []
    form.release_date = data.release_date ?? null
    step.value = 2
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err?.data?.detail ?? CreateGameErrors.FETCH_FAILED
    const match = url.match(STEAM_APP_URL_REGEX)
    if (match) form.steam_app_id = match[1]
    step.value = 2
  } finally {
    fetching.value = false
  }
}

function goToStep3() {
  const name = form.name.trim()
  if (!name) {
    error.value = CreateGameErrors.NAME_REQUIRED
    return
  }
  error.value = null
  step.value = 3
}

function goBack() {
  step.value = step.value === 3 ? 2 : 1
  error.value = null
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
    error.value = CreateGameErrors.NAME_REQUIRED
    return
  }
  submitting.value = true
  error.value = null
  try {
    await createGame($api, {
      name,
      image_url: form.image_url || undefined,
      steam_app_id: form.steam_app_id || undefined,
      state: form.state,
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
    emit('created')
    close()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err?.data?.detail ?? CreateGameErrors.CREATE_FAILED
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleEscape)
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleEscape)
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      @click.self="closeWithDraft"
    >
      <div
        class="fixed inset-0 bg-black/60"
        aria-hidden="true"
        @click="closeWithDraft"
      />
      <div
        class="relative z-10 w-full max-w-6xl max-h-[90vh] overflow-y-auto rounded-xl bg-gray-900 p-6 shadow-xl"
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-game-title"
        @click.stop
      >
        <h2 id="create-game-title" class="mb-4 text-xl font-semibold text-white">
          Добавить игру
        </h2>

        <!-- Прогресс-бар + иконки -->
        <div class="mb-6 flex items-center gap-2">
          <div
            class="flex size-9 shrink-0 items-center justify-center rounded-full transition-colors"
            :class="
              step >= 1 ? 'bg-emerald-600 text-white' : 'bg-gray-700 text-gray-400'
            "
          >
            <Icon name="lucide:link" class="size-4" />
          </div>
          <div
            class="h-1 flex-1 rounded-full transition-colors"
            :class="step >= 2 ? 'bg-emerald-600' : 'bg-gray-700'"
          />
          <div
            class="flex size-9 shrink-0 items-center justify-center rounded-full transition-colors"
            :class="
              step >= 2 ? 'bg-emerald-600 text-white' : 'bg-gray-700 text-gray-400'
            "
          >
            <Icon name="lucide:gamepad-2" class="size-4" />
          </div>
          <div
            class="h-1 flex-1 rounded-full transition-colors"
            :class="step >= 3 ? 'bg-emerald-600' : 'bg-gray-700'"
          />
          <div
            class="flex size-9 shrink-0 items-center justify-center rounded-full transition-colors"
            :class="
              step >= 3 ? 'bg-emerald-600 text-white' : 'bg-gray-700 text-gray-400'
            "
          >
            <Icon name="lucide:star" class="size-4" />
          </div>
        </div>

        <!-- Контент с min-h для одинакового размера -->
        <div class="min-h-[420px] flex flex-col">
        <!-- Шаг 1: Ссылка Steam (опционально) -->
        <div v-if="step === 1" class="flex flex-col gap-4 flex-1">
          <div>
            <label for="steam-url" class="mb-1 block text-sm text-gray-400">
              Ссылка на игру в Steam {{ STEAM_URL_OPTIONAL_LABEL }}
            </label>
            <input
              id="steam-url"
              v-model="steamUrl"
              type="url"
              :placeholder="STEAM_URL_PLACEHOLDER"
              class="w-full rounded-lg border border-gray-600 bg-gray-800 px-4 py-2 text-white placeholder-gray-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              autocomplete="off"
            />
          </div>
          <p v-if="error" class="text-sm text-red-400">{{ error }}</p>
          <div class="flex justify-between gap-2">
            <button
              type="button"
              class="rounded-lg px-4 py-2 text-gray-400 hover:text-white"
              @click="closeWithDraft"
            >
              Отмена
            </button>
            <div class="flex gap-2">
              <button
                type="button"
                class="rounded-lg px-4 py-2 text-gray-300 hover:text-white"
                @click="goToStep2"
              >
                Пропустить
              </button>
              <button
                type="button"
                :disabled="fetching"
                class="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
                @click="goToStep2"
              >
                {{ fetching ? 'Загрузка...' : 'Далее' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Шаг 2: Форма (grid) -->
        <form
          v-else-if="step === 2"
          class="flex flex-col gap-4"
          @submit.prevent="goToStep3"
        >
          <div class="grid grid-cols-1 gap-4 md:grid-cols-[minmax(160px,200px)_1fr]">
            <!-- Левая колонка -->
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
                <label
                  for="steam-url-form"
                  class="mb-1 block text-xs text-gray-500"
                >
                  Ссылка Steam
                </label>
                <input
                  id="steam-url-form"
                  v-model="steamUrl"
                  type="url"
                  :placeholder="STEAM_URL_PLACEHOLDER"
                  class="w-full rounded-lg border border-gray-600 bg-gray-800 px-4 py-2 text-sm text-white placeholder-gray-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                >
              </div>
            </div>
            <!-- Правая колонка -->
            <div class="flex flex-col gap-4">
              <div>
                <label for="game-name" class="mb-1 block text-xs text-gray-500">
                  Название
                </label>
                <input
                  id="game-name"
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
                      @keydown.enter="addCustomGenre"
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
                <span class="mb-1 block text-xs text-gray-500"
                  >Разработчик</span
                >
                <p class="text-sm text-gray-300">
                  {{ form.developers.join(', ') }}
                </p>
              </div>
              <div v-if="form.publishers?.length">
                <span class="mb-1 block text-xs text-gray-500">Издатель</span>
                <p class="text-sm text-gray-300">
                  {{ form.publishers.join(', ') }}
                </p>
              </div>
              <div>
                <label for="game-state" class="mb-1 block text-xs text-gray-500">
                  Статус
                </label>
                <select
                  id="game-state"
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
                <label for="game-note" class="mb-1 block text-xs text-gray-500">
                  Заметка
                </label>
                <textarea
                  id="game-note"
                  v-model="form.note"
                  rows="3"
                  maxlength="500"
                  placeholder="Заметка или отзыв"
                  class="w-full rounded-lg border border-gray-600 bg-gray-800 px-4 py-2 text-sm text-white placeholder-gray-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                />
              </div>
              <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <div>
                  <label for="date-started" class="mb-1 block text-xs text-gray-500">
                    Начал играть
                  </label>
                  <div class="flex gap-1">
                    <input
                      id="date-started"
                      v-model="form.date_started"
                      type="date"
                      class="flex-1 rounded-lg border border-gray-600 bg-gray-800 px-4 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                    >
                  </div>
                </div>
                <div>
                  <label for="date-finished" class="mb-1 block text-xs text-gray-500">
                    Закончил играть
                  </label>
                  <div class="flex gap-1">
                    <input
                      id="date-finished"
                      v-model="form.date_finished"
                      type="date"
                      class="flex-1 rounded-lg border border-gray-600 bg-gray-800 px-4 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                    >
                  </div>
                </div>
              </div>
              <div>
                <label for="hours-played" class="mb-1 block text-xs text-gray-500">
                  Часов сыграно
                </label>
                <input
                  id="hours-played"
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
          <div class="flex justify-between gap-2">
            <button
              type="button"
              class="rounded-lg px-4 py-2 text-gray-400 hover:text-white"
              @click="closeWithDraft"
            >
              Отмена
            </button>
            <div class="flex gap-2">
              <button
                type="button"
                class="rounded-lg px-4 py-2 text-gray-400 hover:text-white"
                @click="goBack"
              >
                Назад
              </button>
              <button
                type="submit"
                class="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-500"
              >
                Далее
              </button>
            </div>
          </div>
        </form>

        <!-- Шаг 3: Оценка -->
        <form v-else-if="step === 3" class="flex flex-col gap-4" @submit.prevent="submit">
          <div class="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
            <h3 class="mb-3 text-sm font-medium text-gray-300">Оценка</h3>
            <p class="text-xs text-gray-500">Скоро</p>
          </div>

          <p v-if="error" class="text-sm text-red-400">{{ error }}</p>
          <div class="flex justify-between gap-2">
            <button
              type="button"
              class="rounded-lg px-4 py-2 text-gray-400 hover:text-white"
              @click="closeWithDraft"
            >
              Отмена
            </button>
            <div class="flex gap-2">
              <button
                type="button"
                class="rounded-lg px-4 py-2 text-gray-400 hover:text-white"
                @click="goBack"
              >
                Назад
              </button>
              <button
                type="submit"
                :disabled="submitting"
                class="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
              >
                {{ submitting ? 'Добавление...' : 'Добавить' }}
              </button>
            </div>
          </div>
        </form>
        </div>
      </div>
    </div>
  </Teleport>
</template>
