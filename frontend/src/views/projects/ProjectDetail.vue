<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Loading State -->
    <div
      v-if="loading"
      class="flex items-center justify-center py-20"
    >
      <div class="loading-spinner w-8 h-8 mr-3" />
      <span class="text-gray-600">Загрузка проекта...</span>
    </div>

    <!-- Error State -->
    <div
      v-else-if="error"
      class="flex items-center justify-center py-20"
    >
      <div class="text-center">
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
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">
          Проект не найден
        </h3>
        <p class="mt-1 text-sm text-gray-500">
          Проект, который вы ищете, не существует или был удален
        </p>
        <div class="mt-6">
          <router-link
            to="/projects"
            class="btn btn-primary"
          >
            ← Вернуться к проектам
          </router-link>
        </div>
      </div>
    </div>

    <!-- Project Content -->
    <div v-else-if="project">
      <!-- Header Image -->
      <div class="relative h-64 bg-gray-200">
        <img
          v-if="project.image"
          :src="project.image"
          :alt="project.title"
          class="w-full h-full object-cover"
        >
        <div
          v-else
          class="w-full h-full bg-gradient-to-r from-primary-500 to-primary-600 flex items-center justify-center"
        >
          <svg
            class="w-16 h-16 text-white opacity-50"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
            />
          </svg>
        </div>
        
        <!-- Status Badge -->
        <div class="absolute top-4 right-4">
          <span :class="getStatusBadgeClass(project.status)">
            {{ getStatusDisplay(project.status) }}
          </span>
        </div>
      </div>

      <div class="container-custom py-8">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Main Content -->
          <div class="lg:col-span-2 space-y-6">
            <!-- Title and Meta -->
            <div>
              <div class="flex items-center space-x-2 mb-4">
                <span class="badge badge-primary">{{ project.category.name }}</span>
                <span class="badge badge-gray">{{ getFormatDisplay(project.format) }}</span>
              </div>
              
              <h1 class="text-3xl font-bold text-gray-900 mb-4">
                {{ project.title }}
              </h1>
              
              <div class="flex flex-wrap gap-4 text-sm text-gray-600">
                <div class="flex items-center">
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                    />
                  </svg>
                  {{ project.organization_name || 'Организация' }}
                </div>
                
                <div
                  v-if="project.region"
                  class="flex items-center"
                >
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314-1.314l4.242 4.242a1.998 1.998 0 010 2.828z"
                    />
                  </svg>
                  {{ project.region.name }}
                </div>
                
                <div
                  v-if="project.start_date"
                  class="flex items-center"
                >
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                  {{ formatDateRange(project.start_date, project.end_date) }}
                </div>
              </div>
            </div>

            <!-- Description -->
            <div class="bg-white p-6 rounded-lg shadow">
              <h2 class="text-xl font-semibold mb-4">
                Описание проекта
              </h2>
              <div class="prose max-w-none text-gray-600">
                <p>{{ project.description }}</p>
              </div>
            </div>

            <!-- Requirements -->
            <div
              v-if="project.requirements"
              class="bg-white p-6 rounded-lg shadow"
            >
              <h2 class="text-xl font-semibold mb-4">
                Требования к волонтерам
              </h2>
              <div class="prose max-w-none text-gray-600">
                <p>{{ project.requirements }}</p>
              </div>
            </div>

            <!-- Contact Info -->
            <div
              v-if="project.contact_info"
              class="bg-white p-6 rounded-lg shadow"
            >
              <h2 class="text-xl font-semibold mb-4">
                Контактная информация
              </h2>
              <div class="text-gray-700 space-y-1">
                <template v-if="contactInfoFormatted">
                  <p v-if="contactInfoFormatted.phone">
                    <span class="font-medium">Телефон:</span> {{ contactInfoFormatted.phone }}
                  </p>
                  <p v-if="contactInfoFormatted.email">
                    <span class="font-medium">Email:</span> {{ contactInfoFormatted.email }}
                  </p>
                  <p v-if="contactInfoFormatted.other">
                    {{ contactInfoFormatted.other }}
                  </p>
                </template>
                <p v-else>
                  {{ project.contact_info }}
                </p>
              </div>
            </div>
          </div>

          <!-- Sidebar -->
          <div class="space-y-6">
            <!-- Apply Card -->
            <div class="bg-white p-6 rounded-lg shadow">
              <h3 class="text-lg font-semibold mb-4">
                Участие в проекте
              </h3>
              
              <!-- Progress -->
              <div class="mb-6">
                <div class="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Волонтеры</span>
                  <span>{{ project.volunteers_needed - project.volunteers_remaining }}/{{ project.volunteers_needed }}</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-3">
                  <div
                    class="bg-primary-600 h-3 rounded-full"
                    :style="{ width: `${getProgressPercentage(project)}%` }"
                  />
                </div>
              </div>

              <!-- Stats -->
              <div class="grid grid-cols-2 gap-4 mb-6 text-center">
                <div>
                  <div class="text-2xl font-bold text-primary-600">
                    {{ project.volunteers_needed }}
                  </div>
                  <div class="text-sm text-gray-600">
                    Нужно волонтеров
                  </div>
                </div>
                <div>
                  <div class="text-2xl font-bold text-green-600">
                    {{ project.volunteers_remaining }}
                  </div>
                  <div class="text-sm text-gray-600">
                    Свободных мест
                  </div>
                </div>
              </div>

              <!-- Apply Button -->
              <div v-if="authStore.isAuthenticated && authStore.isVolunteer">
                <button
                  v-if="project.volunteers_remaining > 0 && project.status === 'active'"
                  class="btn btn-primary w-full"
                  @click="showApplyModal = true"
                >
                  Подать заявку
                </button>
                <button
                  v-else-if="project.volunteers_remaining === 0"
                  disabled
                  class="btn btn-disabled w-full"
                >
                  Мест нет
                </button>
                <button
                  v-else
                  disabled
                  class="btn btn-disabled w-full"
                >
                  Проект не активен
                </button>
              </div>
              
              <div
                v-else-if="!canModerate"
                class="space-y-3"
              >
                <router-link
                  to="/login"
                  class="btn btn-primary w-full"
                >
                  Войти для подачи заявки
                </router-link>
                <router-link
                  to="/register/volunteer"
                  class="btn btn-outline w-full"
                >
                  Зарегистрироваться
                </router-link>
              </div>

              <!-- Admin / Moderator / Owner controls (Block 5) -->
              <div
                v-if="canModerate"
                class="space-y-3 pt-3 border-t mt-3"
              >
                <button
                  v-if="project.status !== 'completed'"
                  class="btn btn-primary w-full"
                  :disabled="closing"
                  @click="handleCloseProject"
                >
                  {{ closing ? 'Закрытие...' : 'Закрыть проект' }}
                </button>
                <button
                  class="btn btn-outline w-full"
                  @click="showParticipantsModal = true"
                >
                  Участники проекта
                </button>
              </div>
            </div>

            <!-- Organization Info -->
            <div class="bg-white p-6 rounded-lg shadow">
              <h3 class="text-lg font-semibold mb-4">
                Организация
              </h3>
              <div class="space-y-2">
                <div>
                  <div class="text-sm text-gray-500">
                    Название
                  </div>
                  <div class="font-medium">
                    {{ project.organization_name || 'Не указано' }}
                  </div>
                </div>
                <div v-if="project.region">
                  <div class="text-sm text-gray-500">
                    Регион
                  </div>
                  <div class="font-medium">
                    {{ project.region.name }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Share -->
            <div class="bg-white p-6 rounded-lg shadow">
              <h3 class="text-lg font-semibold mb-4">
                Поделиться
              </h3>
              <div class="flex space-x-2">
                <button class="flex-1 btn btn-outline">
                  <svg
                    class="w-4 h-4"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                  </svg>
                </button>
                <button class="flex-1 btn btn-outline">
                  <svg
                    class="w-4 h-4"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 00-8.384 4.482A9.953 9.953 0 002.458 4.572c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Apply Modal -->
    <div
      v-if="showApplyModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    >
      <div class="relative min-h-screen flex items-center justify-center p-4">
        <div class="bg-white rounded-lg max-w-md w-full p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            Подать заявку на участие
          </h3>
          
          <form @submit.prevent="handleApply">
            <div
              v-if="applyError"
              class="mb-4 bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-600"
            >
              {{ applyError }}
            </div>
            <div class="space-y-4">
              <div>
                <label class="form-label">Сопроводительное письмо</label>
                <textarea
                  v-model="applicationForm.cover_letter"
                  rows="4"
                  class="form-input"
                  placeholder="Расскажите, почему вы хотите участвовать в этом проекте..."
                  required
                />
              </div>
              
              <div>
                <label class="form-label">Сколько часов готовы уделить?</label>
                <input
                  v-model.number="applicationForm.hours_committed"
                  type="number"
                  min="1"
                  class="form-input"
                  placeholder="5"
                  required
                >
              </div>
            </div>
            
            <div class="mt-6 flex space-x-3">
              <button
                type="submit"
                :disabled="applying"
                class="btn btn-primary flex-1"
              >
                {{ applying ? 'Отправка...' : 'Подать заявку' }}
              </button>
              <button
                type="button"
                class="btn btn-outline"
                @click="showApplyModal = false"
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Participants Modal (Block 5) -->
    <ParticipantsModal
      v-if="project"
      :open="showParticipantsModal"
      :project-id="project.id"
      :project-title="project.title"
      @close="showParticipantsModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import apiService from '@/services/api'
import type { Project } from '@/types/api'
import ParticipantsModal from '@/components/ParticipantsModal.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const project = ref<Project | null>(null)
const loading = ref(true)
const error = ref(false)
const showApplyModal = ref(false)
const applying = ref(false)
const showParticipantsModal = ref(false)
const closing = ref(false)

const canModerate = computed(() => {
  if (!authStore.isAuthenticated || !project.value) return false
  if (authStore.isAdmin || authStore.isModerator) return true
  // Owner of the project
  return authStore.isOrganization && project.value.organization_name === authStore.user?.organization_profile?.name
})

const applicationForm = reactive({
  cover_letter: '',
  hours_committed: 5
})

const applyError = ref('')

const contactInfoFormatted = computed(() => {
  const raw = project.value?.contact_info
  if (!raw) return null
  let parsed: any = null
  if (typeof raw === 'object') {
    parsed = raw
  } else if (typeof raw === 'string') {
    const trimmed = raw.trim()
    if (!trimmed.startsWith('{')) return null
    try { parsed = JSON.parse(trimmed) } catch { return null }
  }
  if (!parsed || typeof parsed !== 'object') return null
  return {
    phone: parsed.phone || '',
    email: parsed.email || '',
    other: parsed.other || parsed.note || ''
  }
})

onMounted(async () => {
  await loadProject()
})

const loadProject = async () => {
  try {
    loading.value = true
    error.value = false
    project.value = await apiService.getProject(Number(route.params.id))
  } catch (err) {
    error.value = true
    console.error('Failed to load project:', err)
  } finally {
    loading.value = false
  }
}

const handleApply = async () => {
  if (!project.value) return

  try {
    applying.value = true
    applyError.value = ''

    await apiService.createApplication({
      project: project.value.id,
      cover_letter: applicationForm.cover_letter,
      hours_committed: applicationForm.hours_committed
    })

    showApplyModal.value = false

    // Show success message or redirect
    router.push('/applications/my')
  } catch (err: any) {
    console.error('Failed to apply:', err)
    const data = err?.response?.data
    if (typeof data === 'string') {
      applyError.value = data
    } else if (data?.detail) {
      applyError.value = data.detail
    } else if (data?.non_field_errors?.length) {
      applyError.value = data.non_field_errors[0]
    } else if (data && typeof data === 'object') {
      const firstField = Object.values(data)[0]
      applyError.value = Array.isArray(firstField) ? String(firstField[0]) : String(firstField)
    } else {
      applyError.value = 'Не удалось подать заявку. Попробуйте ещё раз.'
    }
  } finally {
    applying.value = false
  }
}

const getStatusBadgeClass = (status: string) => {
  const statusClasses = {
    active: 'badge-success',
    draft: 'badge-gray',
    completed: 'badge-primary',
    cancelled: 'badge-danger'
  }
  return statusClasses[status as keyof typeof statusClasses] || 'badge-gray'
}

const getStatusDisplay = (status: string) => {
  const statusMap = {
    active: 'Активный',
    draft: 'Черновик',
    completed: 'Завершен',
    cancelled: 'Отменен'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const getFormatDisplay = (format: string) => {
  const formatMap = {
    online: 'Онлайн',
    offline: 'Офлайн',
    hybrid: 'Гибридный'
  }
  return formatMap[format as keyof typeof formatMap] || format
}

const getProgressPercentage = (project: Project) => {
  return ((project.volunteers_needed - project.volunteers_remaining) / project.volunteers_needed) * 100
}

const handleCloseProject = async () => {
  if (!project.value) return
  if (!confirm('Закрыть проект? Откроется таблица волонтёров для оценки часов и сертификатов.')) return
  closing.value = true
  try {
    const result = await apiService.closeProject(project.value.id)
    project.value = result.project
    showParticipantsModal.value = true
  } catch (e: any) {
    alert(e?.response?.data?.error || 'Не удалось закрыть проект')
  } finally {
    closing.value = false
  }
}

const formatDateRange = (startDate: string, endDate: string) => {
  const start = new Date(startDate)
  const end = endDate ? new Date(endDate) : null
  
  if (end) {
    return `${start.toLocaleDateString('ru-RU')} - ${end.toLocaleDateString('ru-RU')}`
  }
  
  return `С ${start.toLocaleDateString('ru-RU')}`
}
</script>
