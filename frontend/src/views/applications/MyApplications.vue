<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="container-custom py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">
              Мои заявки
            </h1>
            <p class="text-gray-600 mt-1">
              Управление вашими заявками на участие в проектах
            </p>
          </div>
          
          <router-link
            to="/projects"
            class="btn btn-primary"
          >
            Найти проекты
          </router-link>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container-custom py-8">
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
              placeholder="Поиск по названию проекта..."
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
            У вас пока нет заявок
          </h3>
          <p class="mt-1 text-sm text-gray-500">
            Подайте заявку на интересующий проект, чтобы начать помогать
          </p>
          <div class="mt-6">
            <router-link
              to="/projects"
              class="btn btn-primary"
            >
              Найти проекты
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
                
                <!-- Project Info -->
                <h3 class="text-lg font-medium text-gray-900 mb-2">
                  <router-link
                    :to="`/projects/${application.project.id}`"
                    class="hover:text-primary-600"
                  >
                    {{ application.project.title }}
                  </router-link>
                </h3>
                
                <p class="text-gray-600 text-sm mb-3 line-clamp-2">
                  {{ application.cover_letter }}
                </p>
                
                <!-- Project Details -->
                <div class="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                  <div class="flex items-center">
                    <svg
                      class="w-4 h-4 mr-1"
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
                    {{ application.project.organization_name }}
                  </div>
                  
                  <div class="flex items-center">
                    <svg
                      class="w-4 h-4 mr-1"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314-1.314l4.242 4.242a1.998 1.998 0 010 2.828z"
                      />
                    </svg>
                    {{ application.project.region?.name || 'Онлайн' }}
                  </div>
                  
                  <div class="flex items-center">
                    <svg
                      class="w-4 h-4 mr-1"
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
                    {{ application.hours_committed }} часов
                  </div>
                </div>
                
                <!-- Review Info -->
                <div
                  v-if="application.reviewed_by"
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
                    class="text-sm text-gray-600 mt-1"
                  >
                    {{ application.review_comment }}
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
                
                <button
                  v-if="application.status === 'pending'"
                  :disabled="cancelling"
                  class="btn btn-outline text-sm text-red-600 hover:text-red-700"
                  @click="cancelApplication(application.id)"
                >
                  {{ cancelling ? 'Отмена...' : 'Отменить' }}
                </button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import apiService from '@/services/api'
import type { Application } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()

const applications = ref<Application[]>([])
const loading = ref(false)
const cancelling = ref(false)

const filters = reactive({
  status: '',
  ordering: '-created_at',
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

onMounted(() => {
  loadApplications()
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

const cancelApplication = async (applicationId: number) => {
  if (!confirm('Вы уверены, что хотите отменить эту заявку?')) {
    return
  }
  
  try {
    cancelling.value = true
    await apiService.cancelApplication(applicationId)
    
    // Update local applications list
    const index = applications.value.findIndex(app => app.id === applicationId)
    if (index > -1) {
      applications.value[index].status = 'cancelled'
    }
  } catch (error) {
    console.error('Failed to cancel application:', error)
  } finally {
    cancelling.value = false
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
