<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full text-center">
      <div class="mb-8">
        <h1 class="text-9xl font-bold text-primary-600">
          404
        </h1>
        <h2 class="mt-4 text-3xl font-bold text-gray-900">
          Страница не найдена
        </h2>
        <p class="mt-2 text-gray-600">
          Извините, мы не смогли найти страницу, которую вы ищете.
        </p>
      </div>
      
      <div class="space-y-4">
        <router-link
          to="/"
          class="btn btn-primary w-full"
        >
          На главную
        </router-link>
        
        <router-link
          to="/projects"
          class="btn btn-outline w-full"
        >
          Найти проекты
        </router-link>
      </div>
      
      <div class="mt-8">
        <p class="text-sm text-gray-500">
          Если вы считаете, что это ошибка, пожалуйста, свяжитесь с нами.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 404 page component
</script>
