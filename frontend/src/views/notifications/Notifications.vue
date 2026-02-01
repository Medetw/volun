<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="container-custom py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">
              Уведомления
            </h1>
            <p class="text-gray-600 mt-1">
              Будьте в курсе важных событий
            </p>
          </div>
          
          <div class="flex items-center space-x-4">
            <button
              :disabled="markingAll"
              class="btn btn-outline"
              @click="markAllAsRead"
            >
              {{ markingAll ? 'Обработка...' : 'Отметить все прочитанными' }}
            </button>
          </div>
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
                  d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">
                {{ stats.total }}
              </div>
              <div class="text-sm text-gray-600">
                Всего уведомлений
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
                  d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">
                {{ stats.unread }}
              </div>
              <div class="text-sm text-gray-600">
                Непрочитанных
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
                {{ stats.read }}
              </div>
              <div class="text-sm text-gray-600">
                Прочитанных
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
                  d="M13 10V3L4 14l7-7v10h4.5"
                />
              </svg>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">
                {{ stats.today }}
              </div>
              <div class="text-sm text-gray-600">
                Сегодня
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white p-4 rounded-lg shadow mb-6">
        <div class="flex flex-wrap items-center gap-4">
          <div>
            <label class="form-label text-sm">Тип</label>
            <select
              v-model="filters.type"
              class="form-input"
              @change="loadNotifications"
            >
              <option value="">
                Все типы
              </option>
              <option value="application">
                Заявки
              </option>
              <option value="project">
                Проекты
              </option>
              <option value="system">
                Системные
              </option>
              <option value="news">
                Новости
              </option>
              <option value="reminder">
                Напоминания
              </option>
            </select>
          </div>
          
          <div>
            <label class="form-label text-sm">Статус</label>
            <select
              v-model="filters.is_read"
              class="form-input"
              @change="loadNotifications"
            >
              <option value="">
                Все статусы
              </option>
              <option value="false">
                Непрочитанные
              </option>
              <option value="true">
                Прочитанные
              </option>
            </select>
          </div>
          
          <div>
            <label class="form-label text-sm">Сортировка</label>
            <select
              v-model="filters.ordering"
              class="form-input"
              @change="loadNotifications"
            >
              <option value="-created_at">
                Новые сначала
              </option>
              <option value="created_at">
                Старые сначала
              </option>
              <option value="-read_at">
                Недавно прочитанные
              </option>
            </select>
          </div>
          
          <div class="flex-1">
            <label class="form-label text-sm">Поиск</label>
            <input
              v-model="filters.search"
              type="text"
              placeholder="Поиск по заголовку или содержимому..."
              class="form-input"
              @input="debouncedSearch"
            >
          </div>
        </div>
      </div>

      <!-- Notifications List -->
      <div class="bg-white rounded-lg shadow">
        <!-- Loading State -->
        <div
          v-if="loading"
          class="text-center py-12"
        >
          <div class="loading-spinner w-8 h-8 mx-auto mb-4" />
          <p class="text-gray-600">
            Загрузка уведомлений...
          </p>
        </div>

        <!-- Empty State -->
        <div
          v-else-if="notifications.length === 0"
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
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
            />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">
            Уведомлений пока нет
          </h3>
          <p class="mt-1 text-sm text-gray-500">
            Вы будете получать уведомления о важных событиях
          </p>
        </div>

        <!-- Notifications Grid -->
        <div
          v-else
          class="divide-y divide-gray-200"
        >
          <div
            v-for="notification in notifications"
            :key="notification.id"
            :class="[
              'p-6 hover:bg-gray-50 transition-colors cursor-pointer',
              !notification.is_read ? 'bg-blue-50 border-l-4 border-blue-400' : ''
            ]"
            @click="handleNotificationClick(notification)"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-start space-x-4 flex-1">
                <!-- Icon -->
                <div :class="getNotificationIconClass(notification.type)">
                  <svg
                    class="w-6 h-6"
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
                
                <!-- Content -->
                <div class="flex-1">
                  <div class="flex items-center justify-between mb-2">
                    <h3 class="text-lg font-medium text-gray-900">
                      {{ notification.title }}
                    </h3>
                    <div class="flex items-center space-x-2">
                      <span
                        v-if="!notification.is_read"
                        class="w-2 h-2 bg-blue-500 rounded-full"
                      />
                      <span class="text-sm text-gray-500">
                        {{ formatDate(notification.created_at) }}
                      </span>
                    </div>
                  </div>
                  
                  <p class="text-gray-600 mb-3">
                    {{ notification.message }}
                  </p>
                  
                  <!-- Action Button -->
                  <div
                    v-if="notification.action_url"
                    class="mt-3"
                  >
                    <router-link
                      :to="notification.action_url"
                      class="btn btn-primary text-sm"
                      @click.stop
                    >
                      {{ getActionText(notification.action_url) }}
                    </router-link>
                  </div>
                </div>
              </div>
              
              <!-- Actions -->
              <div class="flex items-center space-x-2 ml-4">
                <button
                  v-if="!notification.is_read"
                  :disabled="marking"
                  class="btn btn-outline text-sm"
                  title="Отметить как прочитанное"
                  @click.stop="markAsRead(notification.id)"
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
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </button>
                
                <button
                  :disabled="deleting"
                  class="btn btn-outline text-sm text-red-600 hover:text-red-700"
                  title="Удалить"
                  @click.stop="deleteNotification(notification.id)"
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
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
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
              Показано {{ pagination.start }}-{{ pagination.end }} из {{ pagination.total }} уведомлений
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
import type { Notification } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()

