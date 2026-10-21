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
              Управление заявками
            </h1>
          </div>
          <p class="text-gray-600 mt-1">
            Все заявки волонтёров на участие в проектах платформы
          </p>
        </div>

        <div class="flex items-center gap-2">
          <router-link
            to="/volunteers"
            class="btn btn-outline text-sm"
          >
            Таблица волонтёров
          </router-link>
          <router-link
            to="/admin/projects"
            class="btn btn-outline text-sm"
          >
            Модерация проектов
          </router-link>
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
          <button
            type="button"
            class="px-3 py-1.5 text-xs font-medium rounded-full transition-colors"
            :class="selectedStatus === '' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            @click="setStatus('')"
          >
            Все заявки
          </button>
          <button
            type="button"
            class="px-3 py-1.5 text-xs font-medium rounded-full transition-colors"
            :class="selectedStatus === 'pending' ? 'bg-amber-600 text-white' : 'bg-amber-50 text-amber-700 hover:bg-amber-100'"
            @click="setStatus('pending')"
          >
            Ожидают решения
          </button>
          <button
            type="button"
            class="px-3 py-1.5 text-xs font-medium rounded-full transition-colors"
            :class="selectedStatus === 'approved' ? 'bg-green-600 text-white' : 'bg-green-50 text-green-700 hover:bg-green-100'"
            @click="setStatus('approved')"
          >
            Одобренные
          </button>
          <button
            type="button"
            class="px-3 py-1.5 text-xs font-medium rounded-full transition-colors"
            :class="selectedStatus === 'rejected' ? 'bg-red-600 text-white' : 'bg-red-50 text-red-700 hover:bg-red-100'"
            @click="setStatus('rejected')"
          >
            Отклонённые
          </button>
          <button
            type="button"
            class="px-3 py-1.5 text-xs font-medium rounded-full transition-colors"
            :class="selectedStatus === 'cancelled' ? 'bg-gray-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            @click="setStatus('cancelled')"
          >
            Отменённые
          </button>
        </div>

        <div class="relative w-full md:w-64">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск по заявкам..."
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

      <!-- Applications Table -->
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
          Загрузка заявок...
        </div>

        <div
          v-else-if="applications.length === 0"
          class="p-8 text-center text-gray-500"
        >
          Заявки не найдены
        </div>

        <div
          v-else
          class="overflow-x-auto"
        >
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Волонтёр
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Проект
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Сопроводительное письмо
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Часы
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Статус
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="app in applications"
                :key="app.id"
                class="hover:bg-gray-50"
              >
                <!-- Volunteer -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">
                    {{ getVolunteerName(app.volunteer) }}
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ app.volunteer?.email }}
                  </div>
                </td>

                <!-- Project -->
                <td class="px-6 py-4">
                  <div class="text-sm font-medium text-gray-900">
                    <router-link
                      :to="`/projects/${app.project?.id}`"
                      class="text-primary-600 hover:text-primary-800 line-clamp-1"
                    >
                      {{ app.project?.title }}
                    </router-link>
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ app.project?.organization_name || app.project?.organization?.username }}
                  </div>
                </td>

                <!-- Cover letter -->
                <td class="px-6 py-4">
                  <div class="text-xs text-gray-700 max-w-xs line-clamp-2">
                    {{ app.cover_letter || 'Без письма' }}
                  </div>
                  <div class="text-[11px] text-gray-400 mt-1">
                    {{ formatDate(app.created_at) }}
                  </div>
                </td>

                <!-- Hours -->
                <td class="px-6 py-4 whitespace-nowrap text-xs font-semibold text-gray-800">
                  {{ app.hours_committed || 0 }} ч.
                </td>

                <!-- Status -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    class="px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full"
                    :class="getStatusBadgeClass(app.status)"
                  >
                    {{ getStatusTitle(app.status) }}
                  </span>
                </td>

                <!-- Actions -->
                <td class="px-6 py-4 whitespace-nowrap text-right text-xs font-medium space-x-1.5">
                  <!-- Approve -->
                  <button
                    v-if="app.status === 'pending'"
                    type="button"
                    class="px-2.5 py-1 rounded bg-green-50 text-green-700 hover:bg-green-100 border border-green-200 transition-colors"
                    @click="reviewApplication(app, 'approve')"
                  >
                    Одобрить
                  </button>

                  <!-- Reject -->
                  <button
                    v-if="app.status === 'pending'"
                    type="button"
                    class="px-2.5 py-1 rounded bg-red-50 text-red-700 hover:bg-red-100 border border-red-200 transition-colors"
                    @click="reviewApplication(app, 'reject')"
                  >
                    Отклонить
                  </button>

                  <!-- Cancel -->
                  <button
                    v-if="app.status === 'approved'"
                    type="button"
                    class="px-2.5 py-1 rounded bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200 transition-colors"
                    @click="cancelApplication(app)"
                  >
                    Отменить
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

