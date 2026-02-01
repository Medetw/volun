<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="container-custom py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">
              Заявки на проекты
            </h1>
            <p class="text-gray-600 mt-1">
              Управление заявками волонтеров на ваши проекты
            </p>
          </div>
          
          <router-link
            to="/dashboard/organization"
            class="btn btn-primary"
          >
            Мои проекты
          </router-link>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container-custom py-8">
      <!-- Stats Overview -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-blue-100 rounded-full">
              <svg
                class="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2z"
                />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">
                {{ stats.total }}
              </div>
              <div class="text-sm text-gray-600">
                Всего заявок
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-yellow-100 rounded-full">
              <svg
                class="w-6 h-6 text-yellow-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3v-4m0 6h.01M12 12v4m0 6h.01"
                />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">
                {{ stats.pending }}
              </div>
              <div class="text-sm text-gray-600">
                На рассмотрении
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-green-100 rounded-full">
              <svg
                class="w-6 h-6 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">
                {{ stats.approved }}
              </div>
              <div class="text-sm text-gray-600">
                Одобрено
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-red-100 rounded-full">
              <svg
                class="w-6 h-6 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">
                {{ stats.rejected }}
              </div>
              <div class="text-sm text-gray-600">
                Отклонено
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white p-4 rounded-lg shadow mb-6">
        <div class="flex flex-wrap items-center gap-4">
          <div>
            <label class="form-label text-sm">Статус</label>
            <select
              v-model="filters.status"
              class="form-input"
              @change="loadApplications"
            >
              <option value="">
                Все статусы
              </option>
              <option value="pending">
                На рассмотрении
              </option>
              <option value="approved">
                Одобрено
              </option>
              <option value="rejected">
                Отклонено
              </option>
              <option value="cancelled">
                Отменено
              </option>
            </select>
          </div>
          
          <div>
            <label class="form-label text-sm">Проект</label>
            <select
              v-model="filters.project"
              class="form-input"
              @change="loadApplications"
            >
              <option value="">
                Все проекты
              </option>
              <option
                v-for="project in projects"
                :key="project.id"
                :value="project.id"
              >
                {{ project.title }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="form-label text-sm">Сортировка</label>
            <select
              v-model="filters.ordering"
              class="form-input"
              @change="loadApplications"
            >
              <option value="-created_at">
                Новые сначала
              </option>
              <option value="created_at">
                Старые сначала
              </option>
              <option value="-updated_at">
                Недавно обновленные
              </option>
            </select>
          </div>
          
          <div class="flex-1">
            <label class="form-label text-sm">Поиск</label>
            <input
              v-model="filters.search"
              type="text"
              placeholder="Поиск по волонтеру или проекту..."
              class="form-input"
              @input="debouncedSearch"
            >
          </div>
        </div>
      </div>

      <!-- Applications List -->
      <div class="bg-white rounded-lg shadow">
        <!-- Loading State -->
        <div
          v-if="loading"
          class="text-center py-12"
        >
          <div class="loading-spinner w-8 h-8 mx-auto mb-4" />
          <p class="text-gray-600">
            Загрузка заявок...
          </p>
        </div>

        <!-- Empty State -->
        <div
          v-else-if="applications.length === 0"
          class="text-center py-12"
        >
          <svg
            class="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2z"
            />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">
            Заявок пока нет
          </h3>
          <p class="mt-1 text-sm text-gray-500">
            Волонтеры еще не подали заявки на ваши проекты
          </p>
          <div class="mt-6">
            <router-link
              to="/projects/create"
              class="btn btn-primary"
            >
              Создать проект
            </router-link>
          </div>
        </div>

        <!-- Applications Grid -->
        <div
          v-else
          class="divide-y divide-gray-200"
        >
          <div
            v-for="application in applications"
            :key="application.id"
            class="p-6 hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <!-- Header -->
                <div class="flex items-center space-x-3 mb-3">
                  <span :class="getStatusBadgeClass(application.status)">
                    {{ getStatusDisplay(application.status) }}
                  </span>
                  <span class="text-sm text-gray-500">
                    Подано: {{ formatDate(application.created_at) }}
                  </span>
                  <span
                    v-if="application.updated_at !== application.created_at"
                    class="text-sm text-gray-500"
                  >
                    Обновлено: {{ formatDate(application.updated_at) }}
                  </span>
                </div>
                
                <!-- Volunteer Info -->
                <div class="flex items-center space-x-3 mb-3">
                  <div class="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                    <span class="text-sm font-medium text-gray-700">
                      {{ application.volunteer.username.charAt(0).toUpperCase() }}
                    </span>
                  </div>
                  <div>
                    <h4 class="text-lg font-medium text-gray-900">
                      {{ application.volunteer.username }}
                    </h4>
                    <p class="text-sm text-gray-500">
                      {{ application.volunteer.email }}
                    </p>
                  </div>
                </div>
                
                <!-- Project Info -->
                <div class="bg-gray-50 p-3 rounded-md mb-3">
                  <h3 class="text-lg font-medium text-gray-900 mb-2">
                    <router-link
                      :to="`/projects/${application.project.id}`"
                      class="hover:text-primary-600"
                    >
                      {{ application.project.title }}
                    </router-link>
                  </h3>
                  <p class="text-gray-600 text-sm mb-2">
                    {{ application.project.description }}
                  </p>
                  <div class="flex items-center space-x-4 text-sm text-gray-500">
                    <span>{{ application.hours_committed }} часов</span>
                    <span>{{ application.project.volunteers_needed }} волонтеров нужно</span>
                  </div>
                </div>
                
                <!-- Cover Letter -->
                <div class="mb-3">
                  <h4 class="text-sm font-medium text-gray-900 mb-2">
                    Сопроводительное письмо:
                  </h4>
                  <p class="text-gray-600 text-sm">
                    {{ application.cover_letter }}
                  </p>
                </div>
                
                <!-- Review Section -->
                <div
                  v-if="application.status === 'pending'"
                  class="bg-blue-50 p-4 rounded-md"
                >
                  <h4 class="text-sm font-medium text-gray-900 mb-3">
                    Действия с заявкой:
                  </h4>
                  <div class="flex space-x-3">
                    <button
                      :disabled="processing"
                      class="btn btn-success text-sm"
                      @click="approveApplication(application.id)"
                    >
                      {{ processing ? 'Обработка...' : 'Одобрить' }}
                    </button>
                    <button
                      :disabled="processing"
                      class="btn btn-danger text-sm"
                      @click="showRejectModal(application)"
                    >
                      {{ processing ? 'Обработка...' : 'Отклонить' }}
                    </button>
                  </div>
                </div>
                
                <!-- Review Info -->
                <div
                  v-else-if="application.reviewed_by"
                  class="bg-gray-50 p-3 rounded-md"
                >
                  <div class="flex items-center text-sm">
                    <svg
                      class="w-4 h-4 mr-2 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <span class="text-gray-600">
                      Рассмотрено: {{ application.reviewed_by.username }}
                    </span>
                    <span class="text-gray-500 ml-2">
                      {{ formatDate(application.reviewed_at) }}
                    </span>
                  </div>
                  <p
                    v-if="application.review_comment"
                    class="text-sm text-gray-600 mt-2"
                  >
                    <strong>Комментарий:</strong> {{ application.review_comment }}
                  </p>
                </div>
              </div>
              
              <!-- Actions -->
              <div class="flex items-center space-x-2 ml-4">
                <router-link
                  :to="`/projects/${application.project.id}`"
                  class="btn btn-outline text-sm"
                >
                  Подробнее
                </router-link>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Pagination -->
        <div
          v-if="pagination.totalPages > 1"
          class="px-6 py-4 border-t border-gray-200"
        >
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-700">
              Показано {{ pagination.start }}-{{ pagination.end }} из {{ pagination.total }} заявок
            </div>
            
            <div class="flex space-x-2">
              <button
                :disabled="pagination.currentPage === 1"
                class="btn btn-outline"
                :class="{ 'opacity-50 cursor-not-allowed': pagination.currentPage === 1 }"
                @click="goToPage(pagination.currentPage - 1)"
              >
                ←
              </button>
              
              <div class="flex space-x-1">
                <button
                  v-for="page in pagination.pages"
                  :key="page"
                  :class="[
                    'btn',
                    page === pagination.currentPage
                      ? 'btn-primary'
                      : 'btn-outline'
                  ]"
                  @click="goToPage(page)"
                >
                  {{ page }}
                </button>
              </div>
              
              <button
                :disabled="pagination.currentPage === pagination.totalPages"
                class="btn btn-outline"
                :class="{ 'opacity-50 cursor-not-allowed': pagination.currentPage === pagination.totalPages }"
                @click="goToPage(pagination.currentPage + 1)"
              >
                →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reject Modal -->
    <div
      v-if="showRejectModalFlag"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    >
      <div class="relative min-h-screen flex items-center justify-center p-4">
        <div class="bg-white rounded-lg max-w-md w-full p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            Отклонить заявку
          </h3>
          
          <form @submit.prevent="handleReject">
            <div class="mb-4">
              <label class="form-label">Причина отклонения</label>
              <textarea
                v-model="rejectForm.comment"
                rows="4"
                class="form-input"
                placeholder="Укажите причину отклонения заявки..."
                required
              />
            </div>
            
            <div class="flex space-x-3">
              <button
                type="submit"
                :disabled="processing"
                class="btn btn-danger flex-1"
              >
                {{ processing ? 'Отклонение...' : 'Отклонить' }}
              </button>
              <button
                type="button"
                class="btn btn-outline flex-1"
                @click="showRejectModalFlag = false"
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import apiService from '@/services/api'
import type { Application, Project } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()

