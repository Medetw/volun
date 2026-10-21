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
              Модерация проектов
            </h1>
          </div>
          <p class="text-gray-600 mt-1">
            Просмотр, смена статусов, активация и модерация всех проектов платформы
          </p>
        </div>

        <div class="flex items-center gap-2">
          <router-link
            to="/projects/create"
            class="btn btn-primary text-sm"
          >
            + Создать проект
          </router-link>
          <router-link
            to="/projects"
            class="btn btn-outline text-sm"
          >
            Каталог проектов
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
            Все статусы
          </button>
          <button
            type="button"
            class="px-3 py-1.5 text-xs font-medium rounded-full transition-colors"
            :class="selectedStatus === 'draft' ? 'bg-amber-600 text-white' : 'bg-amber-50 text-amber-700 hover:bg-amber-100'"
            @click="setStatus('draft')"
          >
            Черновики / На модерации
          </button>
          <button
            type="button"
            class="px-3 py-1.5 text-xs font-medium rounded-full transition-colors"
            :class="selectedStatus === 'active' ? 'bg-green-600 text-white' : 'bg-green-50 text-green-700 hover:bg-green-100'"
            @click="setStatus('active')"
          >
            Активные
          </button>
          <button
            type="button"
            class="px-3 py-1.5 text-xs font-medium rounded-full transition-colors"
            :class="selectedStatus === 'completed' ? 'bg-blue-600 text-white' : 'bg-blue-50 text-blue-700 hover:bg-blue-100'"
            @click="setStatus('completed')"
          >
            Завершённые
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
            placeholder="Поиск по названию..."
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

      <!-- Projects Table -->
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
          Загрузка проектов...
        </div>

        <div
          v-else-if="projects.length === 0"
          class="p-8 text-center text-gray-500"
        >
          Проекты не найдены
        </div>

        <div
          v-else
          class="overflow-x-auto"
        >
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Проект
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Организация
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Формат / Регион
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Волонтёры
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
                v-for="p in projects"
                :key="p.id"
                class="hover:bg-gray-50"
              >
                <!-- Title & Category -->
                <td class="px-6 py-4">
                  <div class="text-sm font-medium text-gray-900">
                    <router-link
                      :to="`/projects/${p.id}`"
                      class="text-primary-600 hover:text-primary-800"
                    >
                      {{ p.title }}
                    </router-link>
                  </div>
                  <div class="text-xs text-gray-500 mt-0.5">
                    {{ p.category?.name || 'Без категории' }}
                  </div>
                </td>

                <!-- Organization -->
                <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-600">
                  {{ p.organization_name || 'Не указана' }}
                </td>

                <!-- Format / Region -->
                <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-500">
                  <div>{{ formatBadge(p.format) }}</div>
                  <div class="text-gray-400 mt-0.5">{{ p.region?.name || 'Казахстан' }}</div>
                </td>

                <!-- Volunteers Needed -->
                <td class="px-6 py-4 whitespace-nowrap text-xs">
                  <span class="font-semibold text-gray-900">{{ p.volunteers_count || 0 }}</span>
                  <span class="text-gray-400"> / {{ p.volunteers_needed }}</span>
                </td>

                <!-- Status -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    class="px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full"
                    :class="getStatusBadgeClass(p.status)"
                  >
                    {{ getStatusTitle(p.status) }}
                  </span>
                </td>

                <!-- Actions -->
                <td class="px-6 py-4 whitespace-nowrap text-right text-xs font-medium space-x-1.5">
                  <!-- Activate -->
                  <button
                    v-if="p.status !== 'active'"
                    type="button"
                    class="px-2.5 py-1 rounded bg-green-50 text-green-700 hover:bg-green-100 border border-green-200 transition-colors"
                    title="Одобрить и опубликовать"
                    @click="changeStatus(p, 'active')"
                  >
                    ✓ Одобрить
                  </button>

                  <!-- Make Draft / Reject -->
                  <button
                    v-if="p.status === 'active'"
                    type="button"
                    class="px-2.5 py-1 rounded bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200 transition-colors"
                    title="Вернуть в черновик"
                    @click="changeStatus(p, 'draft')"
                  >
                    В черновик
                  </button>

                  <!-- Complete -->
                  <button
                    v-if="p.status === 'active'"
                    type="button"
                    class="px-2.5 py-1 rounded bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 transition-colors"
                    title="Завершить проект"
                    @click="changeStatus(p, 'completed')"
                  >
                    Завершить
                  </button>

                  <!-- Edit -->
                  <router-link
                    :to="`/projects/${p.id}/edit`"
                    class="px-2 py-1 rounded bg-gray-50 text-gray-700 hover:bg-gray-100 border border-gray-200 inline-block"
                  >
                    ✏️
                  </router-link>

                  <!-- Delete -->
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-red-50 text-red-600 hover:bg-red-100 border border-red-200"
                    title="Удалить"
                    @click="deleteProject(p)"
                  >
                    🗑
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

