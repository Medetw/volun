<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-2xl w-full space-y-8">
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
              d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
            />
          </svg>
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Регистрация организации
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Уже есть аккаунт?
          <router-link
            to="/login"
            class="font-medium text-primary-600 hover:text-primary-500"
          >
            Войдите
          </router-link>
        </p>
      </div>
      
      <form
        class="mt-8 space-y-6"
        @submit.prevent="handleRegister"
      >
        <div
          v-if="authStore.error"
          class="bg-red-50 border border-red-200 rounded-md p-4"
        >
          <div class="text-sm text-red-600">
            {{ authStore.error }}
          </div>
        </div>
        
        <!-- Organization Information -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">
            Информация об организации
          </h3>
          
          <div>
            <label
              for="name"
              class="form-label"
            >Название организации *</label>
            <input
              id="name"
              v-model="form.name"
              name="name"
              type="text"
              required
              class="form-input"
              :class="{ 'border-red-500': errors.name }"
              placeholder="ООО 'Добрые дела'"
            >
            <div
              v-if="errors.name"
              class="form-error"
            >
              {{ errors.name }}
            </div>
          </div>
          
          <div>
            <label
              for="organizationType"
              class="form-label"
            >Тип организации *</label>
            <select
              id="organizationType"
              v-model="form.organization_type"
              name="organizationType"
              required
              class="form-input"
              :class="{ 'border-red-500': errors.organization_type }"
            >
              <option value="">
                Выберите тип
              </option>
              <option value="ngo">
                НКО
              </option>
              <option value="foundation">
                Фонд
              </option>
              <option value="association">
                Ассоциация
              </option>
              <option value="corporate">
                Корпорация
              </option>
              <option value="government">
                Государственная
              </option>
              <option value="educational">
                Образовательная
              </option>
              <option value="religious">
                Религиозная
              </option>
              <option value="other">
                Другое
              </option>
            </select>
            <div
              v-if="errors.organization_type"
              class="form-error"
            >
              {{ errors.organization_type }}
            </div>
          </div>
          
          <div>
            <label
              for="description"
              class="form-label"
            >Описание деятельности</label>
            <textarea
              id="description"
              v-model="form.description"
              name="description"
              rows="4"
              class="form-input"
              placeholder="Опишите основную деятельность вашей организации..."
            />
          </div>
          
          <div>
            <label
              for="website"
              class="form-label"
            >Веб-сайт</label>
            <input
              id="website"
              v-model="form.website"
              name="website"
              type="url"
              class="form-input"
              placeholder="https://example.com"
            >
          </div>
        </div>

        <!-- Contact Information -->
        <div class="space-y-4 border-t pt-6">
          <h3 class="text-lg font-medium text-gray-900">
            Контактная информация
          </h3>
          
          <div>
            <label
              for="email"
              class="form-label"
            >Email *</label>
            <input
              id="email"
              v-model="form.email"
              name="email"
              type="email"
              autocomplete="email"
              required
              class="form-input"
              :class="{ 'border-red-500': errors.email }"
              placeholder="org@example.com"
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
              for="phone"
              class="form-label"
            >Телефон *</label>
            <input
              id="phone"
              v-model="form.phone"
              name="phone"
              type="tel"
              required
              class="form-input"
              :class="{ 'border-red-500': errors.phone }"
              placeholder="+7 (777) 123-45-67"
            >
            <div
              v-if="errors.phone"
              class="form-error"
            >
              {{ errors.phone }}
            </div>
          </div>
          
          <div>
            <label
              for="address"
              class="form-label"
            >Юридический адрес *</label>
            <input
              id="address"
              v-model="form.address"
              name="address"
              type="text"
              required
              class="form-input"
              :class="{ 'border-red-500': errors.address }"
              placeholder="г. Алматы, ул. Абая 123, офис 456"
            >
            <div
              v-if="errors.address"
              class="form-error"
            >
              {{ errors.address }}
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label
                for="city"
                class="form-label"
              >Город *</label>
              <input
                id="city"
                v-model="form.city"
                name="city"
                type="text"
                required
                class="form-input"
                :class="{ 'border-red-500': errors.city }"
                placeholder="Алматы"
              >
              <div
                v-if="errors.city"
                class="form-error"
              >
                {{ errors.city }}
              </div>
            </div>
            
            <div>
              <label
                for="region"
                class="form-label"
              >Регион *</label>
              <input
                id="region"
                v-model="form.region"
                name="region"
                type="text"
                required
                class="form-input"
                :class="{ 'border-red-500': errors.region }"
                placeholder="Алматинская область"
              >
              <div
                v-if="errors.region"
                class="form-error"
              >
                {{ errors.region }}
              </div>
            </div>
          </div>
        </div>

        <!-- Account Information -->
        <div class="space-y-4 border-t pt-6">
          <h3 class="text-lg font-medium text-gray-900">
            Аккаунт
          </h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label
                for="password"
                class="form-label"
              >Пароль *</label>
              <input
                id="password"
                v-model="form.password"
                name="password"
                type="password"
                required
                class="form-input"
                :class="{ 'border-red-500': errors.password }"
                placeholder="••••••••"
              >
              <div
                v-if="errors.password"
                class="form-error"
              >
                {{ errors.password }}
              </div>
            </div>
            
            <div>
              <label
                for="passwordConfirm"
                class="form-label"
              >Подтвердите пароль *</label>
              <input
                id="passwordConfirm"
                v-model="form.password_confirm"
                name="passwordConfirm"
                type="password"
                required
                class="form-input"
                :class="{ 'border-red-500': errors.password_confirm }"
                placeholder="••••••••"
              >
              <div
                v-if="errors.password_confirm"
                class="form-error"
              >
                {{ errors.password_confirm }}
              </div>
            </div>
          </div>
        </div>

        <!-- Documents -->
        <div class="space-y-4 border-t pt-6">
          <h3 class="text-lg font-medium text-gray-900">
            Документы
          </h3>
          
          <div class="bg-blue-50 border border-blue-200 rounded-md p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg
                  class="h-5 w-5 text-blue-400"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fill-rule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                    clip-rule="evenodd"
                  />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-blue-800">
                  Верификация организации
                </h3>
                <div class="mt-2 text-sm text-blue-700">
                  <p>После регистрации вам потребуется предоставить документы для верификации организации:</p>
                  <ul class="list-disc list-inside mt-2 space-y-1">
                    <li>Свидетельство о государственной регистрации</li>
                    <li>Устав организации</li>
                    <li>Документ, подтверждающий полномочия представителя</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Terms -->
        <div class="space-y-4 border-t pt-6">
          <div class="flex items-center">
            <input
              id="agreeTerms"
              v-model="form.agreeTerms"
              name="agreeTerms"
              type="checkbox"
              required
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            >
            <label
              for="agreeTerms"
              class="ml-2 block text-sm text-gray-900"
            >
              Я согласен с <a
                href="#"
                class="text-primary-600 hover:text-primary-500"
              >условиями использования</a> и 
              <a
                href="#"
                class="text-primary-600 hover:text-primary-500"
              >политикой конфиденциальности</a>
            </label>
          </div>
          
          <div class="flex items-center">
            <input
              id="agreeVerification"
              v-model="form.agreeVerification"
              name="agreeVerification"
              type="checkbox"
              required
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            >
            <label
              for="agreeVerification"
              class="ml-2 block text-sm text-gray-900"
            >
              Я понимаю, что потребуется верификация документов
            </label>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="authStore.isLoading || !form.agreeTerms || !form.agreeVerification"
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!authStore.isLoading">Зарегистрировать организацию</span>
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
              Регистрация...
            </span>
          </button>
        </div>
      </form>

      <!-- Volunteer Registration Link -->
      <div class="text-center">
        <p class="text-sm text-gray-600">
          Вы волонтер?
          <router-link
            to="/register/volunteer"
            class="font-medium text-primary-600 hover:text-primary-500"
          >
            Зарегистрируйтесь как волонтер
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { RegisterOrganizationRequest } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive<RegisterOrganizationRequest & { 
  agreeTerms: boolean
  agreeVerification: boolean 
}>({
  email: '',
  password: '',
  password_confirm: '',
  name: '',
  organization_type: '',
  description: '',
  website: '',
  phone: '',
  address: '',
  city: '',
  region: '',
  agreeTerms: false,
  agreeVerification: false
})

