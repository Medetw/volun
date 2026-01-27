<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <div class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100">
          <svg class="h-8 w-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 012 8.242m3.12-1.641a1 1 0 00.819.311l2.841 2.842a1 1 0 001.415 0l2.841-2.842a1 1 0 00.819-.311l2.842-2.841a1 1 0 000-1.415l-2.842-2.841a1 1 0 00-.819-.311l-2.841 2.842a1 1 0 01-1.415 0l-2.841-2.842a1 1 0 00-.819-.311l-2.842 2.842a1 1 0 000 1.415l2.842 2.841a1 1 0 00.819.311l2.841-2.842a1 1 0 011.415 0z" />
          </svg>
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Сброс пароля
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Введите код из письма и новый пароль
        </p>
      </div>
      
      <!-- Success Message -->
      <div v-if="successMessage" class="bg-green-50 border border-green-200 rounded-md p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-green-800">
              Пароль успешно изменен
            </h3>
            <div class="mt-2 text-sm text-green-700">
              <p>{{ successMessage }}</p>
            </div>
            <div class="mt-4">
              <router-link to="/login" class="btn btn-primary">
                Войти в аккаунт
              </router-link>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Error Message -->
      <div v-if="errorMessage" class="bg-red-50 border border-red-200 rounded-md p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
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
      
      <form v-if="!successMessage" class="mt-8 space-y-6" @submit.prevent="handleResetPassword">
        <div>
          <label for="email" class="form-label">Email</label>
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
          />
          <div v-if="errors.email" class="form-error">{{ errors.email }}</div>
        </div>

        <div>
          <label for="resetCode" class="form-label">Код сброса</label>
          <input
            id="resetCode"
            v-model="form.reset_code"
            name="resetCode"
            type="text"
            required
            maxlength="6"
            class="form-input text-center text-lg font-mono"
            :class="{ 'border-red-500': errors.reset_code }"
            placeholder="123456"
          />
          <div v-if="errors.reset_code" class="form-error">{{ errors.reset_code }}</div>
          <p class="mt-1 text-sm text-gray-500">
            Введите 6-значный код из письма
          </p>
        </div>

        <div class="space-y-4">
          <div>
            <label for="newPassword" class="form-label">Новый пароль</label>
            <input
              id="newPassword"
              v-model="form.new_password"
              name="newPassword"
              type="password"
              required
              class="form-input"
              :class="{ 'border-red-500': errors.new_password }"
              placeholder="••••••••"
            />
            <div v-if="errors.new_password" class="form-error">{{ errors.new_password }}</div>
          </div>
          
          <div>
            <label for="confirmPassword" class="form-label">Подтвердите новый пароль</label>
            <input
              id="confirmPassword"
              v-model="form.new_password_confirm"
              name="confirmPassword"
              type="password"
              required
              class="form-input"
              :class="{ 'border-red-500': errors.new_password_confirm }"
              placeholder="••••••••"
            />
            <div v-if="errors.new_password_confirm" class="form-error">{{ errors.new_password_confirm }}</div>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!isLoading">Сбросить пароль</span>
            <span v-else class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Сброс...
            </span>
          </button>
        </div>

        <div class="text-center space-y-2">
          <router-link to="/forgot-password" class="btn btn-ghost text-sm">
            ← Запросить код еще раз
          </router-link>
          <br>
          <router-link to="/login" class="btn btn-ghost text-sm">
            ← Вернуться к входу
          </router-link>
        </div>
      </form>
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
  reset_code: '',
  new_password: '',
  new_password_confirm: ''
})

const errors = reactive({
  email: '',
  reset_code: '',
  new_password: '',
  new_password_confirm: ''
})

const isLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

onMounted(() => {
  // Pre-fill email if provided in query params
  if (route.query.email) {
    form.email = route.query.email as string
  }
  
  // Pre-fill reset code if provided in query params
  if (route.query.code) {
    form.reset_code = route.query.code as string
  }
})

const validateForm = () => {
  // Reset errors
  Object.keys(errors).forEach(key => {
    errors[key as keyof typeof errors] = ''
  })

  if (!form.email) {
    errors.email = 'Email обязателен'
    return false
  }

  if (!/\S+@\S+\.\S+/.test(form.email)) {
    errors.email = 'Email невалиден'
    return false
  }

  if (!form.reset_code) {
    errors.reset_code = 'Код обязателен'
    return false
  }

  if (form.reset_code.length !== 6) {
    errors.reset_code = 'Код должен содержать 6 цифр'
    return false
  }

  if (!form.new_password) {
    errors.new_password = 'Новый пароль обязателен'
    return false
  }

  if (form.new_password.length < 8) {
    errors.new_password = 'Пароль должен содержать минимум 8 символов'
    return false
  }

  if (!form.new_password_confirm) {
    errors.new_password_confirm = 'Подтвердите новый пароль'
    return false
  }

  if (form.new_password !== form.new_password_confirm) {
    errors.new_password_confirm = 'Пароли не совпадают'
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
    
    const response = await authStore.confirmPasswordReset({
      email: form.email,
      reset_code: form.reset_code,
      new_password: form.new_password,
      new_password_confirm: form.new_password_confirm
    })
    
    successMessage.value = response.message
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || 'Произошла ошибка. Проверьте код и попробуйте еще раз.'
  } finally {
    isLoading.value = false
  }
}
</script>
