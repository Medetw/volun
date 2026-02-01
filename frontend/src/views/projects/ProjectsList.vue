<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header with filters -->
    <div class="bg-white shadow-sm border-b">
      <div class="container-custom py-6">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Проекты</h1>
            <p class="text-gray-600 mt-1">Найдите проекты, которые вам интересны</p>
          </div>
          
          <div class="flex flex-col sm:flex-row gap-3">
            <button
              @click="showFilters = !showFilters"
              class="btn btn-outline flex items-center justify-center"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 01-.707.293H3a1 1 0 01-1-1V4z" />
              </svg>
              Фильтры
              <span v-if="activeFiltersCount > 0" class="ml-2 badge badge-primary">
                {{ activeFiltersCount }}
              </span>
            </button>
            
            <div class="relative">
              <input
                v-model="searchQuery"
                @input="debouncedSearch"
                type="text"
                placeholder="Поиск проектов..."
                class="form-input pl-10 pr-4"
              />
              <svg class="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Filters Panel -->
        <div v-if="showFilters" class="mt-6 p-4 bg-gray-50 rounded-lg">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label class="form-label">Категория</label>
              <select v-model="filters.category" @change="applyFilters" class="form-input">
                <option value="">Все категории</option>
                <option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </option>
              </select>
            </div>
            
            <div>
              <label class="form-label">Регион</label>
              <select v-model="filters.region" @change="applyFilters" class="form-input">
                <option value="">Все регионы</option>
                <option v-for="region in regions" :key="region.id" :value="region.id">
                  {{ region.name }}
                </option>
              </select>
            </div>
            
            <div>
              <label class="form-label">Формат</label>
              <select v-model="filters.format" @change="applyFilters" class="form-input">
                <option value="">Все форматы</option>
                <option value="online">Онлайн</option>
                <option value="offline">Офлайн</option>
                <option value="hybrid">Гибридный</option>
              </select>
            </div>
            
            <div>
              <label class="form-label">Статус</label>
              <select v-model="filters.status" @change="applyFilters" class="form-input">
                <option value="">Все статусы</option>
                <option value="active">Активные</option>
                <option value="draft">Черновики</option>
                <option value="completed">Завершенные</option>
              </select>
            </div>
          </div>
          
          <div class="mt-4 flex justify-end space-x-3">
            <button @click="clearFilters" class="btn btn-ghost">
              Очистить
            </button>
            <button @click="showFilters = false" class="btn btn-primary">
              Применить
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Projects Grid -->
    <div class="container-custom py-8">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="loading-spinner w-8 h-8 mx-auto mb-4"></div>
        <p class="text-gray-600">Загрузка проектов...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="projects.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">Проекты не найдены</h3>
        <p class="mt-1 text-sm text-gray-500">
          Попробуйте изменить фильтры или поисковый запрос
        </p>
        <div class="mt-6">
          <button @click="clearFilters" class="btn btn-primary">
            Очистить фильтры
          </button>
        </div>
      </div>

      <!-- Projects Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="project in projects"
          :key="project.id"
          class="card hover:shadow-lg transition-shadow duration-200"
        >
          <div class="p-6">
            <!-- Header -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <span class="badge badge-primary text-xs">
                  {{ project.category.name }}
                </span>
                <h3 class="mt-2 text-lg font-semibold text-gray-900 line-clamp-2">
                  {{ project.title }}
                </h3>
              </div>
              <span class="status-active badge text-xs">
                {{ getStatusDisplay(project.status) }}
              </span>
            </div>

            <!-- Description -->
            <p class="text-gray-600 text-sm mb-4 line-clamp-3">
              {{ project.description }}
            </p>

            <!-- Meta Information -->
            <div class="space-y-2 text-sm text-gray-500 mb-4">
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                {{ project.organization_name || 'Организация' }}
              </div>
              
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314-1.314l4.242 4.242a1.998 1.998 0 010 2.828z" />
                </svg>
                {{ project.region?.name || 'Онлайн' }}
              </div>
              
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {{ getFormatDisplay(project.format) }}
              </div>
              
              <div v-if="project.start_date" class="flex items-center">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {{ formatDate(project.start_date) }}
              </div>
            </div>

            <!-- Progress Bar -->
            <div class="mb-4">
              <div class="flex justify-between text-sm text-gray-600 mb-1">
                <span>Волонтеры</span>
                <span>{{ project.volunteers_needed - project.volunteers_remaining }}/{{ project.volunteers_needed }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  :style="{ width: `${getProgressPercentage(project)}%` }"
                ></div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex space-x-2">
              <router-link
                :to="`/projects/${project.id}`"
                class="btn btn-primary flex-1"
              >
                Подробнее
              </router-link>
              
              <button
                v-if="authStore.isAuthenticated && authStore.isVolunteer && project.volunteers_remaining > 0"
                @click="quickApply(project)"
                class="btn btn-outline"
              >
                Подать заявку
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.totalPages > 1" class="mt-8">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-700">
            Показано {{ pagination.start }}-{{ pagination.end }} из {{ pagination.total }} проектов
          </div>
          
          <div class="flex space-x-2">
            <button
              @click="goToPage(pagination.currentPage - 1)"
              :disabled="pagination.currentPage === 1"
              class="btn btn-outline"
              :class="{ 'opacity-50 cursor-not-allowed': pagination.currentPage === 1 }"
            >
              ←
            </button>
            
            <div class="flex space-x-1">
              <button
                v-for="page in pagination.pages"
                :key="page"
                @click="goToPage(page)"
                :class="[
                  'btn',
                  page === pagination.currentPage
                    ? 'btn-primary'
                    : 'btn-outline'
                ]"
              >
                {{ page }}
              </button>
            </div>
            
            <button
              @click="goToPage(pagination.currentPage + 1)"
              :disabled="pagination.currentPage === pagination.totalPages"
              class="btn btn-outline"
              :class="{ 'opacity-50 cursor-not-allowed': pagination.currentPage === pagination.totalPages }"
            >
              →
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import apiService from '@/services/api'
import type { Project, Category, Region } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()

