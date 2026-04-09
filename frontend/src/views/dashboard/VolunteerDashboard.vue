<template>
  <div class="min-h-screen bg-gray-50">
    <div class="bg-white shadow-sm border-b">
      <div class="container-custom py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">
              Панель волонтера
            </h1>
            <p class="text-gray-600 mt-1">
              Добро пожаловать, {{ getUserDisplayName() }}!
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

    <div class="container-custom py-8">
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
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                />
              </svg>
            </div>
            <div class="ml-4">
              <div class="text-2xl font-bold text-gray-900">
                {{ stats.total_applications }}
              </div>
              <div class="text-sm text-gray-600">
                Мои заявки
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
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <div class="ml-4">
              <div class="text-2xl font-bold text-gray-900">
                {{ stats.approved_applications }}
              </div>
              <div class="text-sm text-gray-600">
                Одобрено
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
                  d="M8 12h8M8 16h8M8 8h8M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>
            <div class="ml-4">
              <div class="text-2xl font-bold text-gray-900">
                {{ stats.hours_committed }}
              </div>
              <div class="text-sm text-gray-600">
                Часов обещано
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
          <div class="flex items-center">
            <div class="p-3 bg-yellow-100 rounded-full">
              <svg
                class="w-6 h-6 text-yellow-600"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
              </svg>
            </div>
            <div class="ml-4">
              <div class="text-2xl font-bold text-gray-900">
                {{ stats.average_rating > 0 ? stats.average_rating.toFixed(1) : '—' }}
              </div>
              <div class="text-sm text-gray-600">
                Средний рейтинг
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs: Заявки | Сертификаты -->
      <div class="mb-6">
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex space-x-8">
            <button
              :class="[activeTab === 'applications' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm']"
              @click="activeTab = 'applications'"
            >
              Мои заявки
            </button>
            <button
              :class="[activeTab === 'certificates' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm']"
              @click="activeTab = 'certificates'; loadCertificates()"
            >
              Мои сертификаты
              <span
                v-if="certificates.length > 0"
                class="ml-2 bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs"
              >{{ certificates.length }}</span>
            </button>
          </nav>
        </div>
      </div>

      <!-- Certificates Tab -->
      <div
        v-if="activeTab === 'certificates'"
        class="bg-white rounded-lg shadow"
      >
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900">
            Мои сертификаты
          </h2>
          <button
            class="btn btn-primary"
            @click="showCertificateForm = !showCertificateForm"
          >
            {{ showCertificateForm ? 'Отмена' : 'Загрузить сертификат' }}
          </button>
        </div>

        <!-- Upload form -->
        <div
          v-if="showCertificateForm"
          class="p-6 border-b border-gray-200 bg-gray-50"
        >
          <form
            class="space-y-4"
            @submit.prevent="uploadCertificate"
          >
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="form-label">Название *</label>
                <input
                  v-model="certForm.title"
                  type="text"
                  class="form-input"
                  placeholder="Название сертификата"
                  required
                >
              </div>
              <div>
                <label class="form-label">Кем выдан</label>
                <input
                  v-model="certForm.issued_by"
                  type="text"
                  class="form-input"
                  placeholder="Организация или учреждение"
                >
              </div>
              <div>
                <label class="form-label">Дата выдачи</label>
                <input
                  v-model="certForm.issued_at"
                  type="date"
                  class="form-input"
                >
              </div>
              <div>
                <label class="form-label">Файл *</label>
                <input
                  ref="certFileInput"
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  class="form-input"
                  required
                >
              </div>
            </div>
            <div>
              <label class="form-label">Описание</label>
              <textarea
                v-model="certForm.description"
                class="form-input"
                rows="2"
                placeholder="Краткое описание"
              />
            </div>
            <div class="flex justify-end">
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="certUploading"
              >
                {{ certUploading ? 'Загрузка...' : 'Загрузить' }}
              </button>
            </div>
          </form>
        </div>

        <div class="p-6">
          <div
            v-if="certificatesLoading"
            class="text-center py-8"
          >
            <div class="loading-spinner mx-auto" />
          </div>
          <div
            v-else-if="certificates.length === 0"
            class="text-center py-8 text-gray-500"
          >
            У вас пока нет сертификатов. Загрузите свой первый сертификат!
          </div>
          <div
            v-else
            class="space-y-4"
          >
            <div
              v-for="cert in certificates"
              :key="cert.id"
              class="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
            >
              <div class="flex-1">
                <h3 class="font-medium text-gray-900">
                  {{ cert.title }}
                </h3>
                <div class="text-sm text-gray-500 mt-1">
                  <span v-if="cert.issued_by">{{ cert.issued_by }}</span>
                  <span v-if="cert.issued_by && cert.issued_at"> · </span>
                  <span v-if="cert.issued_at">{{ formatDate(cert.issued_at) }}</span>
                </div>
                <p
                  v-if="cert.description"
                  class="text-sm text-gray-600 mt-1"
                >
                  {{ cert.description }}
                </p>
              </div>
              <div class="flex items-center space-x-2 ml-4">
                <a
                  :href="cert.file"
                  target="_blank"
                  class="btn btn-outline btn-sm"
                >
                  Скачать
                </a>
                <button
                  class="btn btn-ghost btn-sm text-red-600 hover:text-red-800"
                  @click="deleteCertificate(cert.id)"
                >
                  Удалить
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Applications Tab -->
      <div
        v-if="activeTab === 'applications'"
        class="bg-white rounded-lg shadow"
      >
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900">
            Мои заявки
          </h2>
          <router-link
            to="/applications/my"
            class="btn btn-outline"
          >
            Все заявки
          </router-link>
        </div>
        <div class="p-6">
          <div
            v-if="applicationsLoading"
            class="text-center py-8"
          >
            <div class="loading-spinner w-8 h-8 mx-auto mb-4" />
            <p class="text-gray-600">
              Загрузка заявок...
            </p>
          </div>

          <div
            v-else-if="applications.length === 0"
            class="text-center py-8"
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
              Заявок пока нет
            </h3>
            <p class="mt-1 text-sm text-gray-500">
              Вы еще не подали заявки на проекты
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

          <div
            v-else
            class="space-y-4"
          >
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
import type { Application, VolunteerCertificate } from '@/types/api'

