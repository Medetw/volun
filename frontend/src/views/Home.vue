<template>
  <div>
    <!-- Hero Section -->
    <section class="relative overflow-hidden bg-gradient-to-br from-primary-700 via-primary-600 to-primary-800 text-white">
      <div class="absolute -top-24 -right-16 h-72 w-72 rounded-full bg-white/10 blur-2xl" />
      <div class="absolute bottom-0 left-0 h-64 w-64 -translate-x-1/3 translate-y-1/3 rounded-full bg-primary-400/30 blur-2xl" />
      <div class="container-custom relative py-24">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-14 items-center">
          <div>
            <div class="inline-flex items-center gap-2 rounded-full bg-white/15 px-4 py-2 text-sm font-medium text-primary-50">
              <span class="h-2 w-2 rounded-full bg-emerald-300" />
              Более 500 проектов по Казахстану
            </div>
            <h1 class="mt-6 text-4xl lg:text-6xl font-bold leading-tight">
              Добрые дела рядом.
              <span class="block text-primary-100">Начните сегодня.</span>
            </h1>
            <p class="mt-6 text-lg text-primary-100">
              Найдите волонтёрские инициативы, вступайте в команды и следите за прогрессом в личном кабинете.
              Для организаций — быстрый запуск проектов и набор волонтёров.
            </p>
            <div class="mt-8 flex flex-col sm:flex-row gap-4">
              <router-link
                to="/projects"
                class="btn bg-white text-primary-700 hover:bg-primary-50 btn-lg"
              >
                Найти проекты
              </router-link>
              <router-link
                v-if="!authStore.isAuthenticated"
                to="/register/volunteer"
                class="btn border-2 border-white text-white hover:bg-white hover:text-primary-700 btn-lg"
              >
                Стать волонтером
              </router-link>
              <router-link
                v-if="!authStore.isAuthenticated || authStore.isOrganization || authStore.isAdmin"
                to="/register/organization"
                class="btn bg-primary-900/40 text-white hover:bg-primary-900/60 btn-lg"
              >
                Создать проект
              </router-link>
            </div>
          </div>
          <div class="hidden lg:block">
            <div class="relative rounded-3xl border border-white/20 bg-white/10 p-8 backdrop-blur">
              <div class="grid gap-6">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <div
                      v-if="volunteerOfWeek?.volunteer?.avatar"
                      class="h-10 w-10 rounded-full overflow-hidden flex-shrink-0"
                    >
                      <img
                        :src="volunteerOfWeek.volunteer.avatar"
                        :alt="volunteerOfWeek.volunteer.name"
                        class="h-full w-full object-cover"
                      >
                    </div>
                    <div
                      v-else
                      class="h-10 w-10 rounded-full bg-primary-200/30 flex-shrink-0"
                    />
                    <div>
                      <p class="text-sm uppercase text-primary-100">
                        Волонтёр недели
                      </p>
                      <p class="text-2xl font-semibold">
                        {{ volunteerOfWeek?.volunteer?.name || '—' }}
                      </p>
                    </div>
                  </div>
                  <span
                    v-if="volunteerOfWeek?.week_hours"
                    class="rounded-full bg-emerald-400/20 px-3 py-1 text-xs font-semibold text-emerald-100"
                  >+{{ volunteerOfWeek.week_hours }} часов</span>
                </div>
                <div class="rounded-2xl bg-white/15 p-5">
                  <p class="text-sm text-primary-100">
                    Сейчас активны
                  </p>
                  <p class="mt-2 text-4xl font-bold">
                    {{ stats.projects.active || stats.projects.total }}
                  </p>
                  <p class="text-sm text-primary-100">
                    проектов
                  </p>
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div class="rounded-2xl bg-white/10 p-4">
                    <p class="text-sm text-primary-100">
                      Новые заявки
                    </p>
                    <p class="mt-1 text-2xl font-semibold">
                      {{ stats.applications.recent || stats.applications.total }}
                    </p>
                  </div>
                  <div class="rounded-2xl bg-white/10 p-4">
                    <p class="text-sm text-primary-100">
                      Новые волонтеры
                    </p>
                    <p class="mt-1 text-2xl font-semibold">
                      {{ stats.users.recent || stats.users.volunteers || stats.users.total }}
                    </p>
                  </div>
                </div>
                <div class="flex items-center gap-3 rounded-2xl bg-white/10 p-4">
                  <div class="h-10 w-10 rounded-full bg-primary-200/30" />
                  <div>
                    <p class="text-sm font-medium">
                      Сделано вместе
                    </p>
                    <p class="text-xs text-primary-100">
                      {{ stats.applications.total_hours }} часов помощи
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="py-16 bg-white">
      <div class="container-custom">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
          <div>
            <div class="text-4xl font-bold text-primary-600 mb-2">
              {{ stats.users.total }}
            </div>
            <div class="text-gray-600">
              Пользователей
            </div>
          </div>
          <div>
            <div class="text-4xl font-bold text-primary-600 mb-2">
              {{ stats.projects.total }}
            </div>
            <div class="text-gray-600">
              Проектов
            </div>
          </div>
          <div>
            <div class="text-4xl font-bold text-primary-600 mb-2">
              {{ stats.applications.total }}
            </div>
            <div class="text-gray-600">
              Заявок
            </div>
          </div>
          <div>
            <div class="text-4xl font-bold text-primary-600 mb-2">
              {{ stats.applications.total_hours }}
            </div>
            <div class="text-gray-600">
              Часов помощи
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-16 bg-gray-50">
      <div class="container-custom">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">
            Как это работает?
          </h2>
          <p class="text-xl text-gray-600">
            Простые шаги для начала волонтерской деятельности
          </p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                class="w-8 h-8 text-primary-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </div>
            <h3 class="text-xl font-semibold mb-2">
              Создайте профиль
            </h3>
            <p class="text-gray-600">
              Зарегистрируйтесь как волонтер или организация
            </p>
          </div>
          
          <div class="text-center">
            <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                class="w-8 h-8 text-primary-600"
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
            <h3 class="text-xl font-semibold mb-2">
              Найдите проекты
            </h3>
            <p class="text-gray-600">
              Ищите интересные проекты или создавайте свои
            </p>
          </div>
          
          <div class="text-center">
            <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                class="w-8 h-8 text-primary-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                />
              </svg>
            </div>
            <h3 class="text-xl font-semibold mb-2">
              Помогайте другим
            </h3>
            <p class="text-gray-600">
              Участвуйте в проектах и делайте мир лучше
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Featured Projects -->
    <section class="py-16 bg-white">
      <div class="container-custom">
        <div class="flex justify-between items-center mb-8">
          <div>
            <h2 class="text-3xl font-bold text-gray-900 mb-2">
              Активные проекты
            </h2>
            <p class="text-gray-600">
              Участвуйте в текущих волонтерских инициативах
            </p>
          </div>
          <router-link
            to="/projects"
            class="btn btn-primary"
          >
            Все проекты
          </router-link>
        </div>
        
        <div
          v-if="projectsLoading"
          class="text-center py-8"
        >
          <div class="loading-spinner w-8 h-8 mx-auto mb-4" />
          <p class="text-gray-600">
            Загрузка проектов...
          </p>
        </div>
        
        <div
          v-else-if="projects.length === 0"
          class="text-center py-8"
        >
          <p class="text-gray-600">
            Активных проектов пока нет
          </p>
        </div>
        
        <div
          v-else
          class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          <div
            v-for="project in projects"
            :key="project.id"
            class="card hover:shadow-lg transition-shadow"
          >
            <div class="p-6">
              <div class="flex items-center justify-between mb-4">
                <span class="badge badge-primary">{{ project.category.name }}</span>
                <span class="status-active">{{ project.status }}</span>
              </div>
              
              <h3 class="text-xl font-semibold mb-2">
                {{ project.title }}
              </h3>
              <p class="text-gray-600 mb-4 line-clamp-2">
                {{ project.description }}
              </p>
              
              <div class="flex items-center justify-between text-sm text-gray-500 mb-4">
                <span>{{ project.organization_name }}</span>
                <span>{{ project.volunteers_remaining }}/{{ project.volunteers_needed }} мест</span>
              </div>
              
              <div class="w-full bg-gray-200 rounded-full h-2 mb-4">
                <div 
                  class="bg-primary-600 h-2 rounded-full" 
                  :style="{ width: `${((project.volunteers_needed - project.volunteers_remaining) / project.volunteers_needed) * 100}%` }"
                />
              </div>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <router-link
                  :to="`/projects/${project.id}`"
                  class="btn btn-outline w-full"
                >
                  Подробнее
                </router-link>
                <button
                  class="btn btn-primary w-full"
                  @click="openApplication(project)"
                >
                  Подать заявку
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- News Section -->
    <section class="py-16 bg-gray-50">
      <div class="container-custom">
        <div class="flex justify-between items-center mb-8">
          <div>
            <h2 class="text-3xl font-bold text-gray-900 mb-2">
              Последние новости
            </h2>
            <p class="text-gray-600">
              Будьте в курсе событий платформы
            </p>
          </div>
          <router-link
            to="/news"
            class="btn btn-outline"
          >
            Все новости
          </router-link>
        </div>
        
        <div
          v-if="newsLoading"
          class="text-center py-8"
        >
          <div class="loading-spinner w-8 h-8 mx-auto mb-4" />
          <p class="text-gray-600">
            Загрузка новостей...
          </p>
        </div>
        
        <div
          v-else-if="news.length === 0"
          class="text-center py-8"
        >
          <p class="text-gray-600">
            Новостей пока нет
          </p>
        </div>
        
        <div
          v-else
          class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          <article
            v-for="item in news"
            :key="item.id"
            class="card hover:shadow-lg transition-shadow"
          >
            <div class="p-6">
              <div class="flex items-center justify-between mb-4">
                <span class="badge badge-gray">{{ item.category_display }}</span>
                <span class="text-sm text-gray-500">{{ formatDate(item.published_at) }}</span>
              </div>
              
              <h3 class="text-xl font-semibold mb-2">
                {{ item.title }}
              </h3>
              <p class="text-gray-600 mb-4 line-clamp-2">
                {{ item.excerpt }}
              </p>
              
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-500">{{ item.author_name }}</span>
                <router-link
                  :to="`/news/${item.slug}`"
                  class="text-primary-600 hover:text-primary-800"
                >
                  Читать далее →
                </router-link>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-16 bg-primary-600 text-white">
      <div class="container-custom text-center">
        <h2 class="text-3xl font-bold mb-4">
          Готовы начать?
        </h2>
        <p class="text-xl mb-8 text-primary-100">
          Присоединяйтесь к сообществу волонтеров и начинайте делать мир лучше уже сегодня
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <router-link
            v-if="!authStore.isAuthenticated"
            to="/register/volunteer"
            class="btn bg-white text-primary-600 hover:bg-gray-100 btn-lg"
          >
            Стать волонтером
          </router-link>
          <router-link
            v-if="!authStore.isAuthenticated || authStore.isOrganization || authStore.isAdmin"
            to="/register/organization"
            class="btn btn-outline border-white text-white hover:bg-white hover:text-primary-600 btn-lg"
          >
            Создать проект
          </router-link>
          <router-link
            v-if="authStore.isAuthenticated"
            to="/dashboard"
            class="btn bg-white text-primary-600 hover:bg-gray-100 btn-lg"
          >
            Личный кабинет
          </router-link>
        </div>
      </div>
    </section>

    <teleport to="body">
      <div
        v-if="showApplicationModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
      >
        <div class="w-full max-w-xl rounded-2xl bg-white p-6 shadow-xl">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm text-gray-500">
                Заявка на проект
              </p>
              <h3 class="text-xl font-semibold text-gray-900">
                {{ selectedProject?.title }}
              </h3>
            </div>
            <button
              class="text-gray-400 hover:text-gray-600"
              @click="closeApplication"
            >
              ✕
            </button>
          </div>
          <p class="mt-2 text-sm text-gray-600">
            Расскажите, как вы хотите помочь, и укажите количество часов.
          </p>
          <form
            class="mt-6 space-y-4"
            @submit.prevent="submitApplication"
          >
            <div>
              <label class="form-label">Сопроводительное письмо</label>
              <textarea
                v-model="applicationForm.cover_letter"
                rows="4"
                class="form-input"
                placeholder="Например: могу помогать по выходным, есть опыт в организации мероприятий..."
              />
            </div>
            <div>
              <label class="form-label">Сколько часов готовы выделить</label>
              <input
                v-model.number="applicationForm.hours_committed"
                type="number"
                min="1"
                class="form-input"
                placeholder="5"
              >
            </div>
            <p
              v-if="applicationError"
              class="text-sm text-red-600"
            >
              {{ applicationError }}
            </p>
            <div class="flex flex-col sm:flex-row gap-3">
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="applicationLoading"
              >
                {{ applicationLoading ? 'Отправка...' : 'Отправить заявку' }}
              </button>
              <button
                type="button"
                class="btn btn-outline"
                @click="closeApplication"
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import type { Project, News } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()
const projects = ref<Project[]>([])
const news = ref<News[]>([])
const projectsLoading = ref(true)
const newsLoading = ref(true)
const stats = ref({
  users: { total: 0 },
  projects: { total: 0 },
  applications: { total: 0, total_hours: 0 }
})
const volunteerOfWeek = ref<{ volunteer: { id: number; name: string; avatar: string | null } | null; week_hours: number } | null>(null)
const showApplicationModal = ref(false)
const selectedProject = ref<Project | null>(null)
const applicationLoading = ref(false)
const applicationError = ref<string | null>(null)
const applicationForm = ref({
  cover_letter: '',
  hours_committed: 4
})