const applications = ref<Application[]>([])
const projects = ref<Project[]>([])
const loading = ref(false)
const processing = ref(false)
const showRejectModalFlag = ref(false)
const currentApplicationId = ref<number | null>(null)

const stats = ref({
  total: 0,
  pending: 0,
  approved: 0,
  rejected: 0
})

const filters = reactive({
  status: '',
  project: '',
  ordering: '-created_at',
  search: ''
})

const rejectForm = reactive({
  comment: ''
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
    loadApplications(),
    loadProjects(),
    loadStats()
  ])
})

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    pagination.currentPage = 1
    loadApplications()
  }, 500)
}

const loadApplications = async () => {
  try {
    loading.value = true
    
    const params = {
      ...filters,
      page: pagination.currentPage
    }
    
    const response = await apiService.getApplications(params)
    applications.value = response.results
    
    // Update pagination
    pagination.total = response.count
    pagination.totalPages = Math.ceil(response.count / 10) // 10 items per page
    pagination.start = (pagination.currentPage - 1) * 10 + 1
    pagination.end = Math.min(pagination.currentPage * 10, response.count)
    
    // Generate page numbers
    generatePageNumbers()
  } catch (error) {
    console.error('Failed to load applications:', error)
  } finally {
    loading.value = false
  }
}

