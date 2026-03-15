<script setup lang="ts">
import { TABS } from '~/constants/profile'
import type { CreateGamePayload } from '~/api/users.api'
import { createGame } from '~/api/users.api'

const props = defineProps<{
  modelValue: boolean
  initialDraft?: Partial<CreateGamePayload> | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  draft: [data: Partial<CreateGamePayload>]
  created: []
}>()

const { $api } = useNuxtApp()

const STATE_OPTIONS = TABS.filter((t) => t.id !== 'favorites')

const form = reactive<CreateGamePayload & { is_favorite: boolean }>({
  name: '',
  state: 'backlog',
  is_favorite: false,
})

const submitting = ref(false)
const error = ref<string | null>(null)
const extraExpanded = ref(false)

watch(
  () => props.modelValue,
  (open) => {
    if (open && props.initialDraft) {
      form.name = props.initialDraft.name ?? ''
      form.state = props.initialDraft.state ?? 'backlog'
      form.is_favorite = props.initialDraft.is_favorite ?? false
    } else if (open && !props.initialDraft) {
      form.name = ''
      form.state = 'backlog'
      form.is_favorite = false
    }
    error.value = null
  }
)

function close() {
  emit('update:modelValue', false)
}

function closeWithDraft() {
  const hasData = form.name.trim() || form.state
  if (hasData) {
    emit('draft', {
      name: form.name.trim(),
      state: form.state,
      is_favorite: form.is_favorite,
    })
  }
  close()
}

function handleEscape(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    closeWithDraft()
  }
}

async function submit() {
  const name = form.name.trim()
  if (!name) {
    error.value = 'Введите название игры'
    return
  }
  submitting.value = true
  error.value = null
  try {
    await createGame($api, {
      name,
      state: form.state,
      is_favorite: form.is_favorite,
    })
    emit('created')
    close()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err?.data?.detail ?? 'Не удалось добавить игру'
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
        class="relative z-10 w-full max-w-md rounded-xl bg-gray-900 p-6 shadow-xl"
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-game-title"
        @click.stop
      >
        <h2 id="create-game-title" class="mb-4 text-xl font-semibold text-white">
          Добавить игру
        </h2>
        <form class="flex flex-col gap-4" @submit.prevent="submit">
          <div>
            <label for="game-name" class="mb-1 block text-sm text-gray-400">
              Название
            </label>
            <input
              id="game-name"
              v-model="form.name"
              type="text"
              placeholder="Название игры"
              class="w-full rounded-lg border border-gray-600 bg-gray-800 px-4 py-2 text-white placeholder-gray-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              autocomplete="off"
            />
          </div>
          <div>
            <label for="game-state" class="mb-1 block text-sm text-gray-400">
              Стейт
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
          <div
            class="rounded-lg border border-gray-700 bg-gray-800/50 p-3"
          >
            <button
              type="button"
              class="flex w-full items-center justify-between text-sm text-gray-400"
              @click="extraExpanded = !extraExpanded"
            >
              <span>Дополнительно</span>
              <Icon
                :name="extraExpanded ? 'lucide:chevron-up' : 'lucide:chevron-down'"
                class="size-4"
              />
            </button>
            <p
              v-if="extraExpanded"
              class="mt-2 text-xs text-gray-500"
            >
              Скоро: картинка, ссылки, рейтинг
            </p>
          </div>
          <p v-if="error" class="text-sm text-red-400">
            {{ error }}
          </p>
          <div class="flex justify-end gap-2">
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
