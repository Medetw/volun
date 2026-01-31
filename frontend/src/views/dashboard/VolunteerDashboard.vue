<template>
  <div class="min-h-screen bg-gray-50">
    <div class="bg-white shadow-sm border-b">
      <div class="container-custom py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Панель волонтера</h1>
            <p class="text-gray-600 mt-1">Добро пожаловать, {{ getUserDisplayName() }}!</p>
          </div>
          <div class="flex items-center space-x-4">
            <router-link to="/profile" class="btn btn-outline">
              Профиль
            </router-link>
            <router-link to="/notifications" class="btn btn-outline relative">
              Уведомления
              <span
                v-if="unreadCount > 0"
                class="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center"
              >
                {{ unreadCount }}
              </span>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <div class="container-custom py-8">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-blue-100 rounded-full">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div class="ml-4">
              <div class="text-2xl font-bold text-gray-900">{{ stats.total_applications }}</div>
              <div class="text-sm text-gray-600">Мои заявки</div>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-green-100 rounded-full">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div class="ml-4">
              <div class="text-2xl font-bold text-gray-900">{{ stats.approved_applications }}</div>
              <div class="text-sm text-gray-600">Одобрено</div>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-purple-100 rounded-full">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h8M8 16h8M8 8h8M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="ml-4">
              <div class="text-2xl font-bold text-gray-900">{{ stats.hours_committed }}</div>
              <div class="text-sm text-gray-600">Часов обещано</div>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900">Мои заявки</h2>
          <router-link to="/applications/my" class="btn btn-outline">
            Все заявки
          </router-link>
        </div>
        <div class="p-6">
          <div v-if="applicationsLoading" class="text-center py-8">
            <div class="loading-spinner w-8 h-8 mx-auto mb-4"></div>
            <p class="text-gray-600">Загрузка заявок...</p>
          </div>

          <div v-else-if="applications.length === 0" class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2z" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">Заявок пока нет</h3>
            <p class="mt-1 text-sm text-gray-500">Вы еще не подали заявки на проекты</p>
            <div class="mt-6">
              <router-link to="/projects" class="btn btn-primary">
                Найти проекты
              </router-link>
            </div>
          </div>

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
                  <p class="text-gray-600 text-sm line-clamp-2">
                    {{ application.cover_letter }}
                  </p>
                </div>
                <router-link
                  :to="`/projects/${application.project.id}`"
                  class="btn btn-outline text-sm"
                >
                  Проект
                </router-link>
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
import { useAuthStore } from '@/stores/auth'
import apiService from '@/services/api'
import type { Application } from '@/types/api'

const authStore = useAuthStore()

const stats = ref({
  total_applications: 0,
  approved_applications: 0,
  hours_committed: 0
})

const applications = ref<Application[]>([])
const applicationsLoading = ref(false)
const unreadCount = ref(0)

onMounted(async () => {
  await Promise.all([loadStats(), loadApplications(), loadUnreadCount()])
})

const loadStats = async () => {
  try {
    const data = await apiService.getStatistics()
    stats.value = {
      total_applications: data.total_applications ?? 0,
      approved_applications: data.approved_applications ?? 0,
      hours_committed: data.total_hours ?? 0
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
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
  if (user.volunteer_profile) {
    return `${user.volunteer_profile.first_name} ${user.volunteer_profile.last_name}`
  }
  return user.email
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
    year: 'numeric'
  })
}
</script>
