<template>
  <header class="bg-white shadow-sm border-b border-yellow-200">
    <div class="container-custom">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <router-link
          to="/"
          class="flex items-center space-x-2"
        >
          <div class="w-8 h-8 bg-yellow-400 rounded-lg flex items-center justify-center">
            <img src="@/assets/logo_Newman.jpeg" alt="Logo" class="w-8 h-8 object-cover rounded-lg" />
          </div>
          <span class="text-xl font-bold text-gray-900">NEWMAN</span>
        </router-link>

        <!-- Navigation -->
        <nav class="hidden md:flex space-x-8">
          <router-link
            to="/"
            class="nav-link"
            :class="{ 'nav-link-active': $route.name === 'Home' }"
          >
            Главная
          </router-link>
          <router-link
            to="/projects"
            class="nav-link"
            :class="{ 'nav-link-active': $route.name === 'ProjectsList' }"
          >
            Проекты
          </router-link>
          <router-link
            to="/news"
            class="nav-link"
            :class="{ 'nav-link-active': $route.name === 'NewsList' }"
          >
            Новости
          </router-link>
          <!-- Admin / Moderator only (Block 6) -->
          <router-link
            v-if="authStore.isAdmin || authStore.isModerator"
            to="/volunteers"
            class="nav-link"
            :class="{ 'nav-link-active': $route.name === 'VolunteersTable' }"
          >
            Волонтёры
          </router-link>
        </nav>

        <!-- User menu -->
        <div class="flex items-center space-x-4">
          <!-- Notifications -->
          <div
            v-if="authStore.isAuthenticated"
            class="relative"
          >
            <button
              class="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-full"
              @click="showNotifications = !showNotifications"
            >
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
                  d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                />
              </svg>
              <span
                v-if="unreadCount > 0"
                class="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400"
              />
            </button>
            
            <!-- Notifications dropdown -->
            <div
              v-if="showNotifications"
              class="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
            >
              <div class="p-4 border-b border-gray-200">
                <h3 class="text-sm font-medium text-gray-900">
                  Уведомления
                </h3>
              </div>
              <div class="max-h-64 overflow-y-auto">
                <div
                  v-if="notifications.length === 0"
                  class="p-4 text-center text-gray-500"
                >
                  Нет уведомлений
                </div>
                <div v-else>
                  <div
                    v-for="notification in notifications"
                    :key="notification.id"
                    class="p-4 hover:bg-gray-50 border-b border-gray-100"
                  >
                    <p class="text-sm font-medium text-gray-900">
                      {{ notification.title }}
                    </p>
                    <p class="text-sm text-gray-600">
                      {{ notification.message }}
                    </p>
                    <p class="text-xs text-gray-400 mt-1">
                      {{ formatDate(notification.created_at) }}
                    </p>
                  </div>
                </div>
              </div>
              <div class="p-4 border-t border-gray-200">
                <router-link
                  to="/notifications"
                  class="text-sm text-primary-600 hover:text-primary-800"
                >
                  Все уведомления
                </router-link>
              </div>
            </div>
          </div>

          <!-- User menu -->
          <div
            v-if="authStore.isAuthenticated"
            class="relative"
          >
            <button
              class="flex items-center space-x-2 text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-full p-1"
              @click="showUserMenu = !showUserMenu"
            >
              <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center overflow-hidden">
                <img
                  v-if="authStore.user?.avatar"
                  :src="authStore.user.avatar"
                  alt="Аватар"
                  class="w-full h-full object-cover"
                >
                <span
                  v-else
                  class="text-sm font-medium text-gray-700"
                >
                  {{ getUserInitials() }}
                </span>
              </div>
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
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            <!-- User dropdown -->
            <div
              v-if="showUserMenu"
              class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
            >
              <div class="p-4 border-b border-gray-200">
                <p class="text-sm font-medium text-gray-900">
                  {{ getUserDisplayName() }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ getUserRole() }}
                </p>
              </div>
              <div class="py-2">
                <router-link
                  to="/profile"
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Профиль
                </router-link>
                <router-link
                  to="/dashboard"
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Личный кабинет
                </router-link>
                <button
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  @click="handleLogout"
                >
                  Выйти
                </button>
              </div>
            </div>
          </div>

          <!-- Auth buttons -->
          <div
            v-else
            class="flex items-center space-x-4"
          >
            <router-link
              to="/login"
              class="btn btn-ghost"
            >
              Войти
            </router-link>
            <router-link
              to="/register/volunteer"
              class="btn btn-primary"
            >
              Стать волонтером
            </router-link>
          </div>

          <!-- Mobile menu button -->
          <button
            class="md:hidden p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-md"
            @click="showMobileMenu = !showMobileMenu"
          >
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
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile menu -->
      <div
        v-if="showMobileMenu"
        class="md:hidden border-t border-yellow-200"
      >
        <div class="px-2 pt-2 pb-3 space-y-1">
          <router-link
            to="/"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-yellow-50"
          >
            Главная
          </router-link>
          <router-link
            to="/projects"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-yellow-50"
          >
            Проекты
          </router-link>
          <router-link
            to="/news"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-yellow-50"
          >
            Новости
          </router-link>
        </div>
        <div
          v-if="!authStore.isAuthenticated"
          class="pt-4 pb-3 border-t border-yellow-200"
        >
          <div class="px-2 space-y-1">
            <router-link
              to="/login"
              class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-yellow-50"
            >
              Войти
            </router-link>
            <router-link
              to="/register/volunteer"
              class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-yellow-50"
            >
              Стать волонтером
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import apiService from '@/services/api'
import type { Notification } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()

const showMobileMenu = ref(false)
const showUserMenu = ref(false)
const showNotifications = ref(false)
const notifications = ref<Notification[]>([])
const unreadCount = ref(0)

// Close dropdowns when clicking outside
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showUserMenu.value = false
    showNotifications.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  if (authStore.isAuthenticated) {
    loadNotifications()
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const loadNotifications = async () => {
  try {
    const data = await apiService.getUnreadNotifications()
    notifications.value = data.slice(0, 5) // Show only 5 recent notifications
    unreadCount.value = data.length
  } catch (error) {
    console.error('Failed to load notifications:', error)
  }
}

const getUserInitials = () => {
  if (!authStore.user) return '?'

  const user = authStore.user
  if (user.volunteer_profile) {
    const first = (user.volunteer_profile.first_name || '').charAt(0)
    const last = (user.volunteer_profile.last_name || '').charAt(0)
    return (first + last).toUpperCase() || '?'
  } else if (user.organization_profile) {
    return (user.organization_profile.name || '').charAt(0).toUpperCase() || '?'
  }
  return (user.email || '').charAt(0).toUpperCase() || '?'
}

const getUserDisplayName = () => {
  if (!authStore.user) return ''
  
  const user = authStore.user
  if (user.volunteer_profile) {
    return `${user.volunteer_profile.first_name} ${user.volunteer_profile.last_name}`
  } else if (user.organization_profile) {
    return user.organization_profile.name
  }
  return user.email
}

const getUserRole = () => {
  if (!authStore.user) return ''
  
  const roles: Record<string, string> = {
    volunteer: 'Волонтер',
    organization: 'Организация',
    moderator: 'Модератор',
    admin: 'Администратор'
  }
  return roles[authStore.user.role] || ''
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
  
  if (diffInHours < 1) {
    return 'Только что'
  } else if (diffInHours < 24) {
    return `${diffInHours} ч. назад`
  } else {
    const diffInDays = Math.floor(diffInHours / 24)
    return `${diffInDays} д. назад`
  }
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}
</script>
