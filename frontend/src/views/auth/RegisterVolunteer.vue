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
              d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
            />
          </svg>
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Регистрация волонтера
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
        
        <!-- Personal Information -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">
            Личная информация
          </h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label
                for="firstName"
                class="form-label"
              >Имя *</label>
              <input
                id="firstName"
                v-model="form.first_name"
                name="firstName"
                type="text"
                required
                class="form-input"
                :class="{ 'border-red-500': errors.first_name }"
                placeholder="Иван"
              >
              <div
                v-if="errors.first_name"
                class="form-error"
              >
                {{ errors.first_name }}
              </div>
            </div>
            
            <div>
              <label
                for="lastName"
                class="form-label"
              >Фамилия *</label>
              <input
                id="lastName"
                v-model="form.last_name"
                name="lastName"
                type="text"
                required
                class="form-input"
                :class="{ 'border-red-500': errors.last_name }"
                placeholder="Иванов"
              >
              <div
                v-if="errors.last_name"
                class="form-error"
              >
                {{ errors.last_name }}
              </div>
            </div>
          </div>
          
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
              for="phone"
              class="form-label"
            >Телефон</label>
            <input
              id="phone"
              v-model="form.phone"
              name="phone"
              type="tel"
              class="form-input"
              placeholder="+7 (777) 123-45-67"
            >
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label
                for="birthDate"
                class="form-label"
              >Дата рождения</label>
              <input
                id="birthDate"
                v-model="form.birth_date"
                name="birthDate"
                type="date"
                class="form-input"
              >
            </div>
            
            <div>
              <label
                for="gender"
                class="form-label"
              >Пол</label>
              <select
                id="gender"
                v-model="form.gender"
                name="gender"
                class="form-input"
              >
                <option value="">
                  Выберите
                </option>
                <option value="male">
                  Мужской
                </option>
                <option value="female">
                  Женский
                </option>
                <option value="other">
                  Другой
                </option>
              </select>
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

        <!-- Location -->
        <div class="space-y-4 border-t pt-6">
          <h3 class="text-lg font-medium text-gray-900">
            Местоположение
          </h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label
                for="city"
                class="form-label"
              >Город</label>
              <input
                id="city"
                v-model="form.city"
                name="city"
                type="text"
                class="form-input"
                placeholder="Алматы"
              >
            </div>
            
            <div>
              <label
                for="region"
                class="form-label"
              >Регион</label>
              <input
                id="region"
                v-model="form.region"
                name="region"
                type="text"
                class="form-input"
                placeholder="Алматинская область"
              >
            </div>
          </div>
        </div>

        <!-- Skills and Interests -->
        <div class="space-y-4 border-t pt-6">
          <h3 class="text-lg font-medium text-gray-900">
            Навыки и интересы
          </h3>
          
          <div>
            <label
              for="skills"
              class="form-label"
            >Навыки (через запятую)</label>
            <textarea
              id="skills"
              v-model="skillsText"
              name="skills"
              rows="3"
              class="form-input"
              placeholder="Например: программирование, дизайн, организация мероприятий"
            />
          </div>
          
          <div>
            <label
              for="interests"
              class="form-label"
            >Интересы (через запятую)</label>
            <textarea
              id="interests"
              v-model="interestsText"
              name="interests"
              rows="3"
              class="form-input"
              placeholder="Например: экология, образование, помощь животным"
            />
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
        </div>

        <div>
          <button
            type="submit"
            :disabled="authStore.isLoading || !form.agreeTerms"
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!authStore.isLoading">Зарегистрироваться</span>
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

      <!-- Organization Registration Link -->
      <div class="text-center">
        <p class="text-sm text-gray-600">
          Вы организация?
          <router-link
            to="/register/organization"
            class="font-medium text-primary-600 hover:text-primary-500"
          >
            Зарегистрируйтесь как организация
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { RegisterVolunteerRequest } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive<RegisterVolunteerRequest & { agreeTerms: boolean }>({
  email: '',
  password: '',
  password_confirm: '',
  first_name: '',
  last_name: '',
  phone: '',
  birth_date: '',
  gender: '',
  city: '',
  region: '',
  skills: [],
  interests: [],
  agreeTerms: false
})

const skillsText = computed({
  get: () => form.skills.join(', '),
  set: (value: string) => {
    form.skills = value.split(',').map(s => s.trim()).filter(s => s)
  }
})

const interestsText = computed({
  get: () => form.interests.join(', '),
  set: (value: string) => {
    form.interests = value.split(',').map(s => s.trim()).filter(s => s)
  }
})

const errors = reactive({
  email: '',
  password: '',
  password_confirm: '',
  first_name: '',
  last_name: ''
})

const validateForm = () => {
  errors.email = ''
  errors.password = ''
  errors.password_confirm = ''
  errors.first_name = ''
  errors.last_name = ''

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

  if (!form.first_name) {
    errors.first_name = 'Имя обязательно'
    return false
  }

  if (!form.last_name) {
    errors.last_name = 'Фамилия обязательна'
    return false
  }

  return true
}

const handleRegister = async () => {
  if (!validateForm()) {
    return
  }

  try {
    await authStore.registerVolunteer(form)
    router.push('/dashboard')
  } catch (error) {
    console.error('Registration error:', error)
  }
}
</script>