const errors = reactive({
  email: '',
  password: '',
  password_confirm: '',
  name: '',
  organization_type: '',
  phone: '',
  address: '',
  city: '',
  region: ''
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

  if (!form.password) {
    errors.password = 'Пароль обязателен'
    return false
  }

  if (form.password.length < 8) {
    errors.password = 'Пароль должен содержать минимум 8 символов'
    return false
  }

  if (!form.password_confirm) {
    errors.password_confirm = 'Подтвердите пароль'
    return false
  }

  if (form.password !== form.password_confirm) {
    errors.password_confirm = 'Пароли не совпадают'
    return false
  }

  if (!form.name) {
    errors.name = 'Название организации обязательно'
    return false
  }

  if (!form.organization_type) {
    errors.organization_type = 'Тип организации обязателен'
    return false
  }

  if (!form.phone) {
    errors.phone = 'Телефон обязателен'
    return false
  }

  if (!form.address) {
    errors.address = 'Адрес обязателен'
    return false
  }

  if (!form.city) {
    errors.city = 'Город обязателен'
    return false
  }

  if (!form.region) {
    errors.region = 'Регион обязателен'
    return false
  }

  return true
}

const handleRegister = async () => {
  if (!validateForm()) {
    return
  }

  try {
    await authStore.registerOrganization(form)
    router.push('/dashboard')
  } catch (error) {
    console.error('Registration error:', error)
  }
}
</script>
