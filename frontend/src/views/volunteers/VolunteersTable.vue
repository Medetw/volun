<template>
  <div class="min-h-screen bg-gray-50 py-6">
    <div class="container-custom">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">
            Волонтёры
          </h1>
          <p class="text-gray-600 mt-1">
            Все волонтёры платформы. Строки красного цвета — в чёрном списке.
          </p>
        </div>
        <div class="relative w-full sm:w-80">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск: имя, email, username..."
            class="form-input pl-10 pr-4 w-full"
            @input="debouncedSearch"
          >
          <svg
            class="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
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

      <!-- Messages -->
      <div
        v-if="message"
        class="mb-4 p-3 bg-green-50 border border-green-200 rounded text-sm text-green-700"
      >
        {{ message }}
      </div>
      <div
        v-if="errorMsg"
        class="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700"
      >
        {{ errorMsg }}
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="bg-white p-4 rounded-lg shadow">
          <div class="text-sm text-gray-500">
            Всего волонтёров
          </div>
          <div class="text-2xl font-bold">
            {{ volunteers.length }}
          </div>
        </div>
        <div class="bg-white p-4 rounded-lg shadow">
          <div class="text-sm text-gray-500">
            Активных
          </div>
          <div class="text-2xl font-bold text-green-600">
            {{ activeCount }}
          </div>
        </div>
        <div class="bg-white p-4 rounded-lg shadow">
          <div class="text-sm text-gray-500">
            В ЧС
          </div>
          <div class="text-2xl font-bold text-red-600">
            {{ bannedCount }}
          </div>
        </div>
      </div>

      <!-- Table -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div
          v-if="loading"
          class="text-center py-12 text-gray-500"
        >
          Загрузка...
        </div>
        <div
          v-else-if="volunteers.length === 0"
          class="text-center py-12 text-gray-500"
        >
          Волонтёров не найдено.
        </div>
        <table
          v-else
          class="w-full text-sm"
        >
          <thead class="bg-gray-50 text-left text-xs uppercase text-gray-600">
            <tr>
              <th class="p-3">
                Имя
              </th>
              <th class="p-3">
                Email
              </th>
              <th class="p-3">
                Город
              </th>
              <th class="p-3">
                Часы
              </th>
              <th class="p-3">
                Статус
              </th>
              <th class="p-3">
                Действия
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="v in volunteers"
              :key="v.id"
              :class="['border-b hover:bg-gray-50', v.is_banned ? 'bg-red-50 hover:bg-red-100' : '']"
            >
              <td
                class="p-3"
                :class="v.is_banned ? 'text-red-700 font-semibold' : 'font-medium'"
              >
                {{ v.name }}
                <div class="text-xs text-gray-500 font-normal">
                  @{{ v.username }}
                </div>
              </td>
              <td class="p-3">
                {{ v.email }}
              </td>
              <td class="p-3">
                {{ v.city || '—' }}
              </td>
              <td class="p-3 font-medium">
                {{ v.volunteer_hours }} ч
              </td>
              <td class="p-3">
                <span
                  v-if="v.is_banned"
                  class="badge bg-red-500 text-white text-xs"
                >В ЧС</span>
                <span
                  v-else
                  class="badge badge-success text-xs"
                >Активен</span>
              </td>
              <td class="p-3">
                <button
                  v-if="!v.is_banned"
                  class="btn btn-sm bg-red-500 text-white hover:bg-red-600"
                  @click="openBanForm(v)"
                >
                  В ЧС
                </button>
                <button
                  v-else
                  class="btn btn-sm btn-outline"
                  :disabled="unbanLoadingId === v.id"
                  @click="handleUnban(v)"
                >
                  {{ unbanLoadingId === v.id ? '...' : 'Снять ЧС' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Ban modal -->
      <div
        v-if="banTarget"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click.self="banTarget = null"
      >
        <div class="bg-white rounded-lg w-full max-w-lg p-6">
          <h2 class="text-xl font-semibold text-red-700 mb-4">
            Добавить в ЧС: {{ banTarget.name }}
          </h2>
          <div class="space-y-3">
            <div>
              <label class="form-label">Причина *</label>
              <textarea
                v-model="banForm.reason"
                rows="3"
                placeholder="Опишите причину блокировки..."
                class="form-input w-full"
              />
            </div>
            <div>
              <label class="form-label">Заблокировать до (необязательно)</label>
              <input
                v-model="banForm.banned_until"
                type="datetime-local"
                class="form-input w-full"
              >
              <p class="text-xs text-gray-500 mt-1">
                Пусто — бессрочно.
              </p>
            </div>
          </div>
          <div class="flex gap-2 mt-6 justify-end">
            <button
              class="btn btn-outline"
              @click="banTarget = null"
            >
              Отмена
            </button>
            <button
              class="btn bg-red-500 text-white hover:bg-red-600"
              :disabled="banLoading || !banForm.reason.trim()"
              @click="submitBan"
            >
              {{ banLoading ? '...' : 'Заблокировать' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import apiService from '@/services/api'

interface Volunteer {
  id: number
  username: string
  name: string
  email: string
  city: string
  region: string
  volunteer_hours: number
  is_banned: boolean
}

const volunteers = ref<Volunteer[]>([])
const loading = ref(true)
const searchQuery = ref('')
const message = ref('')
const errorMsg = ref('')

const banTarget = ref<Volunteer | null>(null)
const banForm = reactive({ reason: '', banned_until: '' })
const banLoading = ref(false)
const unbanLoadingId = ref<number | null>(null)

let searchTimeout: ReturnType<typeof setTimeout>

const activeCount = computed(() => volunteers.value.filter((v) => !v.is_banned).length)
const bannedCount = computed(() => volunteers.value.filter((v) => v.is_banned).length)

onMounted(load)

async function load() {
  loading.value = true
  errorMsg.value = ''
  try {
    volunteers.value = await apiService.getVolunteerList({
      search: searchQuery.value || undefined,
    })
  } catch {
    errorMsg.value = 'Не удалось загрузить волонтёров'
  } finally {
    loading.value = false
  }
}

function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(load, 400)
}

function flash(text: string) {
  message.value = text
  setTimeout(() => (message.value = ''), 3000)
}

function openBanForm(v: Volunteer) {
  banTarget.value = v
  banForm.reason = ''
  banForm.banned_until = ''
}

async function submitBan() {
  if (!banTarget.value || !banForm.reason.trim()) return
  banLoading.value = true
  errorMsg.value = ''
  try {
    await apiService.banVolunteer({
      volunteer: banTarget.value.id,
      reason: banForm.reason.trim(),
      banned_until: banForm.banned_until || null,
    })
    flash('Волонтёр добавлен в ЧС')
    banTarget.value = null
    await load()
  } catch (e: any) {
    const data = e?.response?.data
    errorMsg.value = data?.reason?.[0] || data?.volunteer?.[0] || data?.banned_until?.[0] || 'Ошибка'
  } finally {
    banLoading.value = false
  }
}

async function handleUnban(v: Volunteer) {
  if (!confirm(`Снять ${v.name} с чёрного списка?`)) return
  unbanLoadingId.value = v.id
  errorMsg.value = ''
  try {
    // Сначала найдём активную запись ЧС
    const check = await apiService.checkBlacklist(v.id)
    if (!check.is_banned || !check.entry) {
      errorMsg.value = 'Активная запись ЧС не найдена'
      return
    }
    await apiService.unbanVolunteer(check.entry.id)
    flash('Волонтёр снят с ЧС')
    await load()
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.error || 'Ошибка при снятии с ЧС'
  } finally {
    unbanLoadingId.value = null
  }
}
</script>
