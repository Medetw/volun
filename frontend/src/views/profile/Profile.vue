<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="container-custom max-w-4xl">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">
          Профиль
        </h1>
        <p class="text-gray-600 mt-2">
          Управление личной информацией
        </p>
      </div>

      <!-- Loading State -->
      <div
        v-if="loading"
        class="flex items-center justify-center py-20"
      >
        <div class="loading-spinner w-8 h-8 mr-3" />
        <span class="text-gray-600">Загрузка профиля...</span>
      </div>

      <!-- Profile Content -->
      <div
        v-else
        class="space-y-6"
      >
        <!-- Profile Header -->
        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center space-x-6">
            <div class="relative">
              <div class="w-24 h-24 bg-gray-300 rounded-full flex items-center justify-center overflow-hidden">
                <img
                  v-if="authStore.user?.avatar"
                  :src="authStore.user.avatar"
                  alt="Аватар"
                  class="w-full h-full object-cover"
                >
                <span
                  v-else
                  class="text-2xl font-medium text-gray-700"
                >
                  {{ getUserInitials() }}
                </span>
              </div>
              <button
                class="absolute bottom-0 right-0 bg-primary-600 text-white p-2 rounded-full hover:bg-primary-700"
                @click="triggerAvatarUpload"
              >
                <svg
                  class="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </button>
              <input
                ref="avatarInput"
                type="file"
                accept="image/*"
                class="hidden"
                @change="handleAvatarUpload"
              >
            </div>
            
            <div class="flex-1">
              <h2 class="text-2xl font-bold text-gray-900">
                {{ getUserDisplayName() }}
              </h2>
              <p class="text-gray-600">
                {{ getUserEmail() }}
              </p>
              <span :class="getRoleBadgeClass()">
                {{ getRoleDisplay() }}
              </span>
            </div>
          </div>
        </div>

        <!-- Profile Form -->
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-xl font-semibold text-gray-900 mb-6">
            Личная информация
          </h3>
          
          <!-- Success Message -->
          <div
            v-if="successMessage"
            class="bg-green-50 border border-green-200 rounded-md p-4 mb-6"
          >
            <div class="text-sm text-green-600">
              {{ successMessage }}
            </div>
          </div>

          <!-- Error Message -->
          <div
            v-if="errorMessage"
            class="bg-red-50 border border-red-200 rounded-md p-4 mb-6"
          >
            <div class="text-sm text-red-600">
              {{ errorMessage }}
            </div>
          </div>

          <form
            class="space-y-6"
            @submit.prevent="handleUpdateProfile"
          >
            <!-- Basic Information -->
            <div class="space-y-4">
              <h4 class="text-lg font-medium text-gray-900">
                Основная информация
              </h4>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="form-label">Имя</label>
                  <input
                    v-model="form.first_name"
                    type="text"
                    class="form-input"
                    placeholder="Введите имя"
                  >
                </div>
                
                <div>
                  <label class="form-label">Фамилия</label>
                  <input
                    v-model="form.last_name"
                    type="text"
                    class="form-input"
                    placeholder="Введите фамилию"
                  >
                </div>
              </div>

              <div>
                <label class="form-label">Email</label>
                <input
                  v-model="form.email"
                  type="email"
                  class="form-input"
                  placeholder="your@email.com"
                >
              </div>

              <div>
                <label class="form-label">Телефон</label>
                <input
                  v-model="form.phone"
                  type="tel"
                  class="form-input"
                  placeholder="+7 (777) 123-45-67"
                >
              </div>
            </div>

            <!-- Volunteer Specific Fields -->
            <div
              v-if="authStore.isVolunteer"
              class="space-y-4 border-t pt-6"
            >
              <h4 class="text-lg font-medium text-gray-900">
                Информация о волонтере
              </h4>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="form-label">Дата рождения</label>
                  <input
                    v-model="form.birth_date"
                    type="date"
                    class="form-input"
                  >
                </div>
                
                <div>
                  <label class="form-label">Пол</label>
                  <select
                    v-model="form.gender"
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

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="form-label">Город</label>
                  <input
                    v-model="form.city"
                    type="text"
                    class="form-input"
                    placeholder="Алматы"
                  >
                </div>
                
                <div>
                  <label class="form-label">Регион</label>
                  <input
                    v-model="form.region"
                    type="text"
                    class="form-input"
                    placeholder="Алматинская область"
                  >
                </div>
              </div>

              <div>
                <label class="form-label">Навыки (через запятую)</label>
                <textarea
                  v-model="skillsText"
                  rows="3"
                  class="form-input"
                  placeholder="Например: программирование, дизайн, организация мероприятий"
                />
              </div>

              <div>
                <label class="form-label">Интересы (через запятую)</label>
                <textarea
                  v-model="interestsText"
                  rows="3"
                  class="form-input"
                  placeholder="Например: экология, образование, помощь животным"
                />
              </div>
            </div>

            <!-- Organization Specific Fields -->
            <div
              v-if="authStore.isOrganization"
              class="space-y-4 border-t pt-6"
            >
              <h4 class="text-lg font-medium text-gray-900">
                Информация об организации
              </h4>
              
              <div>
                <label class="form-label">Название организации</label>
                <input
                  v-model="form.organization_name"
                  type="text"
                  class="form-input"
                  placeholder="ООО 'Добрые дела'"
                >
              </div>

              <div>
                <label class="form-label">Тип организации</label>
                <select
                  v-model="form.organization_type"
                  class="form-input"
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
              </div>

              <div>
                <label class="form-label">Описание деятельности</label>
                <textarea
                  v-model="form.description"
                  rows="4"
                  class="form-input"
                  placeholder="Опишите основную деятельность вашей организации..."
                />
              </div>

              <div>
                <label class="form-label">Веб-сайт</label>
                <input
                  v-model="form.website"
                  type="url"
                  class="form-input"
                  placeholder="https://example.com"
                >
              </div>

              <div>
                <label class="form-label">Юридический адрес</label>
                <input
                  v-model="form.address"
                  type="text"
                  class="form-input"
                  placeholder="г. Алматы, ул. Абая 123, офис 456"
                >
              </div>
            </div>

            <!-- Actions -->
            <div class="flex justify-end space-x-4 border-t pt-6">
              <button
                type="button"
                class="btn btn-outline"
                @click="resetForm"
              >
                Отмена
              </button>
              <button
                type="submit"
                :disabled="submitting"
                class="btn btn-primary"
              >
                {{ submitting ? 'Сохранение...' : 'Сохранить изменения' }}
              </button>
            </div>
          </form>
        </div>

        <!-- Change Password -->
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-xl font-semibold text-gray-900 mb-6">
            Изменение пароля
          </h3>
          
          <form
            class="space-y-4"
            @submit.prevent="handleChangePassword"
          >
            <div>
              <label class="form-label">Текущий пароль</label>
              <input
                v-model="passwordForm.old_password"
                type="password"
                class="form-input"
                placeholder="••••••••"
                required
              >
            </div>

            <div>
              <label class="form-label">Новый пароль</label>
              <input
                v-model="passwordForm.new_password"
                type="password"
                class="form-input"
                placeholder="••••••••"
                required
              >
            </div>

            <div>
              <label class="form-label">Подтвердите новый пароль</label>
              <input
                v-model="passwordForm.new_password_confirm"
                type="password"
                class="form-input"
                placeholder="••••••••"
                required
              >
            </div>

            <div class="flex justify-end">
              <button
                type="submit"
                :disabled="changingPassword"
                class="btn btn-primary"
              >
                {{ changingPassword ? 'Изменение...' : 'Изменить пароль' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import apiService from '@/services/api'
import type { User } from '@/types/api'

const authStore = useAuthStore()
const avatarInput = ref<HTMLInputElement | null>(null)

const loading = ref(true)
const submitting = ref(false)
const changingPassword = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  birth_date: '',
  gender: '',
  city: '',
  region: '',
  skills: [] as string[],
  interests: [] as string[],
  organization_name: '',
  organization_type: '',
  description: '',
  website: '',
  address: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  new_password_confirm: ''
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

onMounted(async () => {
  await loadProfile()
})

const loadProfile = async () => {
  try {
    loading.value = true
    const user = authStore.user
    
    if (user) {
      // Basic info
      form.email = user.email || ''
      form.phone = user.phone || ''

      // Volunteer profile
      if (user.volunteer_profile) {
        const profile = user.volunteer_profile
        form.first_name = profile.first_name || ''
        form.last_name = profile.last_name || ''
        form.birth_date = profile.birth_date || ''
        form.gender = profile.gender || ''
        form.city = profile.city || ''
        form.region = profile.region || ''
        form.skills = profile.skills || []
        form.interests = profile.interests || []
      }
      
      // Organization profile
      if (user.organization_profile) {
        const profile = user.organization_profile
        form.organization_name = profile.name || ''
        form.organization_type = profile.organization_type || ''
        form.description = profile.description || ''
        form.website = profile.website || ''
        form.address = profile.address || ''
        form.city = profile.city || ''
        form.region = profile.region || ''
      }
    }
  } catch (error) {
    console.error('Failed to load profile:', error)
  } finally {
    loading.value = false
  }
}

const handleUpdateProfile = async () => {
  try {
    submitting.value = true
    successMessage.value = ''
    errorMessage.value = ''
    
    await authStore.updateProfile(form)
    successMessage.value = 'Профиль успешно обновлен!'
    
    // Scroll to top
    window.scrollTo(0, 0)
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || 'Ошибка обновления профиля'
  } finally {
    submitting.value = false
  }
}

const handleChangePassword = async () => {
  if (passwordForm.new_password !== passwordForm.new_password_confirm) {
    errorMessage.value = 'Пароли не совпадают'
    return
  }
  
  try {
    changingPassword.value = true
    successMessage.value = ''
    errorMessage.value = ''
    
    await authStore.changePassword(passwordForm)
    successMessage.value = 'Пароль успешно изменен!'
    
    // Reset form
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.new_password_confirm = ''
    
    // Scroll to top
    window.scrollTo(0, 0)
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || 'Ошибка изменения пароля'
  } finally {
    changingPassword.value = false
  }
}

const resetForm = () => {
  loadProfile()
}

const triggerAvatarUpload = () => {
  avatarInput.value?.click()
}

const handleAvatarUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  try {
    await apiService.uploadAvatar(file)
    await authStore.fetchCurrentUser()
    successMessage.value = 'Аватар обновлён'
    setTimeout(() => { successMessage.value = '' }, 3000)
  } catch (error) {
    errorMessage.value = 'Ошибка загрузки аватара'
    setTimeout(() => { errorMessage.value = '' }, 3000)
  }
}

const getUserInitials = () => {
  const user = authStore.user
  if (!user) return 'U'
  
  if (user.volunteer_profile) {
    const profile = user.volunteer_profile
    return `${profile.first_name?.charAt(0) || ''}${profile.last_name?.charAt(0) || ''}`.toUpperCase()
  }
  
  if (user.organization_profile) {
    return user.organization_profile.name?.charAt(0)?.toUpperCase() || 'O'
  }
  
  return user.email?.charAt(0)?.toUpperCase() || 'U'
}

const getUserDisplayName = () => {
  const user = authStore.user
  if (!user) return ''
  
  if (user.volunteer_profile) {
    const profile = user.volunteer_profile
    return `${profile.first_name || ''} ${profile.last_name || ''}`.trim() || user.email
  }
  
  if (user.organization_profile) {
    return user.organization_profile.name || user.email
  }
  
  return user.email
}

const getUserEmail = () => {
  return authStore.user?.email || ''
}

const getRoleBadgeClass = () => {
  const role = authStore.user?.role
  const roleClasses = {
    volunteer: 'badge-primary',
    organization: 'badge-success',
    admin: 'badge-danger'
  }
  return roleClasses[role as keyof typeof roleClasses] || 'badge-gray'
}

const getRoleDisplay = () => {
  const role = authStore.user?.role
  const roleMap = {
    volunteer: 'Волонтер',
    organization: 'Организация',
    admin: 'Администратор'
  }
  return roleMap[role as keyof typeof roleMap] || role
}
</script>
