<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="container-custom py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Новости</h1>
            <p class="text-gray-600 mt-1">Будьте в курсе событий платформы</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container-custom py-8">
      <!-- Filters -->
      <div class="bg-white p-4 rounded-lg shadow mb-6">
        <div class="flex flex-wrap items-center gap-4">
          <div>
            <label class="form-label text-sm">Категория</label>
            <select v-model="filters.category" @change="loadNews" class="form-input">
              <option value="">Все категории</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="form-label text-sm">Сортировка</label>
            <select v-model="filters.ordering" @change="loadNews" class="form-input">
              <option value="-published_at">Новые сначала</option>
              <option value="published_at">Старые сначала</option>
              <option value="-title">По алфавиту (А-Я)</option>
              <option value="title">По алфавиту (Я-А)</option>
            </select>
          </div>
          
          <div class="flex-1">
            <label class="form-label text-sm">Поиск</label>
            <input
              v-model="filters.search"
              @input="debouncedSearch"
              type="text"
              placeholder="Поиск по заголовку или содержимому..."
              class="form-input"
            />
          </div>
        </div>
      </div>

      <!-- Featured News -->
      <div v-if="featuredNews.length > 0" class="mb-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Избранные новости</h2>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div
            v-for="news in featuredNews"
            :key="news.id"
            class="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow cursor-pointer"
            @click="$router.push(`/news/${news.slug}`)"
          >
            <div class="relative h-48 bg-gradient-to-r from-primary-500 to-primary-600">
              <img
                v-if="news.image"
                :src="news.image"
                :alt="news.title"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex items-center justify-center">
                <svg class="w-16 h-16 text-white opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
              </div>
              
              <div class="absolute top-4 left-4">
                <span class="badge bg-yellow-500 text-white">
                  Избранное
                </span>
              </div>
              
              <div class="absolute bottom-4 left-4 right-4">
                <h3 class="text-xl font-bold text-white mb-2 line-clamp-2">
                  {{ news.title }}
                </h3>
                <p class="text-white text-sm opacity-90">
                  {{ formatDate(news.published_at) }}
                </p>
              </div>
            </div>
            
            <div class="p-6">
              <p class="text-gray-600 line-clamp-3 mb-4">
                {{ news.excerpt }}
              </p>
              
              <div class="flex items-center justify-between">
                <span class="badge badge-primary">
                  {{ news.category_display }}
                </span>
                <span class="text-sm text-gray-500">
                  {{ news.author_name }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- News List -->
      <div class="bg-white rounded-lg shadow">
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-12">
          <div class="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p class="text-gray-600">Загрузка новостей...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="news.length === 0" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">Новостей пока нет</h3>
          <p class="mt-1 text-sm text-gray-500">
            Следите за обновлениями, чтобы быть в курсе событий
          </p>
        </div>

        <!-- News Grid -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
          <article
            v-for="item in news"
            :key="item.id"
            class="group cursor-pointer"
            @click="$router.push(`/news/${item.slug}`)"
          >
            <div class="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-all duration-200">
              <!-- Image -->
              <div class="relative h-40 bg-gray-200">
                <img
                  v-if="item.image"
                  :src="item.image"
                  :alt="item.title"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                />
                <div v-else class="w-full h-full bg-gradient-to-r from-primary-500 to-primary-600 flex items-center justify-center">
                  <svg class="w-12 h-12 text-white opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                  </svg>
                </div>
                
                <!-- Category Badge -->
                <div class="absolute top-2 left-2">
                  <span class="badge badge-primary text-xs">
                    {{ item.category_display }}
                  </span>
                </div>
                
                <!-- Important Badge -->
                <div v-if="item.is_important" class="absolute top-2 right-2">
                  <span class="badge bg-red-500 text-white text-xs">
                    Важно
                  </span>
                </div>
              </div>
              
              <!-- Content -->
              <div class="p-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs text-gray-500">
                    {{ formatDate(item.published_at) }}
                  </span>
                  <span class="text-xs text-gray-500">
                    {{ item.author_name }}
                  </span>
                </div>
                
                <h3 class="text-lg font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-primary-600 transition-colors">
                  {{ item.title }}
                </h3>
                
                <p class="text-gray-600 text-sm line-clamp-3 mb-3">
                  {{ item.excerpt }}
                </p>
                
                <div class="flex items-center justify-between">
                  <span class="text-xs text-gray-500">
                    {{ getReadingTime(item.excerpt) }} мин чтения
                  </span>
                  <span class="text-primary-600 text-sm font-medium group-hover:text-primary-700">
                    Читать далее →
                  </span>
                </div>
              </div>
            </div>
          </article>
        </div>
        
        <!-- Pagination -->
        <div v-if="pagination.totalPages > 1" class="px-6 py-4 border-t border-gray-200">
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-700">
              Показано {{ pagination.start }}-{{ pagination.end }} из {{ pagination.total }} новостей
            </div>
            
            <div class="flex space-x-2">
              <button
                @click="goToPage(pagination.currentPage - 1)"
                :disabled="pagination.currentPage === 1"
                class="btn btn-outline"
                :class="{ 'opacity-50 cursor-not-allowed': pagination.currentPage === 1 }"
              >
                ←
              </button>
              
              <div class="flex space-x-1">
                <button
                  v-for="page in pagination.pages"
                  :key="page"
                  @click="goToPage(page)"
                  :class="[
                    'btn',
                    page === pagination.currentPage
                      ? 'btn-primary'
                      : 'btn-outline'
                  ]"
                >
                  {{ page }}
                </button>
              </div>
              
              <button
                @click="goToPage(pagination.currentPage + 1)"
                :disabled="pagination.currentPage === pagination.totalPages"
                class="btn btn-outline"
                :class="{ 'opacity-50 cursor-not-allowed': pagination.currentPage === pagination.totalPages }"
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
import apiService from '@/services/api'
import type { News, Category } from '@/types/api'

const router = useRouter()

const news = ref<News[]>([])
const featuredNews = ref<News[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)

const filters = reactive({
  category: '',
  ordering: '-published_at',
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
    loadNews(),
    loadFeaturedNews(),
    loadCategories()
  ])
})

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    pagination.currentPage = 1
    loadNews()
  }, 500)
}

const loadNews = async () => {
  try {
    loading.value = true
    
    const params = {
      ...filters,
      page: pagination.currentPage,
      is_featured: false
    }
    
    const response = await apiService.getNews(params)
    news.value = response.results
    
    // Update pagination
    pagination.total = response.count
    pagination.totalPages = Math.ceil(response.count / 9) // 9 items per page
    pagination.start = (pagination.currentPage - 1) * 9 + 1
    pagination.end = Math.min(pagination.currentPage * 9, response.count)
    
    // Generate page numbers
    generatePageNumbers()
  } catch (error) {
    console.error('Failed to load news:', error)
  } finally {
    loading.value = false
  }
}

const loadFeaturedNews = async () => {
  try {
    const response = await apiService.getNews({
      is_featured: true,
      limit: 2
    })
    featuredNews.value = response.results
  } catch (error) {
    console.error('Failed to load featured news:', error)
  }
}

const loadCategories = async () => {
  try {
    const response = await apiService.getNewsCategories()
    categories.value = response.results
  } catch (error) {
    console.error('Failed to load categories:', error)
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
    loadNews()
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const getReadingTime = (text: string) => {
  const wordsPerMinute = 200
  const words = text.split(' ').length
  return Math.ceil(words / wordsPerMinute)
}
</script>
