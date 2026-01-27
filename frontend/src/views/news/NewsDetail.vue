<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="loading-spinner w-8 h-8 mr-3"></div>
      <span class="text-gray-600">Загрузка новости...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex items-center justify-center py-20">
      <div class="text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">Новость не найдена</h3>
        <p class="mt-1 text-sm text-gray-500">
          Новость, которую вы ищете, не существует или была удалена
        </p>
        <div class="mt-6">
          <router-link to="/news" class="btn btn-primary">
            ← Вернуться к новостям
          </router-link>
        </div>
      </div>
    </div>

    <!-- News Content -->
    <div v-else-if="newsItem" class="container-custom py-8">
      <!-- Breadcrumb -->
      <nav class="flex mb-8" aria-label="Breadcrumb">
        <ol class="flex items-center space-x-2">
          <li>
            <router-link to="/" class="text-gray-500 hover:text-gray-700">
              Главная
            </router-link>
          </li>
          <li>
            <span class="text-gray-400">/</span>
          </li>
          <li>
            <router-link to="/news" class="text-gray-500 hover:text-gray-700">
              Новости
            </router-link>
          </li>
          <li>
            <span class="text-gray-400">/</span>
          </li>
          <li>
            <span class="text-gray-900">{{ newsItem.title }}</span>
          </li>
        </ol>
      </nav>

      <!-- Article Header -->
      <article class="max-w-4xl mx-auto">
        <!-- Header Image -->
        <div class="relative h-64 md:h-96 bg-gray-200 rounded-lg overflow-hidden mb-8">
          <img
            v-if="newsItem.image"
            :src="newsItem.image"
            :alt="newsItem.title"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full bg-gradient-to-r from-primary-500 to-primary-600 flex items-center justify-center">
            <svg class="w-24 h-24 text-white opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
          </div>
          
          <!-- Badges -->
          <div class="absolute top-4 left-4 flex space-x-2">
            <span class="badge badge-primary">
              {{ newsItem.category_display }}
            </span>
            <span v-if="newsItem.is_important" class="badge bg-red-500 text-white">
              Важно
            </span>
            <span v-if="newsItem.is_featured" class="badge bg-yellow-500 text-white">
              Избранное
            </span>
          </div>
        </div>

        <!-- Article Info -->
        <div class="mb-8">
          <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            {{ newsItem.title }}
          </h1>
          
          <div class="flex flex-wrap items-center gap-4 text-sm text-gray-600">
            <div class="flex items-center">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              {{ formatDate(newsItem.published_at) }}
            </div>
            
            <div class="flex items-center">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              {{ newsItem.author_name }}
            </div>
            
            <div class="flex items-center">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3v-4m0 6h.01M12 12v4m0 6h.01" />
              </svg>
              {{ getReadingTime(newsItem.content) }} мин чтения
            </div>
          </div>
        </div>

        <!-- Excerpt -->
        <div v-if="newsItem.excerpt" class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-8">
          <p class="text-lg text-blue-700 italic">
            {{ newsItem.excerpt }}
          </p>
        </div>

        <!-- Content -->
        <div class="prose prose-lg max-w-none mb-8">
          <div v-html="newsItem.content" class="text-gray-700"></div>
        </div>

        <!-- Tags -->
        <div v-if="newsItem.tags && newsItem.tags.length > 0" class="mb-8">
          <h3 class="text-lg font-semibold text-gray-900 mb-3">Теги</h3>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="tag in newsItem.tags"
              :key="tag"
              class="badge badge-gray"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <!-- Share Section -->
        <div class="border-t border-gray-200 pt-8 mb-8">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Поделиться новостью</h3>
          <div class="flex space-x-4">
            <button class="btn btn-outline flex items-center">
              <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              Facebook
            </button>
            <button class="btn btn-outline flex items-center">
              <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 00-8.384 4.482A9.953 9.953 0 002.458 4.572c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
              </svg>
              Twitter
            </button>
            <button class="btn btn-outline flex items-center">
              <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
              </svg>
              LinkedIn
            </button>
            <button @click="copyLink" class="btn btn-outline flex items-center">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Копировать ссылку
            </button>
          </div>
        </div>

        <!-- Related News -->
        <div v-if="relatedNews.length > 0" class="border-t border-gray-200 pt-8">
          <h3 class="text-xl font-semibold text-gray-900 mb-6">Похожие новости</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <article
              v-for="item in relatedNews"
              :key="item.id"
              class="group cursor-pointer"
              @click="$router.push(`/news/${item.slug}`)"
            >
              <div class="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow">
                <div class="relative h-32 bg-gray-200">
                  <img
                    v-if="item.image"
                    :src="item.image"
                    :alt="item.title"
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                  />
                  <div v-else class="w-full h-full bg-gradient-to-r from-primary-500 to-primary-600 flex items-center justify-center">
                    <svg class="w-8 h-8 text-white opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                    </svg>
                  </div>
                </div>
                
                <div class="p-4">
                  <div class="flex items-center justify-between mb-2">
                    <span class="badge badge-primary text-xs">
                      {{ item.category_display }}
                    </span>
                    <span class="text-xs text-gray-500">
                      {{ formatDate(item.published_at) }}
                    </span>
                  </div>
                  
                  <h4 class="text-sm font-medium text-gray-900 mb-2 line-clamp-2 group-hover:text-primary-600 transition-colors">
                    {{ item.title }}
                  </h4>
                  
                  <p class="text-xs text-gray-600 line-clamp-2">
                    {{ item.excerpt }}
                  </p>
                </div>
              </div>
            </article>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiService from '@/services/api'
import type { News } from '@/types/api'

const route = useRoute()
const router = useRouter()

const newsItem = ref<News | null>(null)
const relatedNews = ref<News[]>([])
const loading = ref(true)
const error = ref(false)

onMounted(async () => {
  await Promise.all([
    loadNews(),
    loadRelatedNews()
  ])
})

const loadNews = async () => {
  try {
    loading.value = true
    error.value = false
    
    const slug = route.params.slug as string
    newsItem.value = await apiService.getNewsBySlug(slug)
  } catch (err) {
    error.value = true
    console.error('Failed to load news:', err)
  } finally {
    loading.value = false
  }
}

const loadRelatedNews = async () => {
  try {
    const response = await apiService.getNews({
      limit: 3,
      exclude: newsItem.value?.id
    })
    relatedNews.value = response.results
  } catch (error) {
    console.error('Failed to load related news:', error)
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

const copyLink = async () => {
  try {
    const url = window.location.href
    await navigator.clipboard.writeText(url)
    
    // Show success message (you could use a toast notification here)
    alert('Ссылка скопирована в буфер обмена!')
  } catch (error) {
    console.error('Failed to copy link:', error)
  }
}
</script>