onMounted(async () => {
  await Promise.all([
    loadProjects(),
    loadNews(),
    loadStats(),
    loadVolunteerOfWeek(),
  ])
})

const loadProjects = async () => {
  try {
    projectsLoading.value = true
    const data = await apiService.getProjects({ status: 'active' })
    projects.value = data.results.slice(0, 6) // Show only 6 projects
  } catch (error) {
    console.error('Failed to load projects:', error)
  } finally {
    projectsLoading.value = false
  }
}

const loadNews = async () => {
  try {
    newsLoading.value = true
    const data = await apiService.getNews()
    news.value = data.results.slice(0, 3) // Show only 3 news items
  } catch (error) {
    console.error('Failed to load news:', error)
  } finally {
    newsLoading.value = false
  }
}

const loadStats = async () => {
  try {
    const data = await apiService.getStatistics()
    stats.value = data
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const loadVolunteerOfWeek = async () => {
  try {
    volunteerOfWeek.value = await apiService.getVolunteerOfWeek()
  } catch (error) {
    console.error('Failed to load volunteer of week:', error)
  }
}

const openApplication = (project: Project) => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'Login', query: { redirect: `/projects/${project.id}` } })
    return
  }
  selectedProject.value = project
  applicationForm.value = {
    cover_letter: '',
    hours_committed: 4
  }
  applicationError.value = null
  showApplicationModal.value = true
}

const closeApplication = () => {
  showApplicationModal.value = false
  selectedProject.value = null
  applicationError.value = null
}

const submitApplication = async () => {
  if (!selectedProject.value) return
  try {
    applicationLoading.value = true
    applicationError.value = null
    await apiService.createApplication({
      project: selectedProject.value.id,
      cover_letter: applicationForm.value.cover_letter || 'Готов(а) помочь проекту',
      hours_committed: applicationForm.value.hours_committed || 4
    })
    closeApplication()
    router.push({ name: 'MyApplications' })
  } catch (error: any) {
    applicationError.value = error?.response?.data?.detail || 'Не удалось отправить заявку'
  } finally {
    applicationLoading.value = false
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}
</script>
