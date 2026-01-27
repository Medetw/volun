<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="container-custom max-w-4xl">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Редактировать проект</h1>
        <p class="text-gray-600 mt-2">Измените информацию о вашем волонтерском проекте</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="loading-spinner w-8 h-8 mr-3"></div>
        <span class="text-gray-600">Загрузка проекта...</span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="flex items-center justify-center py-20">
        <div class="text-center">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">Проект не найден</h3>
          <p class="mt-1 text-sm text-gray-500">
            Проект, который вы ищете, не существует или был удален
          </p>
          <div class="mt-6">
            <router-link to="/dashboard/organization" class="btn btn-primary">
              ← Вернуться к проектам
            </router-link>
          </div>
        </div>
      </div>

      <!-- Form -->
      <form v-else-if="project" @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Error Message -->
        <div v-if="errorMessage" class="bg-red-50 border border-red-200 rounded-md p-4">
          <div class="text-sm text-red-600">{{ errorMessage }}</div>
        </div>

        <!-- Success Message -->
        <div v-if="successMessage" class="bg-green-50 border border-green-200 rounded-md p-4">
          <div class="text-sm text-green-600">{{ successMessage }}</div>
        </div>

        <!-- Basic Information -->
        <div class="bg-white p-6 rounded-lg shadow">
          <h2 class="text-xl font-semibold mb-6">Основная информация</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="form-label">Название проекта *</label>
              <input
                v-model="form.title"
                type="text"
                required
                class="form-input"
                :class="{ 'border-red-500': errors.title }"
                placeholder="Название проекта"
              />
              <div v-if="errors.title" class="form-error">{{ errors.title }}</div>
            </div>
            
            <div>
              <label class="form-label">Категория *</label>
              <select
                v-model="form.category_id"
                required
                class="form-input"
                :class="{ 'border-red-500': errors.category_id }"
              >
                <option value="">Выберите категорию</option>
                <option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </option>
              </select>
              <div v-if="errors.category_id" class="form-error">{{ errors.category_id }}</div>
            </div>
          </div>

          <div>
            <label class="form-label">Описание *</label>
            <textarea
              v-model="form.description"
              rows="4"
              required
              class="form-input"
              :class="{ 'border-red-500': errors.description }"
              placeholder="Подробное описание проекта, цели и задачи"
            ></textarea>
            <div v-if="errors.description" class="form-error">{{ errors.description }}</div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="form-label">Формат проведения *</label>
              <select
                v-model="form.format"
                required
                class="form-input"
                :class="{ 'border-red-500': errors.format }"
              >
                <option value="">Выберите формат</option>
                <option value="online">Онлайн</option>
                <option value="offline">Офлайн</option>
                <option value="hybrid">Гибридный</option>
              </select>
              <div v-if="errors.format" class="form-error">{{ errors.format }}</div>
            </div>
            
            <div>
              <label class="form-label">Регион *</label>
              <select
                v-model="form.region_id"
                required
                class="form-input"
                :class="{ 'border-red-500': errors.region_id }"
              >
                <option value="">Выберите регион</option>
                <option v-for="region in regions" :key="region.id" :value="region.id">
                  {{ region.name }}
                </option>
              </select>
              <div v-if="errors.region_id" class="form-error">{{ errors.region_id }}</div>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label class="form-label">Дата начала</label>
              <input
                v-model="form.start_date"
                type="date"
                class="form-input"
              />
            </div>
            
            <div>
              <label class="form-label">Дата окончания</label>
              <input
                v-model="form.end_date"
                type="date"
                class="form-input"
              />
            </div>
            
            <div>
              <label class="form-label">Количество волонтеров *</label>
              <input
                v-model.number="form.volunteers_needed"
                type="number"
                min="1"
                required
                class="form-input"
                :class="{ 'border-red-500': errors.volunteers_needed }"
                placeholder="10"
              />
              <div v-if="errors.volunteers_needed" class="form-error">{{ errors.volunteers_needed }}</div>
            </div>
          </div>
        </div>

        <!-- Additional Information -->
        <div class="bg-white p-6 rounded-lg shadow">
          <h2 class="text-xl font-semibold mb-6">Дополнительная информация</h2>
          
          <div>
            <label class="form-label">Требования к волонтерам</label>
            <textarea
              v-model="form.requirements"
              rows="3"
              class="form-input"
              placeholder="Опишите требования к участникам (возраст, навыки, опыт и т.д.)"
            ></textarea>
          </div>

          <div>
            <label class="form-label">Контактная информация</label>
            <textarea
              v-model="form.contact_info"
              rows="2"
              class="form-input"
              placeholder="Как с вами связаться (телефон, email, мессенджеры)"
            ></textarea>
          </div>
        </div>

        <!-- Project Image -->
        <div class="bg-white p-6 rounded-lg shadow">
          <h2 class="text-xl font-semibold mb-6">Изображение проекта</h2>
          
          <div class="space-y-4">
            <div v-if="imagePreview" class="relative">
              <img
                :src="imagePreview"
                alt="Превью изображения"
                class="w-full h-48 object-cover rounded-lg"
              />
              <button
                @click="removeImage"
                type="button"
                class="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div v-else>
              <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <div class="mt-4">
                  <label for="image-upload" class="btn btn-outline cursor-pointer">
                    Выбрать изображение
                  </label>
                  <input
                    id="image-upload"
                    type="file"
                    accept="image/*"
                    @change="handleImageUpload"
                    class="hidden"
                  />
                </div>
                <p class="text-xs text-gray-500 mt-2">
                  PNG, JPG, GIF до 10MB
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Status -->
        <div class="bg-white p-6 rounded-lg shadow">
          <h2 class="text-xl font-semibold mb-6">Статус проекта</h2>
          
          <div>
            <label class="form-label">Статус</label>
            <select
              v-model="form.status"
              class="form-input"
            >
              <option value="draft">Черновик</option>
              <option value="active">Активный</option>
              <option value="completed">Завершен</option>
              <option value="cancelled">Отменен</option>
            </select>
            <p class="text-sm text-gray-500 mt-1">
              Черновик: проект не виден волонтерам<br>
              Активный: проект доступен для заявок
            </p>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end space-x-4">
          <router-link :to="`/projects/${project.id}`" class="btn btn-outline">
            Отмена
          </router-link>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import apiService from '@/services/api'
