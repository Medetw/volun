<template>
  <div>
    <!-- Hero Section -->
    <section class="bg-gradient-to-r from-primary-600 to-primary-800 text-white">
      <div class="container-custom py-20">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div>
            <h1 class="text-4xl lg:text-6xl font-bold mb-6">
              Помогайте другим. 
              <span class="text-primary-200">Меняйте мир.</span>
            </h1>
            <p class="text-xl mb-8 text-primary-100">
              Присоединяйтесь к крупнейшей волонтерской платформе Казахстана. 
              Найдите проекты, которые вам интересны, или создайте собственные.
            </p>
            <div class="flex flex-col sm:flex-row gap-4">
              <router-link to="/register/volunteer" class="btn bg-white text-primary-600 hover:bg-gray-100 btn-lg">
                Стать волонтером
              </router-link>
              <router-link to="/register/organization" class="btn btn-outline border-white text-white hover:bg-white hover:text-primary-600 btn-lg">
                Для организаций
              </router-link>
            </div>
          </div>
          <div class="hidden lg:block">
            <img src="/api/placeholder/600/400" alt="Волонтеры" class="rounded-lg shadow-2xl" />
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="py-16 bg-white">
      <div class="container-custom">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
          <div>
            <div class="text-4xl font-bold text-primary-600 mb-2">{{ stats.users.total }}</div>
            <div class="text-gray-600">Пользователей</div>
          </div>
          <div>
            <div class="text-4xl font-bold text-primary-600 mb-2">{{ stats.projects.total }}</div>
            <div class="text-gray-600">Проектов</div>
          </div>
          <div>
            <div class="text-4xl font-bold text-primary-600 mb-2">{{ stats.applications.total }}</div>
            <div class="text-gray-600">Заявок</div>
          </div>
          <div>
            <div class="text-4xl font-bold text-primary-600 mb-2">{{ stats.applications.total_hours }}</div>
            <div class="text-gray-600">Часов помощи</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-16 bg-gray-50">
      <div class="container-custom">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">Как это работает?</h2>
          <p class="text-xl text-gray-600">Простые шаги для начала волонтерской деятельности</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold mb-2">Создайте профиль</h3>
            <p class="text-gray-600">Зарегистрируйтесь как волонтер или организация</p>
          </div>
          
          <div class="text-center">
            <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold mb-2">Найдите проекты</h3>
            <p class="text-gray-600">Ищите интересные проекты или создавайте свои</p>
          </div>
          
          <div class="text-center">
            <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold mb-2">Помогайте другим</h3>
            <p class="text-gray-600">Участвуйте в проектах и делайте мир лучше</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Featured Projects -->
    <section class="py-16 bg-white">
      <div class="container-custom">
        <div class="flex justify-between items-center mb-8">
          <div>
            <h2 class="text-3xl font-bold text-gray-900 mb-2">Активные проекты</h2>
            <p class="text-gray-600">Участвуйте в текущих волонтерских инициативах</p>
          </div>
          <router-link to="/projects" class="btn btn-primary">
            Все проекты
          </router-link>
        </div>
        
        <div v-if="projectsLoading" class="text-center py-8">
          <div class="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p class="text-gray-600">Загрузка проектов...</p>
        </div>
        
        <div v-else-if="projects.length === 0" class="text-center py-8">
          <p class="text-gray-600">Активных проектов пока нет</p>
        </div>
        
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="project in projects" :key="project.id" class="card hover:shadow-lg transition-shadow">
            <div class="p-6">
              <div class="flex items-center justify-between mb-4">
                <span class="badge badge-primary">{{ project.category.name }}</span>
                <span class="status-active">{{ project.status }}</span>
              </div>
              
              <h3 class="text-xl font-semibold mb-2">{{ project.title }}</h3>
              <p class="text-gray-600 mb-4 line-clamp-2">{{ project.description }}</p>
              
              <div class="flex items-center justify-between text-sm text-gray-500 mb-4">
                <span>{{ project.organization_name }}</span>
                <span>{{ project.volunteers_remaining }}/{{ project.volunteers_needed }} мест</span>
              </div>
              
              <div class="w-full bg-gray-200 rounded-full h-2 mb-4">
                <div 
                  class="bg-primary-600 h-2 rounded-full" 
                  :style="{ width: `${((project.volunteers_needed - project.volunteers_remaining) / project.volunteers_needed) * 100}%` }"
                ></div>
              </div>
              
              <router-link :to="`/projects/${project.id}`" class="btn btn-primary w-full">
                Подробнее
              </router-link>
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
            <h2 class="text-3xl font-bold text-gray-900 mb-2">Последние новости</h2>
            <p class="text-gray-600">Будьте в курсе событий платформы</p>
          </div>
          <router-link to="/news" class="btn btn-outline">
            Все новости
          </router-link>
        </div>
        
        <div v-if="newsLoading" class="text-center py-8">
          <div class="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p class="text-gray-600">Загрузка новостей...</p>
        </div>
        
        <div v-else-if="news.length === 0" class="text-center py-8">
          <p class="text-gray-600">Новостей пока нет</p>
        </div>
        
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <article v-for="item in news" :key="item.id" class="card hover:shadow-lg transition-shadow">
            <div class="p-6">
              <div class="flex items-center justify-between mb-4">
                <span class="badge badge-gray">{{ item.category_display }}</span>
                <span class="text-sm text-gray-500">{{ formatDate(item.published_at) }}</span>
              </div>
              
              <h3 class="text-xl font-semibold mb-2">{{ item.title }}</h3>
              <p class="text-gray-600 mb-4 line-clamp-2">{{ item.excerpt }}</p>
              
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-500">{{ item.author_name }}</span>
                <router-link :to="`/news/${item.slug}`" class="text-primary-600 hover:text-primary-800">
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
        <h2 class="text-3xl font-bold mb-4">Готовы начать?</h2>
        <p class="text-xl mb-8 text-primary-100">
          Присоединяйтесь к сообществу волонтеров и начинайте делать мир лучше уже сегодня
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <router-link to="/register/volunteer" class="btn bg-white text-primary-600 hover:bg-gray-100 btn-lg">
            Стать волонтером
          </router-link>
          <router-link to="/projects" class="btn btn-outline border-white text-white hover:bg-white hover:text-primary-600 btn-lg">
            Найти проекты
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiService from '@/services/api'
import type { Project, News } from '@/types/api'

const projects = ref<Project[]>([])
const news = ref<News[]>([])
const projectsLoading = ref(true)
const newsLoading = ref(true)
const stats = ref({
  users: { total: 0 },
  projects: { total: 0 },
  applications: { total: 0, total_hours: 0 }
})

onMounted(async () => {
  await Promise.all([
    loadProjects(),
    loadNews(),
    loadStats()
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
