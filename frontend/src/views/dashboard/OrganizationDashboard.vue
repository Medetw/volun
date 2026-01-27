<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="container-custom py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Панель организации</h1>
            <p class="text-gray-600 mt-1">Добро пожаловать, {{ getUserDisplayName() }}!</p>
          </div>
          
          <div class="flex items-center space-x-4">
            <router-link to="/profile" class="btn btn-outline">
              Профиль
            </router-link>
            <router-link to="/notifications" class="btn btn-outline relative">
              Уведомления
              <span v-if="unreadCount > 0" class="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {{ unreadCount }}
              </span>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container-custom py-8">
      <!-- Stats Overview -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-blue-100 rounded-full">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ stats.total_projects }}</div>
              <div class="text-sm text-gray-600">Всего проектов</div>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-green-100 rounded-full">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2z" />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ stats.total_applications }}</div>
              <div class="text-sm text-gray-600">Всего заявок</div>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-purple-100 rounded-full">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3v-4m0 6h.01M12 12v4m0 6h.01" />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ stats.total_hours }}</div>
              <div class="text-sm text-gray-600">Часов помощи</div>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-orange-100 rounded-full">
              <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14l7-7v10h4.5" />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ stats.active_projects }}</div>
              <div class="text-sm text-gray-600">Активных проектов</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div class="flex items-center mb-4">
            <div class="p-2 bg-primary-100 rounded-full">
              <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900">Создать проект</h3>
          </div>
          <p class="text-gray-600 text-sm mb-4">
            Запустите новый волонтерский проект
          </p>
          <router-link to="/projects/create" class="btn btn-primary w-full">
            Создать проект
          </router-link>
        </div>

        <div class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div class="flex items-center mb-4">
            <div class="p-2 bg-green-100 rounded-full">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900">Заявки</h3>
          </div>
          <p class="text-gray-600 text-sm mb-4">
            Управляйте заявками на ваши проекты
          </p>
          <router-link to="/applications/organization" class="btn btn-outline w-full">
            Мои заявки
          </router-link>
        </div>

        <div class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div class="flex items-center mb-4">
            <div class="p-2 bg-blue-100 rounded-full">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v1a1 1 0 001 1h4a1 1 0 001-1v-1m3-2V8a2 2 0 00-2-2H8a2 2 0 00-2 2v7m3-2h6" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900">Отчеты</h3>
          </div>
          <p class="text-gray-600 text-sm mb-4">
            Создавайте отчеты по проектам
          </p>
          <router-link to="/reports" class="btn btn-outline w-full">
            Отчеты
          </router-link>
        </div>
      </div>

      <!-- Recent Projects -->
      <div class="bg-white rounded-lg shadow mb-8">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold text-gray-900">Мои проекты</h2>
            <router-link to="/projects/create" class="btn btn-primary">
              Создать проект
            </router-link>
          </div>
        </div>

        <div class="p-6">
          <!-- Loading State -->
          <div v-if="projectsLoading" class="text-center py-8">
            <div class="loading-spinner w-8 h-8 mx-auto mb-4"></div>
            <p class="text-gray-600">Загрузка проектов...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="projects.length === 0" class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">У вас пока нет проектов</h3>
            <p class="mt-1 text-sm text-gray-500">
              Создайте свой первый волонтерский проект
            </p>
            <div class="mt-6">
              <router-link to="/projects/create" class="btn btn-primary">
                Создать проект
              </router-link>
            </div>
          </div>

          <!-- Projects List -->
          <div v-else class="space-y-4">
            <div
              v-for="project in projects"
              :key="project.id"
              class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-2">
                    <span :class="getStatusBadgeClass(project.status)">
                      {{ getStatusDisplay(project.status) }}
                    </span>
                    <span class="badge badge-primary text-xs">
                      {{ project.category.name }}
                    </span>
                    <span class="text-sm text-gray-500">
                      {{ formatDate(project.created_at) }}
                    </span>
                  </div>
                  
                  <h3 class="text-lg font-medium text-gray-900 mb-2">
                    {{ project.title }}
                  </h3>
                  <p class="text-gray-600 text-sm mb-3 line-clamp-2">
                    {{ project.description }}
                  </p>
                  
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4 text-sm text-gray-500">
                      <span>{{ project.volunteers_needed }} волонтеров</span>
                      <span>{{ project.volunteers_remaining }} свободных мест</span>
                      <span v-if="project.region">{{ project.region.name }}</span>
                    </div>
                    
                    <div class="w-32 bg-gray-200 rounded-full h-2">
                      <div
                        class="bg-primary-600 h-2 rounded-full"
                        :style="{ width: `${getProgressPercentage(project)}%` }"
                      ></div>
                    </div>
                  </div>
                </div>
                
                <div class="flex items-center space-x-2 ml-4">
                  <router-link
                    :to="`/projects/${project.id}`"
                    class="btn btn-outline text-sm"
                  >
                    Подробнее
                  </router-link>
                  <router-link
                    :to="`/projects/${project.id}/edit`"
                    class="btn btn-outline text-sm"
                  >
                    Редактировать
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Applications -->
      <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold text-gray-900">Последние заявки</h2>
            <router-link to="/applications/organization" class="btn btn-outline">
              Все заявки
            </router-link>
          </div>
        </div>

        <div class="p-6">
          <!-- Loading State -->
          <div v-if="applicationsLoading" class="text-center py-8">
            <div class="loading-spinner w-8 h-8 mx-auto mb-4"></div>
            <p class="text-gray-600">Загрузка заявок...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="applications.length === 0" class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2z" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">Заявок пока нет</h3>
            <p class="mt-1 text-sm text-gray-500">
              Волонтеры еще не подали заявки на ваши проекты
            </p>
          </div>

          <!-- Applications List -->
          <div v-else class="space-y-4">
            <div
              v-for="application in applications"
              :key="application.id"
              class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-2">
                    <span :class="getStatusBadgeClass(application.status)">
                      {{ getStatusDisplay(application.status) }}
                    </span>
                    <span class="text-sm text-gray-500">
                      {{ formatDate(application.created_at) }}
                    </span>
                  </div>
                  
                  <h3 class="text-lg font-medium text-gray-900 mb-2">
                    {{ application.project.title }}
                  </h3>
                  <p class="text-gray-600 text-sm mb-2">
                    <strong>Волонтер:</strong> {{ application.volunteer.username }}
                  </p>
                  <p class="text-gray-600 text-sm mb-2 line-clamp-2">
                    {{ application.cover_letter }}
                  </p>
                  <div class="flex items-center text-sm text-gray-500">
                    <span class="mr-4">{{ application.hours_committed }} часов</span>
                    <span v-if="application.reviewed_by">
                      Отзыв: {{ application.reviewed_by.username }}
                    </span>
                  </div>
                </div>
                
                <div class="flex items-center space-x-2">
                  <button
                    v-if="application.status === 'pending'"
                    @click="approveApplication(application.id)"
                    class="btn btn-success text-sm"
                  >
                    Одобрить
                  </button>
                  <button
                    v-if="application.status === 'pending'"
                    @click="rejectApplication(application.id)"
                    class="btn btn-danger text-sm"
                  >
                    Отклонить
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import apiService from '@/services/api'
import type { Project, Application } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()

