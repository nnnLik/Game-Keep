<script setup lang="ts">
function logout() {
  useAuthStore().clearTokens()
  navigateTo('/login')
}
</script>

<template>
  <div class="min-h-screen bg-gray-900 flex">
    <!-- Сайдбар без границы -->
    <aside class="w-96 shrink-0 pl-40 pr-8 py-12 flex flex-col">
      <div class="mb-16 sidebar-title">
        <h1 class="text-5xl font-bold text-white tracking-tight leading-tight">
          Game&Keep
        </h1>
        <p class="text-2x font-semibold text-gray-400 mt-2">
          Твой игровой трекер
        </p>
      </div>
      <nav class="flex flex-col gap-2 flex-1">
        <NuxtLink
          to="/"
          class="flex items-center gap-4 rounded-full px-5 py-4 text-lg text-white hover:bg-gray-800/50 transition-colors"
          active-class="!bg-gray-800"
        >
          <Icon name="lucide:user" class="size-7 shrink-0" />
          Профиль
        </NuxtLink>
        <NuxtLink
          to="/feed"
          class="flex items-center gap-4 rounded-full px-5 py-4 text-lg text-white hover:bg-gray-800/50 transition-colors"
          active-class="!bg-gray-800"
        >
          <Icon name="lucide:scroll-text" class="size-7 shrink-0" />
          Лента
        </NuxtLink>
        <NuxtLink
          to="/collectors"
          class="flex items-center gap-4 rounded-full px-5 py-4 text-lg text-white hover:bg-gray-800/50 transition-colors"
          active-class="!bg-gray-800"
        >
          <Icon name="lucide:users" class="size-7 shrink-0" />
          Коллекционеры
        </NuxtLink>
      </nav>
      <button
        type="button"
        class="flex items-center gap-4 rounded-full px-5 py-4 text-lg text-white hover:bg-gray-800/50 transition-colors mt-auto"
        @click="logout"
      >
        <Icon name="lucide:log-out" class="size-7 shrink-0" />
        Выйти
      </button>
    </aside>

    <!-- Контент -->
    <main class="flex-1 min-w-0">
      <div class="mx-auto w-full max-w-4xl px-6 py-10">
        <slot />
      </div>
    </main>
  </div>
</template>