import type { Project, Category, Region } from '@/types/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const project = ref<Project | null>(null)
const categories = ref<Category[]>([])
const regions = ref<Region[]>([])
const imageFile = ref<File | null>(null)
const imagePreview = ref<string | null>(null)

const loading = ref(true)
const error = ref(false)
const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const form = reactive({
  title: '',
  description: '',
  category_id: '',
  region_id: '',
  format: '',
  start_date: '',
  end_date: '',
  volunteers_needed: 1,
  requirements: '',
  contact_info: '',
  status: 'draft'
})

const errors = reactive({
  title: '',
  description: '',
  category_id: '',
  region_id: '',
  format: '',
  volunteers_needed: ''
})

onMounted(async () => {
  await Promise.all([
    loadProject(),
    loadCategories(),
    loadRegions()
  ])
})

const loadProject = async () => {
  try {
    loading.value = true
    error.value = false
    
    const projectId = Number(route.params.id)
    project.value = await apiService.getProject(projectId)
    
    // Populate form with project data
    form.title = project.value.title
    form.description = project.value.description
    form.category_id = project.value.category.id
    form.region_id = project.value.region?.id || ''
    form.format = project.value.format
    form.start_date = project.value.start_date || ''
    form.end_date = project.value.end_date || ''
    form.volunteers_needed = project.value.volunteers_needed
    form.requirements = project.value.requirements || ''
    form.contact_info = project.value.contact_info || ''
    form.status = project.value.status
    
    // Set image preview if exists
    if (project.value.image) {
      imagePreview.value = project.value.image
    }
  } catch (err) {
    error.value = true
    console.error('Failed to load project:', err)
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const response = await apiService.getCategories()
    categories.value = response.results
  } catch (err) {
    console.error('Failed to load categories:', err)
  }
}

const loadRegions = async () => {
  try {
    const response = await apiService.getRegions()
    regions.value = response.results
  } catch (err) {
    console.error('Failed to load regions:', err)
  }
}

const handleImageUpload = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (file) {
    imageFile.value = file
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const removeImage = () => {
  imageFile.value = null
  imagePreview.value = null
}

const validateForm = () => {
  // Reset errors
  Object.keys(errors).forEach(key => {
    errors[key as keyof typeof errors] = ''
  })

  if (!form.title.trim()) {
    errors.title = 'Название проекта обязательно'
    return false
  }

  if (!form.description.trim()) {
    errors.description = 'Описание проекта обязательно'
    return false
  }

  if (!form.category_id) {
    errors.category_id = 'Категория обязательна'
    return false
  }

  if (!form.region_id) {
    errors.region_id = 'Регион обязателен'
    return false
  }

  if (!form.format) {
    errors.format = 'Формат обязателен'
    return false
  }

  if (!form.volunteers_needed || form.volunteers_needed < 1) {
    errors.volunteers_needed = 'Количество волонтеров должно быть больше 0'
    return false
  }

  return true
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  try {
    submitting.value = true
    errorMessage.value = ''
    successMessage.value = ''

    const projectId = Number(route.params.id)
    
    const projectData = {
      ...form,
      image: imageFile.value
    }

    const updatedProject = await apiService.updateProject(projectId, projectData)
    
    successMessage.value = 'Проект успешно обновлен!'
    
    // Update local project data
    project.value = updatedProject
    
    // Scroll to top
    window.scrollTo(0, 0)
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Произошла ошибка при обновлении проекта'
  } finally {
    submitting.value = false
  }
}
</script>
