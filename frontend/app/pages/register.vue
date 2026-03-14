<script setup lang="ts">
import { register } from '~/api/auth.api'

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
    const res = await register(config.public.apiBase as string, form)
    useAuthStore().setTokens(res.access_token, res.refresh_token)
    await navigateTo('/')
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Ошибка регистрации'
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
        Зарегистрироваться
      </UButton>
    </UForm>

    <p class="text-center text-sm text-gray-400">
      Уже есть аккаунт?
      <NuxtLink to="/login" class="text-primary hover:underline">Войти</NuxtLink>
    </p>
  </div>
</template>