interface ProjectItem {
  id: number
  title: string
  description?: string
  status: string
  format: string
  organization_name?: string
  volunteers_needed: number
  volunteers_count?: number
  category?: { name?: string }
  region?: { name?: string }
}

const projects = ref<ProjectItem[]>([])
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

const fetchProjects = async () => {
  isLoading.value = true
  try {
    const params: Record<string, any> = {}
    if (selectedStatus.value) params.status = selectedStatus.value
    if (searchQuery.value) params.search = searchQuery.value

    const res = await axios.get('/api/projects/', {
      headers: authHeader(),
      params
    })

    if (Array.isArray(res.data)) {
      projects.value = res.data
    } else if (res.data?.results) {
      projects.value = res.data.results
    }
  } catch (err: any) {
    console.error('Failed to load projects', err)
    errorMsg.value = err.response?.data?.detail || 'Ошибка загрузки проектов'
  } finally {
    isLoading.value = false
  }
}

const setStatus = (status: string) => {
  selectedStatus.value = status
  fetchProjects()
}

const onSearchInput = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    fetchProjects()
  }, 400)
}

const changeStatus = async (p: ProjectItem, newStatus: string) => {
  try {
    await axios.patch(`/api/projects/${p.id}/`, {
      status: newStatus
    }, {
      headers: authHeader()
    })
    p.status = newStatus
    message.value = `Статус проекта "${p.title}" изменён на: ${getStatusTitle(newStatus)}`
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || 'Не удалось обновить статус проекта'
  }
}

const deleteProject = async (p: ProjectItem) => {
  if (!confirm(`Вы уверены, что хотите удалить проект "${p.title}"?`)) {
    return
  }
  try {
    await axios.delete(`/api/projects/${p.id}/`, {
      headers: authHeader()
    })
    projects.value = projects.value.filter(item => item.id !== p.id)
    message.value = `Проект "${p.title}" удалён`
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || 'Ошибка удаления проекта'
  }
}

const formatBadge = (fmt: string) => {
  const map: Record<string, string> = {
    online: 'Онлайн',
    offline: 'Офлайн',
    hybrid: 'Гибрид'
  }
  return map[fmt] || fmt
}

const getStatusTitle = (st: string) => {
  const map: Record<string, string> = {
    draft: 'Черновик',
    active: 'Активен',
    completed: 'Завершён',
    cancelled: 'Отменён'
  }
  return map[st] || st
}

const getStatusBadgeClass = (st: string) => {
  const map: Record<string, string> = {
    draft: 'bg-amber-100 text-amber-800',
    active: 'bg-green-100 text-green-800',
    completed: 'bg-blue-100 text-blue-800',
    cancelled: 'bg-gray-100 text-gray-800'
  }
  return map[st] || 'bg-gray-100 text-gray-800'
}

onMounted(() => {
  fetchProjects()
})
</script>