const loadProjects = async () => {
  try {
    const response = await apiService.getProjects()
    projects.value = response.results
  } catch (error) {
    console.error('Failed to load projects:', error)
  }
}

const loadStats = async () => {
  try {
    const response = await apiService.getApplications()
    const allApplications = response.results
    
    stats.value = {
      total: allApplications.length,
      pending: allApplications.filter(app => app.status === 'pending').length,
      approved: allApplications.filter(app => app.status === 'approved').length,
      rejected: allApplications.filter(app => app.status === 'rejected').length
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
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
    loadApplications()
  }
}

const approveApplication = async (applicationId: number) => {
  try {
    processing.value = true
    await apiService.approveApplication(applicationId)
    
    // Update local applications list
    const index = applications.value.findIndex(app => app.id === applicationId)
    if (index > -1) {
      applications.value[index].status = 'approved'
    }
    
    // Update stats
    await loadStats()
  } catch (error) {
    console.error('Failed to approve application:', error)
  } finally {
    processing.value = false
  }
}

const showRejectModal = (application: Application) => {
  currentApplicationId.value = application.id
  rejectForm.comment = ''
  showRejectModalFlag.value = true
}

const handleReject = async () => {
  if (!currentApplicationId.value) return
  
  try {
    processing.value = true
    await apiService.rejectApplication(currentApplicationId.value, {
      review_comment: rejectForm.comment
    })
    
    // Update local applications list
    const index = applications.value.findIndex(app => app.id === currentApplicationId.value)
    if (index > -1) {
      applications.value[index].status = 'rejected'
      applications.value[index].review_comment = rejectForm.comment
    }
    
    // Update stats
    await loadStats()
    
    // Close modal
    showRejectModalFlag.value = false
    currentApplicationId.value = null
  } catch (error) {
    console.error('Failed to reject application:', error)
  } finally {
    processing.value = false
  }
}

const getStatusBadgeClass = (status: string) => {
  const statusClasses = {
    pending: 'badge-warning',
    approved: 'badge-success',
    rejected: 'badge-danger',
    cancelled: 'badge-gray'
  }
  return statusClasses[status as keyof typeof statusClasses] || 'badge-gray'
}

const getStatusDisplay = (status: string) => {
  const statusMap = {
    pending: 'На рассмотрении',
    approved: 'Одобрено',
    rejected: 'Отклонено',
    cancelled: 'Отменено'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