const stats = ref({
  total_projects: 0,
  total_applications: 0,
  approved_applications: 0,
  total_hours: 0,
  active_projects: 0
})

const projects = ref<Project[]>([])
const applications = ref<Application[]>([])
const projectsLoading = ref(false)
const applicationsLoading = ref(false)
const unreadCount = ref(0)

onMounted(async () => {
  await Promise.all([
    loadStats(),
    loadProjects(),
    loadApplications(),
    loadUnreadCount()
  ])
})

const loadStats = async () => {
  try {
    const data = await apiService.getStatistics()
    stats.value = data
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const loadProjects = async () => {
  try {
    projectsLoading.value = true
    const response = await apiService.getProjects({ limit: 5 })
    projects.value = response.results
  } catch (error) {
    console.error('Failed to load projects:', error)
  } finally {
    projectsLoading.value = false
  }
}

const loadApplications = async () => {
  try {
    applicationsLoading.value = true
    const response = await apiService.getApplications({ limit: 5 })
    applications.value = response.results
  } catch (error) {
    console.error('Failed to load applications:', error)
  } finally {
    applicationsLoading.value = false
  }
}

const loadUnreadCount = async () => {
  try {
    const data = await apiService.getNotificationStats()
    unreadCount.value = data.unread
  } catch (error) {
    console.error('Failed to load unread count:', error)
  }
}

const getUserDisplayName = () => {
  if (!authStore.user) return ''
  
  const user = authStore.user
  if (user.organization_profile) {
    return user.organization_profile.name
  } else if (user.volunteer_profile) {
    return `${user.volunteer_profile.first_name} ${user.volunteer_profile.last_name}`
  }
  return user.email
}

const getStatusBadgeClass = (status: string) => {
  const statusClasses = {
    active: 'badge-success',
    draft: 'badge-gray',
    completed: 'badge-primary',
    cancelled: 'badge-danger',
    pending: 'badge-warning',
    approved: 'badge-success',
    rejected: 'badge-danger',
    cancelled: 'badge-gray'
  }
  return statusClasses[status as keyof typeof statusClasses] || 'badge-gray'
}

const getStatusDisplay = (status: string) => {
  const statusMap = {
    active: 'Активный',
    draft: 'Черновик',
    completed: 'Завершен',
    cancelled: 'Отменен',
    pending: 'На рассмотрении',
    approved: 'Одобрено',
    rejected: 'Отклонено'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const getProgressPercentage = (project: Project) => {
  return ((project.volunteers_needed - project.volunteers_remaining) / project.volunteers_needed) * 100
}

const approveApplication = async (applicationId: number) => {
  try {
    await apiService.approveApplication(applicationId)
    
    // Update local applications list
    const index = applications.value.findIndex(app => app.id === applicationId)
    if (index > -1) {
      applications.value[index].status = 'approved'
    }
  } catch (error) {
    console.error('Failed to approve application:', error)
  }
}

const rejectApplication = async (applicationId: number) => {
  try {
    await apiService.rejectApplication(applicationId)
    
    // Update local applications list
    const index = applications.value.findIndex(app => app.id === applicationId)
    if (index > -1) {
      applications.value[index].status = 'rejected'
    }
  } catch (error) {
    console.error('Failed to reject application:', error)
  }
}
</script>