interface ApplicationItem {
  id: number
  status: string
  cover_letter?: string
  hours_committed?: number
  created_at?: string
  volunteer?: {
    id?: number
    username?: string
    email?: string
    first_name?: string
    last_name?: string
    volunteer_profile?: {
      first_name?: string
      last_name?: string
    }
  }
  project?: {
    id?: number
    title?: string
    organization_name?: string
    organization?: { username?: string }
  }
}

const applications = ref<ApplicationItem[]>([])
const isLoading = ref(false)
const message = ref('')
const errorMsg = ref('')

const selectedStatus = ref('')
const searchQuery = ref('')
let searchTimer: any = null

const authHeader = () => {
  const token = localStorage.getItem('access_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const fetchApplications = async () => {
  isLoading.value = true
  try {
    const params: Record<string, any> = {}
    if (selectedStatus.value) params.status = selectedStatus.value
    if (searchQuery.value) params.search = searchQuery.value

    const res = await axios.get('/api/applications/', {
      headers: authHeader(),
      params
    })

    if (Array.isArray(res.data)) {
      applications.value = res.data
    } else if (res.data?.results) {
      applications.value = res.data.results
    }
  } catch (err: any) {
    console.error('Failed to load applications', err)
    errorMsg.value = err.response?.data?.detail || 'Ошибка загрузки заявок'
  } finally {
    isLoading.value = false
  }
}

const setStatus = (status: string) => {
  selectedStatus.value = status
  fetchApplications()
}

const onSearchInput = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    fetchApplications()
  }, 400)
}

const reviewApplication = async (app: ApplicationItem, action: 'approve' | 'reject') => {
  const comment = prompt(
    action === 'approve'
      ? 'Комментарий к одобрению заявки (необязательно):'
      : 'Причина отклонения заявки:'
  )
  if (comment === null) return // отмена

  try {
    await axios.post(`/api/applications/${app.id}/${action}/`, {
      review_comment: comment || ''
    }, {
      headers: authHeader()
    })
    app.status = action === 'approve' ? 'approved' : 'rejected'
    message.value = `Заявка успешно ${action === 'approve' ? 'одобрена' : 'отклонена'}`
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || 'Ошибка обработки заявки'
  }
}

const cancelApplication = async (app: ApplicationItem) => {
  if (!confirm('Вы уверены, что хотите отменить эту заявку?')) return
  try {
    await axios.post(`/api/applications/${app.id}/cancel/`, {}, {
      headers: authHeader()
    })
    app.status = 'cancelled'
    message.value = 'Заявка отменена'
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || 'Ошибка отмены заявки'
  }
}

const getVolunteerName = (vol?: ApplicationItem['volunteer']) => {
  if (!vol) return 'Неизвестный'
  if (vol.volunteer_profile?.first_name || vol.volunteer_profile?.last_name) {
    return `${vol.volunteer_profile.first_name || ''} ${vol.volunteer_profile.last_name || ''}`.trim()
  }
  if (vol.first_name || vol.last_name) {
    return `${vol.first_name || ''} ${vol.last_name || ''}`.trim()
  }
  return vol.username || vol.email || 'Волонтёр'
}

const getStatusTitle = (st: string) => {
  const map: Record<string, string> = {
    pending: 'На рассмотрении',
    approved: 'Одобрена',
    rejected: 'Отклонена',
    cancelled: 'Отменена'
  }
  return map[st] || st
}

const getStatusBadgeClass = (st: string) => {
  const map: Record<string, string> = {
    pending: 'bg-amber-100 text-amber-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    cancelled: 'bg-gray-100 text-gray-800'
  }
  return map[st] || 'bg-gray-100 text-gray-800'
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
  fetchApplications()
})
</script>
