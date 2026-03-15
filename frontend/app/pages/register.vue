<script setup lang="ts">
import { registerStart } from '~/api/auth.api'

definePageMeta({
  layout: 'auth',
})

const config = useRuntimeConfig()
const toast = useToast()

const form = reactive({
  email: '',
  password: '',
})

const loading = ref(false)
const error = ref('')

function getErrorDetail(e: unknown): string {
  const err = e as { data?: { detail?: string | Array<{ msg?: string }> } }
  const d = err?.data?.detail
  if (Array.isArray(d)) return d.map((x) => x.msg ?? '').filter(Boolean).join(', ') || 'Ошибка'
  return (typeof d === 'string' ? d : null) ?? 'Ошибка регистрации'
}

async function onSubmit() {
  if (!form.email || !form.password) {
    error.value = 'Заполни все поля'
    return
  }
  error.value = ''
  loading.value = true
  try {
    const res = await registerStart(config.public.apiBase as string, form)
    useAuthStore().setTokens(res.access_token, res.refresh_token)
    window.location.href = '/complete-registration'
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
      <p class="text-gray-400 mt-1">Создать аккаунт</p>
    </div>

    <UForm @submit="onSubmit" class="space-y-4 w-full">
      <UInput
        v-model="form.email"
        type="email"
        placeholder="Email"
        autocomplete="email"
        size="lg"
        class="w-full"
        :disabled="loading"
      />
      <UInput
        v-model="form.password"
        type="password"
        placeholder="Пароль (мин. 8 символов)"
        autocomplete="new-password"
        size="lg"
        class="w-full"
        :disabled="loading"
      />
      <UButton
        type="submit"
        block
        size="lg"
        :loading="loading"
      >
        Далее
      </UButton>
    </UForm>

    <p class="text-center text-sm text-gray-400">
      Уже есть аккаунт?
      <NuxtLink to="/login" class="text-primary hover:underline">Войти</NuxtLink>
    </p>
  </div>
</template>
