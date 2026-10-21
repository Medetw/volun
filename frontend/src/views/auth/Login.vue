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
              d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
            />
          </svg>
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Вход в аккаунт
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Или
          <router-link
            to="/register/volunteer"
            class="font-medium text-primary-600 hover:text-primary-500"
          >
            зарегистрируйтесь
          </router-link>
        </p>
      </div>
      
      <form
        class="mt-8 space-y-6"
        @submit.prevent="handleLogin"
      >
        <div
          v-if="authStore.error"
          class="bg-red-50 border border-red-200 rounded-md p-4"
        >
          <div class="text-sm text-red-600">
            {{ authStore.error }}
          </div>
        </div>
        
        <div class="space-y-4">
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
            <label
              for="password"
              class="form-label"
            >Пароль</label>
            <div class="relative">
              <input
                id="password"
                v-model="form.password"
                name="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                required
                class="form-input pr-10"
                :class="{ 'border-red-500': errors.password }"
                placeholder="••••••••"
              >
              <button
                type="button"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
                @click="showPassword = !showPassword"
              >
                <svg
                  v-if="showPassword"
                  class="h-5 w-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                  />
                </svg>
                <svg
                  v-else
                  class="h-5 w-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
              </button>
            </div>
            <div
              v-if="errors.password"
              class="form-error"
            >
              {{ errors.password }}
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember-me"
              v-model="form.rememberMe"
              name="remember-me"
              type="checkbox"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            >
            <label
              for="remember-me"
              class="ml-2 block text-sm text-gray-900"
            >
              Запомнить меня
            </label>
          </div>

          <div class="text-sm">
            <router-link
              to="/forgot-password"
              class="font-medium text-primary-600 hover:text-primary-500"
            >
              Забыли пароль?
            </router-link>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="authStore.isLoading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!authStore.isLoading">Войти</span>
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
              Вход...
            </span>
          </button>
        </div>
      </form>

      <!-- Registration links -->
      <div class="mt-6">
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300" />
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-gray-50 text-gray-500">Или войдите как</span>
          </div>
        </div>

        <div class="mt-6 grid grid-cols-2 gap-3">
          <router-link
            to="/register/volunteer"
            class="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
          >
            Волонтер
          </router-link>
          <router-link
            to="/register/organization"
            class="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
          >
            Организация
          </router-link>
        </div>
      </div>

      <!-- Quick test credentials / secret shortcut buttons for testing -->
      <div class="mt-6 pt-4 border-t border-dashed border-gray-200">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Тестовый доступ (1-клик)</span>
          <span class="text-[11px] text-gray-400">для заказчика / QA</span>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
          <button
            type="button"
            class="text-xs py-1.5 px-2 bg-gray-100 hover:bg-primary-50 hover:text-primary-700 text-gray-700 rounded border border-gray-200 transition-colors text-left"
            @click="fillTestAccount('test_admin@volun.test', 'Admin@12345')"
          >
            👑 <b>Админ</b>
          </button>
          <button
            type="button"
            class="text-xs py-1.5 px-2 bg-gray-100 hover:bg-primary-50 hover:text-primary-700 text-gray-700 rounded border border-gray-200 transition-colors text-left"
            @click="fillTestAccount('test_moderator@volun.test', 'Mod@12345')"
          >
            🛡 <b>Модератор</b>
          </button>
          <button
            type="button"
            class="text-xs py-1.5 px-2 bg-gray-100 hover:bg-primary-50 hover:text-primary-700 text-gray-700 rounded border border-gray-200 transition-colors text-left"
            @click="fillTestAccount('test_org@volun.test', 'Org@12345')"
          >
            🏢 <b>Организация</b>
          </button>
          <button
            type="button"
            class="text-xs py-1.5 px-2 bg-gray-100 hover:bg-primary-50 hover:text-primary-700 text-gray-700 rounded border border-gray-200 transition-colors text-left"
            @click="fillTestAccount('test_volunteer@volun.test', 'Vol@12345')"
          >
            🙋 <b>Волонтёр 1</b>
          </button>
          <button
            type="button"
            class="text-xs py-1.5 px-2 bg-gray-100 hover:bg-primary-50 hover:text-primary-700 text-gray-700 rounded border border-gray-200 transition-colors text-left"
            @click="fillTestAccount('test_volunteer2@volun.test', 'Vol@12345')"
          >
            🙋 <b>Волонтёр 2</b>
          </button>
          <button
            type="button"
            class="text-xs py-1.5 px-2 bg-gray-100 hover:bg-primary-50 hover:text-primary-700 text-gray-700 rounded border border-gray-200 transition-colors text-left"
            @click="fillTestAccount('test_mod_limited@volun.test', 'Mod@12345')"
          >
            🔒 <b>Мод (огран.)</b>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = reactive({
  email: '',
  password: '',
  rememberMe: false
})

const showPassword = ref(false)
const errors = reactive({
  email: '',
  password: ''
})

onMounted(() => {
  // Pre-fill email if provided in query params
  if (route.query.email) {
    form.email = route.query.email as string
  }
})

const fillTestAccount = (email: string, pass: string) => {
  form.email = email
  form.password = pass
  errors.email = ''
  errors.password = ''
}

const validateForm = () => {
  errors.email = ''
  errors.password = ''

  if (!form.email) {
    errors.email = 'Email обязателен'
    return false
  }

  if (!/\S+@\S+\.\S+/.test(form.email)) {
    errors.email = 'Email невалиден'
    return false
  }

  if (!form.password) {
    errors.password = 'Пароль обязателен'
    return false
  }

  if (form.password.length < 6) {
    errors.password = 'Пароль должен содержать минимум 6 символов'
    return false
  }

  return true
}

const handleLogin = async () => {
  if (!validateForm()) {
    return
  }

  try {
    await authStore.login({
      email: form.email,
      password: form.password
    })

    // Redirect to intended page or dashboard
    const redirect = route.query.redirect as string
    router.push(redirect || '/dashboard')
  } catch (error) {
    console.error('Login error:', error)
  }
}
</script>
