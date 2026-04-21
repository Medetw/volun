<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="container-custom max-w-3xl">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">
        Создать новость
      </h1>

      <div
        v-if="errorMsg"
        class="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700"
      >
        {{ errorMsg }}
      </div>

      <form
        class="bg-white p-6 rounded-lg shadow space-y-4"
        @submit.prevent="submit"
      >
        <div>
          <label class="form-label">Заголовок *</label>
          <input
            v-model="form.title"
            type="text"
            class="form-input w-full"
            required
          >
        </div>

        <div>
          <label class="form-label">URL (slug) *</label>
          <input
            v-model="form.slug"
            type="text"
            class="form-input w-full"
            placeholder="meropriyatiye-2026"
            pattern="[a-z0-9-]+"
            required
          >
          <p class="text-xs text-gray-500 mt-1">
            Только латиница, цифры и дефисы.
          </p>
        </div>

        <div>
          <label class="form-label">Категория</label>
          <select
            v-model="form.category"
            class="form-input w-full"
          >
            <option value="general">
              Общие новости
            </option>
            <option value="events">
              Мероприятия
            </option>
            <option value="announcements">
              Объявления
            </option>
            <option value="success_stories">
              Истории успеха
            </option>
            <option value="partners">
              Партнёры
            </option>
          </select>
        </div>

        <div>
          <label class="form-label">Краткое описание</label>
          <textarea
            v-model="form.excerpt"
            rows="2"
            class="form-input w-full"
            maxlength="500"
          />
        </div>

        <div>
          <label class="form-label">Содержание *</label>
          <textarea
            v-model="form.content"
            rows="10"
            class="form-input w-full"
            required
          />
        </div>

        <div>
          <label class="form-label">Изображение</label>
          <input
            type="file"
            accept="image/*"
            class="form-input w-full"
            @change="onFile"
          >
        </div>

        <div>
          <label class="form-label">Статус</label>
          <select
            v-model="form.status"
            class="form-input w-full"
          >
            <option value="draft">
              Черновик
            </option>
            <option value="published">
              Опубликовано
            </option>
          </select>
        </div>

        <!-- Featured (реклама) — только admin -->
        <div
          v-if="authStore.isAdmin"
          class="flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded"
        >
          <input
            id="featured"
            v-model="form.featured"
            type="checkbox"
            class="h-4 w-4"
          >
          <label
            for="featured"
            class="text-sm"
          >
            <strong>Реклама (featured)</strong> — новость будет отмечена как избранная. Только админы.
          </label>
        </div>

        <div class="flex gap-3 justify-end pt-3 border-t">
          <router-link
            to="/news"
            class="btn btn-outline"
          >
            Отмена
          </router-link>
          <button
            type="submit"
            :disabled="submitting"
            class="btn btn-primary"
          >
            {{ submitting ? 'Создание...' : 'Создать' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import apiService from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  title: '',
  slug: '',
  category: 'general',
  excerpt: '',
  content: '',
  status: 'published',
  featured: false,
  image: null as File | null,
})

const submitting = ref(false)
const errorMsg = ref('')

function onFile(e: Event) {
  form.image = (e.target as HTMLInputElement).files?.[0] ?? null
}

async function submit() {
  submitting.value = true
  errorMsg.value = ''
  try {
    const fd = new FormData()
    fd.append('title', form.title.trim())
    fd.append('slug', form.slug.trim())
    fd.append('category', form.category)
    fd.append('excerpt', form.excerpt)
    fd.append('content', form.content)
    fd.append('status', form.status)
    if (authStore.isAdmin && form.featured) fd.append('featured', 'true')
    if (form.image) fd.append('image', form.image)

    await apiService.createNews(fd as any)
    router.push('/news')
  } catch (e: any) {
    const data = e?.response?.data
    errorMsg.value = data?.detail || data?.slug?.[0] || data?.title?.[0] || 'Ошибка создания'
  } finally {
    submitting.value = false
  }
}
</script>