const notifications = ref<Notification[]>([])
const loading = ref(false)
const marking = ref(false)
const markingAll = ref(false)
const deleting = ref(false)

const stats = ref({
  total: 0,
  unread: 0,
  read: 0,
  today: 0
})

const filters = reactive({
  type: '',
  is_read: '',
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

onMounted(async () => {
  await Promise.all([
    loadNotifications(),
    loadStats()
  ])
})

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    pagination.currentPage = 1
    loadNotifications()
  }, 500)
}

const loadNotifications = async () => {
  try {
    loading.value = true
    
    const params = {
      ...filters,
      page: pagination.currentPage
    }
    
    const response = await apiService.getNotifications(params)
    notifications.value = response.results
    
    // Update pagination
    pagination.total = response.count
    pagination.totalPages = Math.ceil(response.count / 10) // 10 items per page
    pagination.start = (pagination.currentPage - 1) * 10 + 1
    pagination.end = Math.min(pagination.currentPage * 10, response.count)
    
    // Generate page numbers
    generatePageNumbers()
  } catch (error) {
    console.error('Failed to load notifications:', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const data = await apiService.getNotificationStats()
    stats.value = data
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
    loadNotifications()
  }
}

const handleNotificationClick = async (notification: Notification) => {
  if (!notification.is_read) {
    await markAsRead(notification.id)
  }
  
  if (notification.action_url) {
    router.push(notification.action_url)
  }
}

const markAsRead = async (notificationId: number) => {
  try {
    marking.value = true
    await apiService.markNotificationAsRead(notificationId)
    
    // Update local notification
    const index = notifications.value.findIndex(n => n.id === notificationId)
    if (index > -1) {
      notifications.value[index].is_read = true
      notifications.value[index].read_at = new Date().toISOString()
    }
    
    // Update stats
    await loadStats()
  } catch (error) {
    console.error('Failed to mark notification as read:', error)
  } finally {
    marking.value = false
  }
}

const markAllAsRead = async () => {
  try {
    markingAll.value = true
    await apiService.markAllNotificationsAsRead()
    
    // Update all notifications
    notifications.value.forEach(notification => {
      notification.is_read = true
      notification.read_at = new Date().toISOString()
    })
    
    // Update stats
    await loadStats()
  } catch (error) {
    console.error('Failed to mark all notifications as read:', error)
  } finally {
    markingAll.value = false
  }
}

const deleteNotification = async (notificationId: number) => {
  if (!confirm('Вы уверены, что хотите удалить это уведомление?')) {
    return
  }
  
  try {
    deleting.value = true
    await apiService.deleteNotification(notificationId)
    
    // Remove from local list
    notifications.value = notifications.value.filter(n => n.id !== notificationId)
    
    // Update stats
    await loadStats()
  } catch (error) {
    console.error('Failed to delete notification:', error)
  } finally {
    deleting.value = false
  }
}

const getNotificationIconClass = (type: string) => {
  const iconClasses = {
    application: 'p-3 bg-blue-100 rounded-full text-blue-600',
    project: 'p-3 bg-green-100 rounded-full text-green-600',
    system: 'p-3 bg-purple-100 rounded-full text-purple-600',
    news: 'p-3 bg-yellow-100 rounded-full text-yellow-600',
    reminder: 'p-3 bg-orange-100 rounded-full text-orange-600'
  }
  return iconClasses[type as keyof typeof iconClasses] || 'p-3 bg-gray-100 rounded-full text-gray-600'
}

const getActionText = (actionUrl: string) => {
  if (actionUrl.includes('/projects/')) return 'Перейти к проекту'
  if (actionUrl.includes('/applications/')) return 'Перейти к заявкам'
  if (actionUrl.includes('/profile')) return 'Перейти в профиль'
  if (actionUrl.includes('/news/')) return 'Читать новость'
  return 'Подробнее'
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  
  if (hours < 1) {
    const minutes = Math.floor(diff / (1000 * 60))
    return `${minutes} минут назад`
  } else if (hours < 24) {
    return `${hours} часов назад`
  } else if (hours < 48) {
    return 'Вчера'
  } else {
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  }
}
</script>
