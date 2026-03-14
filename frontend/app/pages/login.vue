<script setup lang="ts">
import { login } from '~/api/auth.api'

definePageMeta({
  layout: 'auth',
})

const config = useRuntimeConfig()
const toast = useToast()

const form = reactive({
  username: '',
  password: '',
})

const loading = ref(false)
const error = ref('')

async function onSubmit() {
  if (!form.username || !form.password) {
    error.value = 'Заполни все поля'
    return
  }
  error.value = ''
  loading.value = true
  try {
    const res = await login(config.public.apiBase as string, form)
    useAuthStore().setTokens(res.access_token, res.refresh_token)
    await navigateTo('/')
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Ошибка входа'
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
      <p class="text-gray-400 mt-1">Вход в аккаунт</p>
    </div>

    <UForm @submit="onSubmit" class="space-y-4 w-full">
      <UInput
        v-model="form.username"
        placeholder="Имя пользователя"
        autocomplete="username"
        size="lg"
        class="w-full"
        :disabled="loading"
      />
      <UInput
        v-model="form.password"
        type="password"
        placeholder="Пароль"
        autocomplete="current-password"
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
        Войти
      </UButton>
    </UForm>

    <p class="text-center text-sm text-gray-400">
      Нет аккаунта?
      <NuxtLink to="/register" class="text-primary hover:underline">Регистрация</NuxtLink>
    </p>
  </div>
</template>