const projects = ref<Project[]>([])
const categories = ref<Category[]>([])
const regions = ref<Region[]>([])
const loading = ref(true)
const showFilters = ref(false)
const searchQuery = ref('')

const filters = reactive({
  category: '',
  region: '',
  format: '',
  status: 'active',
  search: ''
})

const pagination = reactive({
  currentPage: 1,
  totalPages: 1,
  total: 0,
  start: 0,
  end: 0,
  pages: [] as number[]
})

let searchTimeout: NodeJS.Timeout

onMounted(async () => {
  await Promise.all([
    loadProjects(),
    loadCategories(),
    loadRegions()
  ])
})

const activeFiltersCount = computed(() => {
  return Object.values(filters).filter(value => value !== '').length
})

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    filters.search = searchQuery.value
    applyFilters()
  }, 500)
}

const loadProjects = async () => {
  try {
    loading.value = true
    
    const params = {
      ...filters,
      page: pagination.currentPage
    }
    
    const response = await apiService.getProjects(params)
    projects.value = response.results
    
    // Update pagination
    pagination.total = response.count
    pagination.totalPages = Math.ceil(response.count / 9) // 9 items per page
    pagination.start = (pagination.currentPage - 1) * 9 + 1
    pagination.end = Math.min(pagination.currentPage * 9, response.count)
    
    // Generate page numbers
    generatePageNumbers()
  } catch (error) {
    console.error('Failed to load projects:', error)
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const response = await apiService.getCategories()
    categories.value = response.results
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const loadRegions = async () => {
  try {
    const response = await apiService.getRegions()
    regions.value = response.results
  } catch (error) {
    console.error('Failed to load regions:', error)
  }
}

const applyFilters = () => {
  pagination.currentPage = 1
  loadProjects()
}

const clearFilters = () => {
  Object.keys(filters).forEach(key => {
    filters[key as keyof typeof filters] = ''
  })
  filters.status = 'active'
  searchQuery.value = ''
  showFilters.value = false
  applyFilters()
}

const generatePageNumbers = () => {
  const pages = []
  const currentPage = pagination.currentPage
  const totalPages = pagination.totalPages
  
  if (totalPages <= 7) {
    for (let i = 1; i <= totalPages; i++) {
      pages.push(i)
    }
  } else {
    if (currentPage <= 4) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push(-1)
      pages.push(totalPages)
    } else if (currentPage >= totalPages - 3) {
      pages.push(1)
      pages.push(-1)
      for (let i = totalPages - 4; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1)
      pages.push(-1)
      for (let i = currentPage - 1; i <= currentPage + 1; i++) {
        pages.push(i)
      }
      pages.push(-1)
      pages.push(totalPages)
    }
  }
  
  pagination.pages = pages
}

const goToPage = (page: number) => {
  if (page >= 1 && page <= pagination.totalPages) {
    pagination.currentPage = page
    loadProjects()
  }
}

const getStatusDisplay = (status: string) => {
  const statusMap = {
    active: 'Активный',
    draft: 'Черновик',
    completed: 'Завершен',
    cancelled: 'Отменен'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const getFormatDisplay = (format: string) => {
  const formatMap = {
    online: 'Онлайн',
    offline: 'Офлайн',
    hybrid: 'Гибридный'
  }
  return formatMap[format as keyof typeof formatMap] || format
}

const getProgressPercentage = (project: Project) => {
  return ((project.volunteers_needed - project.volunteers_remaining) / project.volunteers_needed) * 100
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const quickApply = async (project: Project) => {
  try {
    await apiService.createApplication({
      project: project.id,
      cover_letter: 'Хочу принять участие в проекте!',
      hours_committed: 5
    })
    
    // Show success message or redirect
    router.push('/applications/my')
  } catch (error) {
    console.error('Failed to apply:', error)
  }
}

// Watch for filter changes
watch(() => filters.category, () => {
  if (filters.category) {
    applyFilters()
  }
})

watch(() => filters.region, () => {
  if (filters.region) {
    applyFilters()
  }
})
</script>
