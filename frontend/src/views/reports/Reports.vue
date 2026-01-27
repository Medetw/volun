<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="container-custom py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Отчеты</h1>
            <p class="text-gray-600 mt-1">Аналитика и статистика платформы</p>
          </div>
          
          <button
            @click="showCreateModal = true"
            class="btn btn-primary"
          >
            Создать отчет
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container-custom py-8">
      <!-- Quick Stats -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-blue-100 rounded-full">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ quickStats.totalReports }}</div>
              <div class="text-sm text-gray-600">Всего отчетов</div>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-green-100 rounded-full">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3v-4m0 6h.01M12 12v4m0 6h.01" />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ quickStats.totalHours }}</div>
              <div class="text-sm text-gray-600">Часов помощи</div>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-purple-100 rounded-full">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ quickStats.activeVolunteers }}</div>
              <div class="text-sm text-gray-600">Активных волонтеров</div>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-orange-100 rounded-full">
              <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ quickStats.completedProjects }}</div>
              <div class="text-sm text-gray-600">Завершено проектов</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white p-4 rounded-lg shadow mb-6">
        <div class="flex flex-wrap items-center gap-4">
          <div>
            <label class="form-label text-sm">Тип отчета</label>
            <select v-model="filters.type" @change="loadReports" class="form-input">
              <option value="">Все типы</option>
              <option value="volunteer">Волонтерские</option>
              <option value="organization">Организационные</option>
              <option value="project">Проектные</option>
              <option value="system">Системные</option>
            </select>
          </div>
          
          <div>
            <label class="form-label text-sm">Период</label>
            <select v-model="filters.period" @change="loadReports" class="form-input">
              <option value="">Все время</option>
              <option value="week">Последняя неделя</option>
              <option value="month">Последний месяц</option>
              <option value="quarter">Последний квартал</option>
              <option value="year">Последний год</option>
            </select>
          </div>
          
          <div>
            <label class="form-label text-sm">Статус</label>
            <select v-model="filters.status" @change="loadReports" class="form-input">
              <option value="">Все статусы</option>
              <option value="draft">Черновик</option>
              <option value="processing">В обработке</option>
              <option value="completed">Завершен</option>
              <option value="failed">Ошибка</option>
            </select>
          </div>
          
          <div class="flex-1">
            <label class="form-label text-sm">Поиск</label>
            <input
              v-model="filters.search"
              @input="debouncedSearch"
              type="text"
              placeholder="Поиск по названию или описанию..."
              class="form-input"
            />
          </div>
        </div>
      </div>

      <!-- Reports List -->
      <div class="bg-white rounded-lg shadow">
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-12">
          <div class="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p class="text-gray-600">Загрузка отчетов...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="reports.length === 0" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v1a1 1 0 001 1h4a1 1 0 001-1v-1m3-2V8a2 2 0 00-2-2H8a2 2 0 00-2 2v7m3-2h6" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">Отчетов пока нет</h3>
          <p class="mt-1 text-sm text-gray-500">
            Создайте первый отчет для анализа данных платформы
          </p>
          <div class="mt-6">
            <button @click="showCreateModal = true" class="btn btn-primary">
              Создать отчет
            </button>
          </div>
        </div>

        <!-- Reports Grid -->
        <div v-else class="divide-y divide-gray-200">
          <div
            v-for="report in reports"
            :key="report.id"
            class="p-6 hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <!-- Header -->
                <div class="flex items-center space-x-3 mb-3">
                  <span :class="getStatusBadgeClass(report.status)">
                    {{ getStatusDisplay(report.status) }}
                  </span>
                  <span class="badge badge-gray">
                    {{ getTypeDisplay(report.type) }}
                  </span>
                  <span class="text-sm text-gray-500">
                    Создан: {{ formatDate(report.created_at) }}
                  </span>
                  <span v-if="report.completed_at" class="text-sm text-gray-500">
                    Завершен: {{ formatDate(report.completed_at) }}
                  </span>
                </div>
                
                <!-- Title and Description -->
                <h3 class="text-lg font-medium text-gray-900 mb-2">
                  {{ report.title }}
                </h3>
                
                <p class="text-gray-600 text-sm mb-3">
                  {{ report.description }}
                </p>
                
                <!-- Report Details -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                  <div class="flex items-center text-sm text-gray-500">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {{ getPeriodDisplay(report.period) }}
                  </div>
                  
                  <div class="flex items-center text-sm text-gray-500">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    {{ report.file_size || 'N/A' }}
                  </div>
                  
                  <div class="flex items-center text-sm text-gray-500">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    {{ report.created_by?.username || 'Система' }}
                  </div>
                </div>
                
                <!-- Progress Bar -->
                <div v-if="report.status === 'processing'" class="mb-3">
                  <div class="flex items-center justify-between text-sm text-gray-600 mb-1">
                    <span>Прогресс генерации</span>
                    <span>{{ report.progress || 0 }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      :style="{ width: `${report.progress || 0}%` }"
                    ></div>
                  </div>
                </div>
                
                <!-- Error Message -->
                <div v-if="report.status === 'failed'" class="bg-red-50 border border-red-200 rounded-md p-3 mb-3">
                  <p class="text-sm text-red-600">
                    {{ report.error_message || 'Ошибка генерации отчета' }}
                  </p>
                </div>
              </div>
              
              <!-- Actions -->
              <div class="flex items-center space-x-2 ml-4">
                <button
                  v-if="report.status === 'completed'"
                  @click="downloadReport(report.id)"
                  :disabled="downloading"
                  class="btn btn-primary text-sm"
                >
                  {{ downloading ? 'Загрузка...' : 'Скачать' }}
                </button>
                
                <button
                  v-if="report.status === 'draft'"
                  @click="generateReport(report.id)"
                  :disabled="generating"
                  class="btn btn-outline text-sm"
                >
                  {{ generating ? 'Генерация...' : 'Сгенерировать' }}
                </button>
                
                <button
                  @click="viewReport(report.id)"
                  class="btn btn-outline text-sm"
                >
                  Подробнее
                </button>
                
                <button
                  @click="deleteReport(report.id)"
                  :disabled="deleting"
                  class="btn btn-outline text-sm text-red-600 hover:text-red-700"
                >
                  Удалить
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Pagination -->
        <div v-if="pagination.totalPages > 1" class="px-6 py-4 border-t border-gray-200">
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-700">
              Показано {{ pagination.start }}-{{ pagination.end }} из {{ pagination.total }} отчетов
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

    <!-- Create Report Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative min-h-screen flex items-center justify-center p-4">
        <div class="bg-white rounded-lg max-w-2xl w-full p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-medium text-gray-900">Создать отчет</h3>
            <button @click="showCreateModal = false" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <form @submit.prevent="handleCreateReport">
            <div class="space-y-4">
              <div>
                <label class="form-label">Название отчета</label>
                <input
                  v-model="createForm.title"
                  type="text"
                  class="form-input"
                  placeholder="Например: Ежемесячный отчет по волонтерству"
                  required
                />
              </div>
              
              <div>
                <label class="form-label">Тип отчета</label>
                <select v-model="createForm.type" class="form-input" required>
                  <option value="">Выберите тип</option>
                  <option value="volunteer">Волонтерский отчет</option>
                  <option value="organization">Организационный отчет</option>
                  <option value="project">Проектный отчет</option>
                  <option value="system">Системный отчет</option>
                </select>
              </div>
              
              <div>
                <label class="form-label">Период</label>
                <select v-model="createForm.period" class="form-input" required>
                  <option value="">Выберите период</option>
                  <option value="week">Последняя неделя</option>
                  <option value="month">Последний месяц</option>
                  <option value="quarter">Последний квартал</option>
                  <option value="year">Последний год</option>
                  <option value="custom">Произвольный период</option>
                </select>
              </div>
              
              <div v-if="createForm.period === 'custom'" class="grid grid-cols-2 gap-4">
                <div>
                  <label class="form-label">Дата начала</label>
                  <input
                    v-model="createForm.start_date"
                    type="date"
                    class="form-input"
                    required
                  />
                </div>
                <div>
                  <label class="form-label">Дата окончания</label>
                  <input
                    v-model="createForm.end_date"
                    type="date"
                    class="form-input"
                    required
                  />
                </div>
              </div>
              
              <div>
                <label class="form-label">Формат</label>
                <select v-model="createForm.format" class="form-input" required>
                  <option value="pdf">PDF</option>
                  <option value="excel">Excel</option>
                  <option value="csv">CSV</option>
                </select>
              </div>
              
              <div>
                <label class="form-label">Описание</label>
                <textarea
                  v-model="createForm.description"
                  rows="3"
                  class="form-input"
                  placeholder="Опишите, что должен содержать отчет..."
                ></textarea>
              </div>
            </div>
            
            <div class="flex space-x-3 mt-6">
              <button
                type="submit"
                :disabled="creating"
                class="btn btn-primary flex-1"
              >
                {{ creating ? 'Создание...' : 'Создать отчет' }}
              </button>
              <button
                type="button"
                @click="showCreateModal = false"
                class="btn btn-outline flex-1"
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
import type { Report } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()

const reports = ref<Report[]>([])
const loading = ref(false)
const downloading = ref(false)
const generating = ref(false)
const deleting = ref(false)
const creating = ref(false)
const showCreateModal = ref(false)

const quickStats = ref({
  totalReports: 0,
  totalHours: 0,
  activeVolunteers: 0,
  completedProjects: 0
})

const filters = reactive({
  type: '',
  period: '',
  status: '',
  search: ''
})

const createForm = reactive({
  title: '',
  type: '',
  period: '',
  start_date: '',
  end_date: '',
  format: 'pdf',
  description: ''
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
    loadReports(),
    loadQuickStats()
  ])
})

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    pagination.currentPage = 1
    loadReports()
  }, 500)
}

