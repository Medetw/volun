<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="container-custom py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">
              Админ панель
            </h1>
            <p class="text-gray-600 mt-1">
              Управление платформой
            </p>
          </div>
          
          <div class="flex items-center space-x-4">
            <router-link
              to="/profile"
              class="btn btn-outline"
            >
              Профиль
            </router-link>
            <router-link
              to="/notifications"
              class="btn btn-outline relative"
            >
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

    <!-- Main Content -->
    <div class="container-custom py-8">
      <!-- Stats Overview -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
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
                  d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">
                {{ stats.users.total }}
              </div>
              <div class="text-sm text-gray-600">
                Пользователей
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
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">
                {{ stats.projects.total }}
              </div>
              <div class="text-sm text-gray-600">
                Проектов
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-purple-100 rounded-full">
              <svg
                class="w-6 h-6 text-purple-600"
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
                {{ stats.applications.total }}
              </div>
              <div class="text-sm text-gray-600">
                Заявок
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-orange-100 rounded-full">
              <svg
                class="w-6 h-6 text-orange-600"
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
                {{ stats.applications.total_hours }}
              </div>
              <div class="text-sm text-gray-600">
                Часов помощи
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div class="flex items-center mb-4">
            <div class="p-2 bg-blue-100 rounded-full">
              <svg
                class="w-5 h-5 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900">
              Пользователи
            </h3>
          </div>
          <p class="text-gray-600 text-sm mb-4">
            Управление пользователями
          </p>
          <router-link
            to="/admin/users"
            class="btn btn-primary w-full"
          >
            Управление
          </router-link>
        </div>

        <div class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div class="flex items-center mb-4">
            <div class="p-2 bg-green-100 rounded-full">
              <svg
                class="w-5 h-5 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900">
              Проекты
            </h3>
          </div>
          <p class="text-gray-600 text-sm mb-4">
            Модерация проектов
          </p>
          <router-link
            to="/admin/projects"
            class="btn btn-outline w-full"
          >
            Модерация
          </router-link>
        </div>

        <div class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div class="flex items-center mb-4">
            <div class="p-2 bg-purple-100 rounded-full">
              <svg
                class="w-5 h-5 text-purple-600"
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
            <h3 class="text-lg font-semibold text-gray-900">
              Заявки
            </h3>
          </div>
          <p class="text-gray-600 text-sm mb-4">
            Управление заявками
          </p>
          <router-link
            to="/admin/applications"
            class="btn btn-outline w-full"
          >
            Управление
          </router-link>
        </div>

        <div class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div class="flex items-center mb-4">
            <div class="p-2 bg-orange-100 rounded-full">
              <svg
                class="w-5 h-5 text-orange-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 17v1a1 1 0 001 1h4a1 1 0 001-1v-1m3-2V8a2 2 0 00-2-2H8a2 2 0 00-2 2v7m3-2h6"
                />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900">
              Отчеты
            </h3>
          </div>
          <p class="text-gray-600 text-sm mb-4">
            Аналитика и отчеты
          </p>
          <router-link
            to="/reports"
            class="btn btn-outline w-full"
          >
            Отчеты
          </router-link>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- User Growth Chart -->
        <div class="bg-white p-6 rounded-lg shadow">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">
            Рост пользователей
          </h2>
          <div class="h-64 flex items-center justify-center bg-gray-50 rounded">
            <div class="text-center text-gray-500">
              <svg
                class="w-16 h-16 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              <p>График роста пользователей</p>
            </div>
          </div>
        </div>

        <!-- Project Status Chart -->
        <div class="bg-white p-6 rounded-lg shadow">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">
            Статус проектов
          </h2>
          <div class="h-64 flex items-center justify-center bg-gray-50 rounded">
            <div class="text-center text-gray-500">
              <svg
                class="w-16 h-16 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"
                />
              </svg>
              <p>Диаграмма статусов проектов</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-xl font-semibold text-gray-900">
            Последняя активность
          </h2>
        </div>

        <div class="p-6">
          <!-- Loading State -->
          <div
            v-if="activityLoading"
            class="text-center py-8"
          >
            <div class="loading-spinner w-8 h-8 mx-auto mb-4" />
            <p class="text-gray-600">
              Загрузка активности...
            </p>
          </div>

          <!-- Activity List -->
          <div
            v-else
            class="space-y-4"
          >
            <div
              v-for="activity in recentActivity"
              :key="activity.id"
              class="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg"
            >
              <div class="flex-shrink-0">
                <div :class="getActivityIconClass(activity.type)">
                  <svg
                    class="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M13 10V3L4 14l7-7v10h4.5"
                    />
                  </svg>
                </div>
              </div>
              <div class="flex-1">
                <p class="text-sm text-gray-900">
                  <span class="font-medium">{{ activity.user }}</span>
                  {{ getActivityDescription(activity) }}
                </p>
                <p class="text-xs text-gray-500 mt-1">
                  {{ formatDate(activity.created_at) }}
                </p>
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

const authStore = useAuthStore()

const stats = ref({
  users: { total: 0 },
  projects: { total: 0 },
  applications: { total: 0, total_hours: 0 }
})

const recentActivity = ref([])
const activityLoading = ref(false)
const unreadCount = ref(0)

onMounted(async () => {
  await Promise.all([
    loadStats(),
    loadRecentActivity(),
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

const loadRecentActivity = async () => {
  try {
    activityLoading.value = true
    // Mock data for now - replace with actual API call
    recentActivity.value = [
      {
        id: 1,
        user: 'Иван Иванов',
        type: 'user_registered',
        description: 'зарегистрировался как волонтер',
        created_at: new Date().toISOString()
      },
      {
        id: 2,
        user: 'ООО "Добрые дела"',
        type: 'project_created',
        description: 'создал проект "Помощь животным"',
        created_at: new Date(Date.now() - 3600000).toISOString()
      },
      {
        id: 3,
        user: 'Мария Петрова',
        type: 'application_submitted',
        description: 'подала заявку на проект "Экологическая акция"',
        created_at: new Date(Date.now() - 7200000).toISOString()
      }
    ]
  } catch (error) {
    console.error('Failed to load recent activity:', error)
  } finally {
    activityLoading.value = false
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

const getActivityIconClass = (type: string) => {
  const iconClasses = {
    user_registered: 'p-2 bg-blue-100 rounded-full text-blue-600',
    project_created: 'p-2 bg-green-100 rounded-full text-green-600',
    application_submitted: 'p-2 bg-purple-100 rounded-full text-purple-600',
    application_approved: 'p-2 bg-green-100 rounded-full text-green-600',
    application_rejected: 'p-2 bg-red-100 rounded-full text-red-600'
  }
  return iconClasses[type as keyof typeof iconClasses] || 'p-2 bg-gray-100 rounded-full text-gray-600'
}

const getActivityDescription = (activity: any) => {
  return activity.description
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
