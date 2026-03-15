<script setup lang="ts">
import { completeRegistration } from '~/api/auth.api'

definePageMeta({
  layout: 'auth',
})

const { $api } = useNuxtApp()
const toast = useToast()
const router = useRouter()

const form = reactive({
  username: '',
  tag: '',
})
const avatarFile = ref<File | null>(null)
const avatarPreview = ref<string | null>(null)

const loading = ref(false)
const error = ref('')

function getErrorDetail(e: unknown): string {
  const err = e as { data?: { detail?: string | Array<{ msg?: string }> } }
  const d = err?.data?.detail
  if (Array.isArray(d)) return d.map((x) => x.msg ?? '').filter(Boolean).join(', ') || 'Ошибка'
  return (typeof d === 'string' ? d : null) ?? 'Ошибка'
}

function onAvatarChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    error.value = 'Выберите изображение (jpg, png, gif, webp)'
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    error.value = 'Файл не более 5 МБ'
    return
  }
  avatarFile.value = file
  error.value = ''
  const reader = new FileReader()
  reader.onload = () => {
    avatarPreview.value = reader.result as string
  }
  reader.readAsDataURL(file)
}

async function onSubmit() {
  if (!form.username.trim() || !form.tag.trim()) {
    error.value = 'Заполни имя и тег'
    return
  }
  error.value = ''
  loading.value = true
  try {
    await completeRegistration($api, {
      username: form.username.trim(),
      tag: form.tag.trim(),
      avatar: avatarFile.value ?? undefined,
    })
    toast.add({ title: 'Готово', description: 'Профиль создан', color: 'success' })
    await router.push('/')
  } catch (e: unknown) {
    error.value = getErrorDetail(e)
    toast.add({ title: 'Ошибка', description: error.value, color: 'error' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="space-y-6 w-full">
    <div class="text-center">
      <h1 class="text-2xl font-bold text-white">Game&Keep</h1>
      <p class="text-gray-400 mt-1">Имя, тег и аватар</p>
    </div>

    <UForm @submit="onSubmit" class="space-y-4 w-full">
      <div>
        <label class="mb-1 block text-sm text-gray-400">Аватар</label>
        <div class="flex items-center gap-4">
          <div
            class="flex size-20 shrink-0 items-center justify-center overflow-hidden rounded-full bg-gray-700"
          >
            <img
              v-if="avatarPreview"
              :src="avatarPreview"
              alt="Превью"
              class="size-full object-cover"
            />
            <Icon v-else name="lucide:user" class="size-10 text-gray-500" />
          </div>
          <input
            type="file"
            accept="image/jpeg,image/png,image/gif,image/webp"
            class="text-sm text-gray-400 file:mr-2 file:rounded-lg file:border-0 file:bg-emerald-600 file:px-4 file:py-2 file:text-white file:hover:bg-emerald-500"
            @change="onAvatarChange"
          />
        </div>
      </div>

      <UInput
        v-model="form.username"
        placeholder="Имя пользователя (мин. 5 символов)"
        autocomplete="username"
        size="lg"
        class="w-full"
        :disabled="loading"
      />
      <UInput
        v-model="form.tag"
        placeholder="Тег (3–15 символов, a-z 0-9)"
        autocomplete="off"
        size="lg"
        class="w-full"
        :disabled="loading"
      />

      <p v-if="error" class="text-sm text-red-400">{{ error }}</p>

      <UButton
        type="submit"
        block
        size="lg"
        :loading="loading"
      >
        Завершить регистрацию
      </UButton>
    </UForm>
  </div>
</template>