const loadReports = async () => {
  try {
    loading.value = true
    
    const params = {
      ...filters,
      page: pagination.currentPage
    }
    
    const response = await apiService.getReports(params)
    reports.value = response.results
    
    // Update pagination
    pagination.total = response.count
    pagination.totalPages = Math.ceil(response.count / 10) // 10 items per page
    pagination.start = (pagination.currentPage - 1) * 10 + 1
    pagination.end = Math.min(pagination.currentPage * 10, response.count)
    
    // Generate page numbers
    generatePageNumbers()
  } catch (error) {
    console.error('Failed to load reports:', error)
  } finally {
    loading.value = false
  }
}

const loadQuickStats = async () => {
  try {
    const data = await apiService.getStatistics()
    quickStats.value = {
      totalReports: data.reports?.total || 0,
      totalHours: data.applications?.total_hours || 0,
      activeVolunteers: data.users?.active || 0,
      completedProjects: data.projects?.completed || 0
    }
  } catch (error) {
    console.error('Failed to load quick stats:', error)
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
    loadReports()
  }
}

const handleCreateReport = async () => {
  try {
    creating.value = true
    const report = await apiService.createReport(createForm)
    
    // Close modal and reset form
    showCreateModal.value = false
    Object.assign(createForm, {
      title: '',
      type: '',
      period: '',
      start_date: '',
      end_date: '',
      format: 'pdf',
      description: ''
    })
    
    // Reload reports
    await loadReports()
  } catch (error) {
    console.error('Failed to create report:', error)
  } finally {
    creating.value = false
  }
}

