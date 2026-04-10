<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <div class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100">
          <svg
            class="h-8 w-8 text-primary-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 7a2 2 0 012 2m4 0a6 6 0 012 8.242m3.12-1.641a1 1 0 00.819.311l2.841 2.842a1 1 0 001.415 0l2.841-2.842a1 1 0 00.819-.311l2.842-2.841a1 1 0 000-1.415l-2.842-2.841a1 1 0 00-.819-.311l-2.841 2.842a1 1 0 01-1.415 0l-2.841-2.842a1 1 0 00-.819-.311l-2.842 2.842a1 1 0 000 1.415l2.842 2.841a1 1 0 00.819.311l2.841-2.842a1 1 0 011.415 0z"
            />
          </svg>
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Восстановление пароля
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Введите ваш email, и мы отправим вам код для сброса пароля
        </p>
      </div>
      
      <!-- Success Message -->
      <div
        v-if="successMessage"
        class="bg-green-50 border border-green-200 rounded-md p-4"
      >
        <div class="flex">
          <div class="flex-shrink-0">
            <svg
              class="h-5 w-5 text-green-400"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fill-rule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clip-rule="evenodd"
              />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-green-800">
              Код отправлен
            </h3>
            <div class="mt-2 text-sm text-green-700">
              <p>{{ successMessage }}</p>
            </div>
            <div class="mt-4">
              <router-link
                to="/reset-password"
                class="btn btn-primary"
              >
                Ввести код
              </router-link>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Error Message -->
      <div
        v-if="errorMessage"
        class="bg-red-50 border border-red-200 rounded-md p-4"
      >
        <div class="flex">
          <div class="flex-shrink-0">
            <svg
              class="h-5 w-5 text-red-400"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fill-rule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clip-rule="evenodd"
              />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">
              Ошибка
            </h3>
            <div class="mt-2 text-sm text-red-700">
              <p>{{ errorMessage }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <form
        v-if="!successMessage"
        class="mt-8 space-y-6"
        @submit.prevent="handleResetPassword"
      >
        <div>
          <label
            for="email"
            class="form-label"
          >Email адрес</label>
          <input
            id="email"
            v-model="form.email"
            name="email"
            type="email"
            autocomplete="email"
            required
            class="form-input"
            :class="{ 'border-red-500': errors.email }"
            placeholder="your@email.com"
          >
          <div
            v-if="errors.email"
            class="form-error"
          >
            {{ errors.email }}
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!isLoading">Отправить код</span>
            <span
              v-else
              class="flex items-center"
            >
              <svg
                class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                />
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Отправка...
            </span>
          </button>
        </div>

        <div class="text-center">
          <router-link
            to="/login"
            class="btn btn-ghost"
          >
            ← Вернуться к входу
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const form = reactive({
  email: ''
})

const errors = reactive({
  email: ''
})

const isLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const resetCode = ref('')

const validateForm = () => {
  errors.email = ''

  if (!form.email) {
    errors.email = 'Email обязателен'
    return false
  }

  if (!/\S+@\S+\.\S+/.test(form.email)) {
    errors.email = 'Email невалиден'
    return false
  }

  return true
}

const handleResetPassword = async () => {
  if (!validateForm()) {
    return
  }

  try {
    isLoading.value = true
    errorMessage.value = ''
    
    const response = await authStore.requestPasswordReset(form.email)
    successMessage.value = response.message
    
    // В development режиме показываем код
    if (response.reset_code) {
      resetCode.value = response.reset_code
    }
  } catch (error: any) {
    errorMessage.value = error.response?.data?.email?.[0] || 'Произошла ошибка. Попробуйте еще раз.'
  } finally {
    isLoading.value = false
  }
}
</script>
