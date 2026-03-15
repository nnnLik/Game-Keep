<script setup lang="ts">
import {
  CreateGameErrors,
  DEFAULT_GAME_STATE,
  GAME_NAME_PLACEHOLDER,
  IMAGE_URL_PLACEHOLDER,
  STEAM_APP_URL_REGEX,
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
const form = reactive<CreateGamePayload & { is_favorite: boolean }>({
  name: '',
  image_url: null as string | null,
  steam_app_id: null as string | null,
  state: DEFAULT_GAME_STATE,
  is_favorite: false,
})

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
        form.is_favorite = props.initialDraft.is_favorite ?? false
        step.value = props.initialDraft.step ?? 1
      } else {
        steamUrl.value = ''
        form.name = ''
        form.image_url = null
        form.steam_app_id = null
        form.state = DEFAULT_GAME_STATE
        form.is_favorite = false
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
      is_favorite: form.is_favorite,
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
    error.value = CreateGameErrors.STEAM_URL_REQUIRED
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

function goBack() {
  step.value = 1
  error.value = null
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
      is_favorite: form.is_favorite,
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
        class="relative z-10 w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-xl bg-gray-900 p-6 shadow-xl"
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
        </div>

        <!-- Шаг 1: Ссылка Steam -->
        <div v-if="step === 1" class="flex flex-col gap-4">
          <div>
            <label for="steam-url" class="mb-1 block text-sm text-gray-400">
              Ссылка на игру в Steam
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
          <div class="flex justify-end gap-2">
            <button
              type="button"
              class="rounded-lg px-4 py-2 text-gray-400 hover:text-white"
              @click="closeWithDraft"
            >
              Отмена
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

        <!-- Шаг 2: Форма (карточки) -->
        <form v-else class="flex flex-col gap-4" @submit.prevent="submit">
          <!-- Карточка: Картинка -->
          <div class="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
            <h3 class="mb-3 text-sm font-medium text-gray-300">Картинка</h3>
            <div
              v-if="form.image_url"
              class="mb-3 flex aspect-video w-full items-center justify-center overflow-hidden rounded-lg bg-gray-700"
            >
              <img
                :src="form.image_url"
                alt="Обложка"
                class="h-full w-full object-contain"
                @error="form.image_url = null"
              />
            </div>
            <div
              v-else
              class="mb-3 flex aspect-video w-full items-center justify-center rounded-lg bg-gray-700"
            >
              <Icon name="lucide:image" class="size-12 text-gray-500" />
            </div>
            <input
              v-model="form.image_url"
              type="url"
              :placeholder="IMAGE_URL_PLACEHOLDER"
              class="w-full rounded-lg border border-gray-600 bg-gray-800 px-4 py-2 text-sm text-white placeholder-gray-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          <!-- Карточка: Основное -->
          <div class="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
            <h3 class="mb-3 text-sm font-medium text-gray-300">Основное</h3>
            <div class="flex flex-col gap-3">
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
                />
              </div>
              <div v-if="form.steam_app_id">
                <label class="mb-1 block text-xs text-gray-500">
                  Ссылка Steam
                </label>
                <a
                  :href="buildSteamAppUrl(form.steam_app_id)"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="block truncate rounded-lg border border-gray-600 bg-gray-800/50 px-4 py-2 text-sm text-emerald-400 hover:underline"
                >
                  store.steampowered.com/app/{{ form.steam_app_id }}/
                </a>
              </div>
            </div>
          </div>

          <!-- Карточка: Стейт -->
          <div class="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
            <h3 class="mb-3 text-sm font-medium text-gray-300">Стейт</h3>
            <div class="flex flex-col gap-3">
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
              <label class="flex cursor-pointer items-center gap-2">
                <input
                  v-model="form.is_favorite"
                  type="checkbox"
                  class="rounded border-gray-600 bg-gray-800 text-emerald-600 focus:ring-emerald-500"
                />
                <span class="text-sm text-gray-300">В избранное</span>
              </label>
            </div>
          </div>

          <!-- Карточка: Оценка (заглушка) -->
          <div class="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
            <h3 class="mb-3 text-sm font-medium text-gray-300">Оценка</h3>
            <p class="text-xs text-gray-500">Скоро</p>
          </div>

          <p v-if="error" class="text-sm text-red-400">{{ error }}</p>
          <div class="flex justify-end gap-2">
            <button
              type="button"
              class="rounded-lg px-4 py-2 text-gray-400 hover:text-white"
              @click="goBack"
            >
              Назад
            </button>
            <button
              type="button"
              class="rounded-lg px-4 py-2 text-gray-400 hover:text-white"
              @click="closeWithDraft"
            >
              Отмена
            </button>
            <button
              type="submit"
              :disabled="submitting"
              class="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
            >
              {{ submitting ? 'Добавление...' : 'Добавить' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>