const generateReport = async (reportId: number) => {
  try {
    generating.value = true
    await apiService.generateReport(reportId)
    
    // Update local report status
    const index = reports.value.findIndex(r => r.id === reportId)
    if (index > -1) {
      reports.value[index].status = 'processing'
      reports.value[index].progress = 0
    }
  } catch (error) {
    console.error('Failed to generate report:', error)
  } finally {
    generating.value = false
  }
}

const downloadReport = async (reportId: number) => {
  try {
    downloading.value = true
    await apiService.downloadReport(reportId)
  } catch (error) {
    console.error('Failed to download report:', error)
  } finally {
    downloading.value = false
  }
}

const viewReport = (reportId: number) => {
  router.push(`/reports/${reportId}`)
}

const deleteReport = async (reportId: number) => {
  if (!confirm('Вы уверены, что хотите удалить этот отчет?')) {
    return
  }
  
  try {
    deleting.value = true
    await apiService.deleteReport(reportId)
    
    // Remove from local list
    reports.value = reports.value.filter(r => r.id !== reportId)
  } catch (error) {
    console.error('Failed to delete report:', error)
  } finally {
    deleting.value = false
  }
}

const getStatusBadgeClass = (status: string) => {
  const statusClasses = {
    draft: 'badge-gray',
    processing: 'badge-warning',
    completed: 'badge-success',
    failed: 'badge-danger'
  }
  return statusClasses[status as keyof typeof statusClasses] || 'badge-gray'
}

const getStatusDisplay = (status: string) => {
  const statusMap = {
    draft: 'Черновик',
    processing: 'В обработке',
    completed: 'Завершен',
    failed: 'Ошибка'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const getTypeDisplay = (type: string) => {
  const typeMap = {
    volunteer: 'Волонтерский',
    organization: 'Организационный',
    project: 'Проектный',
    system: 'Системный'
  }
  return typeMap[type as keyof typeof typeMap] || type
}

const getPeriodDisplay = (period: string) => {
  const periodMap = {
    week: 'Последняя неделя',
    month: 'Последний месяц',
    quarter: 'Последний квартал',
    year: 'Последний год',
    custom: 'Произвольный'
  }
  return periodMap[period as keyof typeof periodMap] || period
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