const authStore = useAuthStore()

const activeTab = ref<'applications' | 'certificates'>('applications')

const stats = ref({
  total_applications: 0,
  approved_applications: 0,
  hours_committed: 0,
  average_rating: 0
})

const applications = ref<Application[]>([])
const applicationsLoading = ref(false)
const unreadCount = ref(0)

// Certificates
const certificates = ref<VolunteerCertificate[]>([])
const certificatesLoading = ref(false)
const showCertificateForm = ref(false)
const certUploading = ref(false)
const certFileInput = ref<HTMLInputElement | null>(null)
const certForm = ref({
  title: '',
  description: '',
  issued_by: '',
  issued_at: ''
})

onMounted(async () => {
  await Promise.all([loadStats(), loadApplications(), loadUnreadCount()])
})

const loadStats = async () => {
  try {
    const data = await apiService.getStatistics()
    stats.value = {
      total_applications: data.my_applications?.total ?? data.total_applications ?? 0,
      approved_applications: data.my_applications?.approved ?? data.approved_applications ?? 0,
      hours_committed: data.my_applications?.total_hours ?? data.total_hours ?? 0,
      average_rating: data.achievements?.average_rating ?? 0
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

const loadCertificates = async () => {
  if (certificates.value.length > 0) return
  try {
    certificatesLoading.value = true
    const response = await apiService.getCertificates()
    certificates.value = response.results || []
  } catch (error) {
    console.error('Failed to load certificates:', error)
  } finally {
    certificatesLoading.value = false
  }
}

const uploadCertificate = async () => {
  const file = certFileInput.value?.files?.[0]
  if (!file || !certForm.value.title) return

  try {
    certUploading.value = true
    const formData = new FormData()
    formData.append('title', certForm.value.title)
    formData.append('file', file)
    if (certForm.value.description) formData.append('description', certForm.value.description)
    if (certForm.value.issued_by) formData.append('issued_by', certForm.value.issued_by)
    if (certForm.value.issued_at) formData.append('issued_at', certForm.value.issued_at)

    const newCert = await apiService.uploadCertificate(formData)
    certificates.value.unshift(newCert)
    showCertificateForm.value = false
    certForm.value = { title: '', description: '', issued_by: '', issued_at: '' }
    if (certFileInput.value) certFileInput.value.value = ''
  } catch (error) {
    console.error('Failed to upload certificate:', error)
  } finally {
    certUploading.value = false
  }
}

const deleteCertificate = async (id: number) => {
  if (!confirm('Удалить этот сертификат?')) return
  try {
    await apiService.deleteCertificate(id)
    certificates.value = certificates.value.filter(c => c.id !== id)
  } catch (error) {
    console.error('Failed to delete certificate:', error)
  }
}
</script>
