<template>
  <div class="min-h-screen bg-gray-50 py-6">
    <div class="container-custom max-w-7xl">
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div>
          <div class="flex items-center gap-3">
            <router-link
              to="/dashboard/admin"
              class="text-gray-400 hover:text-gray-600 transition-colors"
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
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
            </router-link>
            <h1 class="text-2xl font-bold text-gray-900">
              Управление пользователями
            </h1>
          </div>
          <p class="text-gray-600 mt-1">
            Просмотр, модерация, блокировка и верификация организаций
          </p>
        </div>

        <div class="flex items-center gap-2">
          <router-link
            to="/admin/moderators"
            class="btn btn-outline text-sm"
          >
            🛡 Модераторы
          </router-link>
          <router-link
            to="/volunteers"
            class="btn btn-outline text-sm"
          >
            🙋 Таблица волонтёров
          </router-link>
          <a
            href="/admin/"
            target="_blank"
            class="btn btn-secondary text-sm bg-gray-800 hover:bg-gray-900 text-white"
          >
            ⚙️ Django Admin (БД)
          </a>
        </div>
      </div>

      <!-- Quick Stats -->
      <div
        v-if="stats"
        class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-6"
      >
        <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
          <div class="text-xs text-gray-500 uppercase font-medium">Всего</div>
          <div class="text-2xl font-bold text-gray-900 mt-1">{{ stats.total_users }}</div>
        </div>
        <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
          <div class="text-xs text-gray-500 uppercase font-medium">Волонтёры</div>
          <div class="text-2xl font-bold text-primary-600 mt-1">{{ stats.volunteers }}</div>
        </div>
        <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
          <div class="text-xs text-gray-500 uppercase font-medium">Организации</div>
          <div class="text-2xl font-bold text-indigo-600 mt-1">{{ stats.organizations }}</div>
        </div>
        <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
          <div class="text-xs text-gray-500 uppercase font-medium">Верифицированы</div>
          <div class="text-2xl font-bold text-green-600 mt-1">{{ stats.verified_organizations }}</div>
        </div>
        <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
          <div class="text-xs text-gray-500 uppercase font-medium">Активные</div>
          <div class="text-2xl font-bold text-emerald-600 mt-1">{{ stats.active_users }}</div>
        </div>
        <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
          <div class="text-xs text-gray-500 uppercase font-medium">Заблокированы</div>
          <div class="text-2xl font-bold text-red-600 mt-1">{{ stats.blocked_users }}</div>
        </div>
      </div>

      <!-- Messages -->
      <div
        v-if="message"
        class="mb-4 p-3 bg-green-50 border border-green-200 rounded text-sm text-green-700 flex justify-between items-center"
      >
        <span>{{ message }}</span>
        <button
          class="text-green-800 font-bold"
          @click="message = ''"
        >
          &times;
        </button>
      </div>
      <div
        v-if="errorMsg"
        class="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700 flex justify-between items-center"
      >
        <span>{{ errorMsg }}</span>
        <button
          class="text-red-800 font-bold"
          @click="errorMsg = ''"
        >
          &times;
        </button>
      </div>

      <!-- Filters & Search -->
      <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100 mb-6 flex flex-col md:flex-row gap-3 items-center justify-between">
        <div class="flex flex-wrap gap-2 w-full md:w-auto">
          <!-- Role filter tabs -->
          <button
            type="button"
            class="px-3 py-1.5 text-xs font-medium rounded-full transition-colors"
            :class="selectedRole === '' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            @click="setRole('')"
          >
            Все роли
          </button>
          <button
            type="button"
            class="px-3 py-1.5 text-xs font-medium rounded-full transition-colors"
            :class="selectedRole === 'volunteer' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            @click="setRole('volunteer')"
          >
            Волонтёры
          </button>
          <button
            type="button"
            class="px-3 py-1.5 text-xs font-medium rounded-full transition-colors"
            :class="selectedRole === 'organization' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            @click="setRole('organization')"
          >
            Организации
          </button>
          <button
            type="button"
            class="px-3 py-1.5 text-xs font-medium rounded-full transition-colors"
            :class="selectedRole === 'moderator' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            @click="setRole('moderator')"
          >
            Модераторы
          </button>
          <button
            type="button"
            class="px-3 py-1.5 text-xs font-medium rounded-full transition-colors"
            :class="selectedRole === 'admin' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            @click="setRole('admin')"
          >
            Админы
          </button>
        </div>

        <div class="flex items-center gap-3 w-full md:w-auto">
          <!-- Status select -->
          <select
            v-model="selectedStatus"
            class="form-input text-xs py-1.5"
            @change="fetchUsers"
          >
            <option value="">Все статусы</option>
            <option value="true">Только активные</option>
            <option value="false">Заблокированные</option>
          </select>

          <!-- Search -->
          <div class="relative w-full md:w-64">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Поиск: логин, email, имя..."
              class="form-input pl-9 pr-3 text-xs py-1.5 w-full"
              @input="onSearchInput"
            >
            <svg
              class="absolute left-2.5 top-2 h-4 w-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
        </div>
      </div>

      <!-- Users Table -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div
          v-if="isLoading"
          class="p-8 text-center text-gray-500"
        >
          <svg
            class="animate-spin h-8 w-8 mx-auto text-primary-600 mb-2"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            />
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          Загрузка пользователей...
        </div>

        <div
          v-else-if="users.length === 0"
          class="p-8 text-center text-gray-500"
        >
          Пользователи не найдены
        </div>

        <div
          v-else
          class="overflow-x-auto"
        >
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Пользователь
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Роль
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Контакты
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Статус
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Регистрация
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="u in users"
                :key="u.id"
                :class="!u.is_active ? 'bg-red-50/40' : 'hover:bg-gray-50'"
              >
                <!-- User name & avatar -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-9 w-9 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-bold text-sm">
                      {{ (u.first_name || u.username || 'U')[0].toUpperCase() }}
                    </div>
                    <div class="ml-3">
                      <div class="text-sm font-medium text-gray-900">
                        {{ getUserDisplayName(u) }}
                      </div>
                      <div class="text-xs text-gray-500">
                        @{{ u.username }}
                      </div>
                    </div>
                  </div>
                </td>

                <!-- Role badge -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    class="px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full"
                    :class="getRoleBadgeClass(u.role)"
                  >
                    {{ getRoleTitle(u.role) }}
                  </span>
                  <span
                    v-if="u.role === 'organization' && u.organization_profile?.is_verified"
                    class="ml-1 text-xs text-green-600 font-semibold"
                    title="Верифицирована"
                  >
                    ✓
                  </span>
                </td>

                <!-- Email & phone -->
                <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-500">
                  <div>{{ u.email }}</div>
                  <div
                    v-if="u.phone"
                    class="text-gray-400"
                  >
                    {{ u.phone }}
                  </div>
                </td>

                <!-- Status badge -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    v-if="u.is_active"
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800"
                  >
                    Активен
                  </span>
                  <span
                    v-else
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800"
                  >
                    Заблокирован
                  </span>
                </td>

                <!-- Date joined -->
                <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-500">
                  {{ formatDate(u.date_joined) }}
                </td>

                <!-- Actions -->
                <td class="px-6 py-4 whitespace-nowrap text-right text-xs font-medium space-x-2">
                  <!-- Block / Unblock -->
                  <button
                    v-if="u.role !== 'admin'"
                    type="button"
                    class="inline-block px-2.5 py-1 rounded text-xs transition-colors"
                    :class="u.is_active ? 'bg-red-50 text-red-700 hover:bg-red-100 border border-red-200' : 'bg-green-50 text-green-700 hover:bg-green-100 border border-green-200'"
                    @click="toggleBlock(u)"
                  >
                    {{ u.is_active ? 'Заблокировать' : 'Разблокировать' }}
                  </button>

                  <!-- Verify / Revoke for organizations -->
                  <button
                    v-if="u.role === 'organization'"
                    type="button"
                    class="inline-block px-2.5 py-1 rounded text-xs transition-colors bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200"
                    @click="toggleOrgVerification(u)"
                  >
                    {{ u.organization_profile?.is_verified ? 'Отозвать верификацию' : 'Верифицировать' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div
          v-if="totalCount > pageSize"
          class="px-6 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500"
        >
          <div>
            Показано {{ users.length }} из {{ totalCount }}
          </div>
          <div class="flex gap-1">
            <button
              :disabled="currentPage === 1"
              class="px-2.5 py-1 rounded border border-gray-300 disabled:opacity-40"
              @click="goToPage(currentPage - 1)"
            >
              Назад
            </button>
            <span class="px-2.5 py-1">Стр. {{ currentPage }}</span>
            <button
              :disabled="currentPage * pageSize >= totalCount"
              class="px-2.5 py-1 rounded border border-gray-300 disabled:opacity-40"
              @click="goToPage(currentPage + 1)"
            >
              Вперёд
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

interface UserItem {
  id: number
  username: string
  email: string
  role: string
  first_name?: string
  last_name?: string
  phone?: string
  is_active: boolean
  date_joined?: string
  organization_profile?: {
    name?: string
    is_verified?: boolean
  }
}

interface StatsData {
  total_users: number
  active_users: number
  blocked_users: number
  volunteers: number
  organizations: number
  admins: number
  verified_organizations: number
}

const users = ref<UserItem[]>([])
const stats = ref<StatsData | null>(null)
const isLoading = ref(false)
const message = ref('')
const errorMsg = ref('')

const selectedRole = ref('')
const selectedStatus = ref('')
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

let searchDebounceTimer: any = null

const authHeader = () => {
  const token = localStorage.getItem('access_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const fetchStats = async () => {
  try {
    const res = await axios.get('/api/admin/users/stats/', {
      headers: authHeader()
    })
    stats.value = res.data
  } catch (err) {
    console.error('Failed to load stats', err)
  }
}

const fetchUsers = async () => {
  isLoading.value = true
  try {
    const params: Record<string, any> = {
      page: currentPage.value
    }
    if (selectedRole.value) params.role = selectedRole.value
    if (selectedStatus.value !== '') params.is_active = selectedStatus.value
    if (searchQuery.value) params.search = searchQuery.value

    const res = await axios.get('/api/admin/users/', {
      headers: authHeader(),
      params
    })

    if (Array.isArray(res.data)) {
      users.value = res.data
      totalCount.value = res.data.length
    } else if (res.data?.results) {
      users.value = res.data.results
      totalCount.value = res.data.count || res.data.results.length
    }
  } catch (err: any) {
    console.error('Failed to load users', err)
    errorMsg.value = err.response?.data?.error || 'Ошибка загрузки пользователей'
  } finally {
    isLoading.value = false
  }
}

const setRole = (role: string) => {
  selectedRole.value = role
  currentPage.value = 1
  fetchUsers()
}

const onSearchInput = () => {
  clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    currentPage.value = 1
    fetchUsers()
  }, 400)
}

const goToPage = (page: number) => {
  currentPage.value = page
  fetchUsers()
}

const toggleBlock = async (u: UserItem) => {
  const action = u.is_active ? 'block' : 'unblock'
  const actionTitle = u.is_active ? 'заблокировать' : 'разблокировать'
  if (!confirm(`Вы действительно хотите ${actionTitle} пользователя ${u.username}?`)) {
    return
  }

  try {
    await axios.post(`/api/admin/users/${u.id}/${action}/`, {}, {
      headers: authHeader()
    })
    u.is_active = !u.is_active
    message.value = `Пользователь ${u.username} успешно ${u.is_active ? 'разблокирован' : 'заблокирован'}`
    fetchStats()
  } catch (err: any) {
    errorMsg.value = err.response?.data?.error || 'Ошибка выполнения действия'
  }
}

const toggleOrgVerification = async (u: UserItem) => {
  const isVerified = u.organization_profile?.is_verified
  const action = isVerified ? 'revoke_verification' : 'verify_organization'
  const actionTitle = isVerified ? 'отозвать верификацию у' : 'верифицировать'
  if (!confirm(`Вы действительно хотите ${actionTitle} организации ${u.username}?`)) {
    return
  }

  try {
    await axios.post(`/api/admin/users/${u.id}/${action}/`, {}, {
      headers: authHeader()
    })
    if (u.organization_profile) {
      u.organization_profile.is_verified = !isVerified
    }
    message.value = `Верификация для ${u.username} обновлена`
    fetchStats()
  } catch (err: any) {
    errorMsg.value = err.response?.data?.error || 'Ошибка верификации'
  }
}

const getUserDisplayName = (u: UserItem) => {
  if (u.role === 'organization' && u.organization_profile?.name) {
    return u.organization_profile.name
  }
  if (u.first_name || u.last_name) {
    return `${u.first_name || ''} ${u.last_name || ''}`.trim()
  }
  return u.username
}

const getRoleTitle = (role: string) => {
  const map: Record<string, string> = {
    admin: 'Администратор',
    moderator: 'Модератор',
    organization: 'Организация',
    volunteer: 'Волонтёр'
  }
  return map[role] || role
}

const getRoleBadgeClass = (role: string) => {
  const map: Record<string, string> = {
    admin: 'bg-red-100 text-red-800',
    moderator: 'bg-yellow-100 text-yellow-800',
    organization: 'bg-indigo-100 text-indigo-800',
    volunteer: 'bg-blue-100 text-blue-800'
  }
  return map[role] || 'bg-gray-100 text-gray-800'
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  } catch {
    return dateStr
  }
}

onMounted(() => {
  fetchStats()
  fetchUsers()
})
</script>
