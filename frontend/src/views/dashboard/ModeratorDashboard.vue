<template>
  <div class="container-custom py-8">
    <div class="mb-8 flex items-start justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          Панель модератора
        </h1>
        <p
          v-if="profile?.department"
          class="mt-1 text-gray-500"
        >
          {{ profile.department }}
        </p>
      </div>
      <!-- RBAC-бейджи -->
      <div
        v-if="profile"
        class="flex flex-wrap gap-2"
      >
        <span
          :class="profile.can_view_volunteers ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-400'"
          class="rounded-full px-3 py-1 text-xs font-medium"
        >
          {{ profile.can_view_volunteers ? '✓' : '✗' }} Волонтёры
        </span>
        <span
          :class="profile.can_manage_hours ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-400'"
          class="rounded-full px-3 py-1 text-xs font-medium"
        >
          {{ profile.can_manage_hours ? '✓' : '✗' }} Учёт часов
        </span>
        <span
          :class="profile.can_manage_certificates ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-400'"
          class="rounded-full px-3 py-1 text-xs font-medium"
        >
          {{ profile.can_manage_certificates ? '✓' : '✗' }} Сертификаты
        </span>
      </div>
    </div>

    <!-- Табы -->
    <div class="mb-6 flex gap-1 border-b border-gray-200">
      <button
        v-if="profile?.can_view_volunteers"
        :class="activeTab === 'volunteers' ? 'border-b-2 border-primary-600 text-primary-600' : 'text-gray-500 hover:text-gray-700'"
        class="px-4 py-2 text-sm font-medium"
        @click="activeTab = 'volunteers'"
      >
        Волонтёры
      </button>
      <button
        v-if="profile?.can_manage_hours"
        :class="activeTab === 'hours' ? 'border-b-2 border-primary-600 text-primary-600' : 'text-gray-500 hover:text-gray-700'"
        class="px-4 py-2 text-sm font-medium"
        @click="activeTab = 'hours'"
      >
        Учёт часов
      </button>
      <button
        v-if="profile?.can_manage_certificates"
        :class="activeTab === 'certificates' ? 'border-b-2 border-primary-600 text-primary-600' : 'text-gray-500 hover:text-gray-700'"
        class="px-4 py-2 text-sm font-medium"
        @click="activeTab = 'certificates'"
      >
        Сертификаты
      </button>
    </div>

    <!-- ТАБ: Волонтёры -->
    <div v-if="activeTab === 'volunteers' && profile?.can_view_volunteers">
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900">
            Список волонтёров
          </h2>
          <input
            v-model="volunteerSearch"
            type="text"
            placeholder="Поиск..."
            class="form-input text-sm py-1 w-48"
          >
        </div>

        <div
          v-if="volunteersLoading"
          class="text-center py-8"
        >
          <div class="loading-spinner w-8 h-8 mx-auto" />
        </div>
        <div
          v-else
          class="overflow-x-auto"
        >
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b text-left text-gray-500">
                <th class="pb-3 pr-4">
                  Имя
                </th>
                <th class="pb-3 pr-4">
                  Логин
                </th>
                <th class="pb-3 pr-4">
                  Email
                </th>
                <th class="pb-3 pr-4">
                  Город
                </th>
                <th class="pb-3">
                  Часы
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="v in filteredVolunteers"
                :key="v.id"
                class="border-b border-gray-100 last:border-0"
              >
                <td class="py-3 pr-4 font-medium text-gray-900">
                  {{ v.name }}
                </td>
                <td class="py-3 pr-4 text-gray-500">
                  {{ v.username }}
                </td>
                <td class="py-3 pr-4 text-gray-500">
                  {{ v.email }}
                </td>
                <td class="py-3 pr-4 text-gray-500">
                  {{ v.city || '—' }}
                </td>
                <td class="py-3">
                  <span class="inline-flex items-center rounded-full bg-primary-50 px-2 py-0.5 text-xs font-semibold text-primary-700">
                    {{ v.volunteer_hours }} ч
                  </span>
                </td>
              </tr>
              <tr v-if="filteredVolunteers.length === 0">
                <td
                  colspan="5"
                  class="py-8 text-center text-gray-500"
                >
                  Ничего не найдено
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ТАБ: Учёт часов -->
    <div
      v-if="activeTab === 'hours' && profile?.can_manage_hours"
      class="grid grid-cols-1 lg:grid-cols-3 gap-8"
    >
      <!-- Форма -->
      <div class="lg:col-span-1">
        <div class="card p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">
            Внести часы
          </h2>
          <form
            class="space-y-4"
            @submit.prevent="submitHours"
          >
            <div>
              <label class="form-label">Волонтёр</label>
              <select
                v-model="hoursForm.volunteer"
                class="form-input"
                required
              >
                <option
                  value=""
                  disabled
                >
                  Выберите волонтёра
                </option>
                <option
                  v-for="v in volunteers"
                  :key="v.id"
                  :value="v.id"
                >
                  {{ v.name }} ({{ v.username }})
                </option>
              </select>
            </div>
            <div>
              <label class="form-label">Часов</label>
              <input
                v-model.number="hoursForm.hours"
                type="number"
                min="1"
                class="form-input"
                required
              >
            </div>
            <div>
              <label class="form-label">Дата</label>
              <input
                v-model="hoursForm.date"
                type="date"
                class="form-input"
                required
              >
            </div>
            <div>
              <label class="form-label">Описание</label>
              <textarea
                v-model="hoursForm.description"
                rows="3"
                class="form-input"
                placeholder="Краткое описание деятельности..."
              />
            </div>
            <p
              v-if="hoursError"
              class="text-sm text-red-600"
            >
              {{ hoursError }}
            </p>
            <p
              v-if="hoursSuccess"
              class="text-sm text-green-600"
            >
              {{ hoursSuccess }}
            </p>
            <button
              type="submit"
              class="btn btn-primary w-full"
              :disabled="hoursLoading"
            >
              {{ hoursLoading ? 'Сохранение...' : 'Добавить часы' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Таблица -->
      <div class="lg:col-span-2 space-y-4">
        <div class="card p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">
              Записи
            </h2>
            <select
              v-model="hoursFilter"
              class="form-input text-sm py-1"
              @change="loadHours"
            >
              <option value="">
                Все волонтёры
              </option>
              <option
                v-for="v in volunteers"
                :key="v.id"
                :value="v.id"
              >
                {{ v.name }}
              </option>
            </select>
          </div>
          <div
            v-if="hoursTableLoading"
            class="text-center py-8"
          >
            <div class="loading-spinner w-8 h-8 mx-auto" />
          </div>
          <table
            v-else
            class="w-full text-sm"
          >
            <thead>
              <tr class="border-b text-left text-gray-500">
                <th class="pb-3 pr-4">
                  Волонтёр
                </th>
                <th class="pb-3 pr-4">
                  Часы
                </th>
                <th class="pb-3 pr-4">
                  Дата
                </th>
                <th class="pb-3 pr-4">
                  Описание
                </th>
                <th class="pb-3" />
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="r in hoursRecords"
                :key="r.id"
                class="border-b border-gray-100 last:border-0"
              >
                <td class="py-3 pr-4 font-medium">
                  {{ r.volunteer_name }}
                </td>
                <td class="py-3 pr-4">
                  <span class="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-semibold text-emerald-700">
                    +{{ r.hours }}ч
                  </span>
                </td>
                <td class="py-3 pr-4 text-gray-500">
                  {{ formatDate(r.date) }}
                </td>
                <td class="py-3 pr-4 text-gray-500 max-w-xs truncate">
                  {{ r.description || '—' }}
                </td>
                <td class="py-3">
                  <button
                    class="text-red-400 hover:text-red-600 text-xs"
                    @click="deleteHours(r.id)"
                  >
                    Удалить
                  </button>
                </td>
              </tr>
              <tr v-if="hoursRecords.length === 0">
                <td
                  colspan="5"
                  class="py-6 text-center text-gray-500"
                >
                  Записей нет
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Итого -->
        <div class="card p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-3">
            Итого по волонтёрам
          </h2>
          <ul class="divide-y divide-gray-100">
            <li
              v-for="v in volunteers"
              :key="v.id"
              class="flex items-center justify-between py-2"
            >
              <span class="text-gray-800">{{ v.name }}</span>
              <span class="font-semibold text-primary-600">{{ v.volunteer_hours }} ч</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- ТАБ: Сертификаты -->
    <div
      v-if="activeTab === 'certificates' && profile?.can_manage_certificates"
      class="grid grid-cols-1 lg:grid-cols-3 gap-8"
    >
      <!-- Форма -->
      <div class="lg:col-span-1">
        <div class="card p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">
            Добавить сертификат
          </h2>
          <form
            class="space-y-4"
            @submit.prevent="submitCertificate"
          >
            <div>
              <label class="form-label">Волонтёр</label>
              <select
                v-model="certForm.volunteer"
                class="form-input"
                required
              >
                <option
                  value=""
                  disabled
                >
                  Выберите волонтёра
                </option>
                <option
                  v-for="v in volunteers"
                  :key="v.id"
                  :value="v.id"
                >
                  {{ v.name }} ({{ v.username }})
                </option>
              </select>
            </div>
            <div>
              <label class="form-label">Название</label>
              <input
                v-model="certForm.title"
                type="text"
                class="form-input"
                required
              >
            </div>
            <div>
              <label class="form-label">Кем выдан</label>
              <input
                v-model="certForm.issued_by"
                type="text"
                class="form-input"
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
              <label class="form-label">Описание</label>
              <textarea
                v-model="certForm.description"
                rows="2"
                class="form-input"
              />
            </div>
            <div>
              <label class="form-label">Файл (PDF / JPG / PNG)</label>
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                class="form-input"
                @change="onCertFile"
              >
            </div>
            <p
              v-if="certError"
              class="text-sm text-red-600"
            >
              {{ certError }}
            </p>
            <p
              v-if="certSuccess"
              class="text-sm text-green-600"
            >
              {{ certSuccess }}
            </p>
            <button
              type="submit"
              class="btn btn-primary w-full"
              :disabled="certLoading"
            >
              {{ certLoading ? 'Загрузка...' : 'Добавить сертификат' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Список -->
      <div class="lg:col-span-2">
        <div class="card p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">
              Сертификаты волонтёров
            </h2>
            <select
              v-model="certFilter"
              class="form-input text-sm py-1"
              @change="loadCertificates"
            >
              <option value="">
                Все волонтёры
              </option>
              <option
                v-for="v in volunteers"
                :key="v.id"
                :value="v.id"
              >
                {{ v.name }}
              </option>
            </select>
          </div>
          <div
            v-if="certsLoading"
            class="text-center py-8"
          >
            <div class="loading-spinner w-8 h-8 mx-auto" />
          </div>
          <ul
            v-else
            class="divide-y divide-gray-100"
          >
            <li
              v-for="c in certificates"
              :key="c.id"
              class="flex items-start justify-between py-3"
            >
              <div>
                <p class="font-medium text-gray-900">
                  {{ c.title }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ c.volunteer_name }} · {{ c.issued_by || '—' }} · {{ c.issued_at || '—' }}
                </p>
              </div>
              <a
                :href="c.file"
                target="_blank"
                class="text-primary-600 text-xs hover:underline ml-4 flex-shrink-0"
              >
                Скачать
              </a>
            </li>
            <li
              v-if="certificates.length === 0"
              class="py-6 text-center text-gray-500 text-sm"
            >
              Сертификатов нет
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Нет разрешений -->
    <div
      v-if="!profile?.can_view_volunteers && !profile?.can_manage_hours && !profile?.can_manage_certificates"
      class="card p-12 text-center text-gray-500"
    >
      У вашего аккаунта нет активных разрешений. Обратитесь к администратору.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import apiService from '@/services/api'

// Profile & permissions
const profile = ref<{
  department: string
  can_view_volunteers: boolean
  can_manage_hours: boolean
  can_manage_certificates: boolean
} | null>(null)

// Volunteers list (shared across tabs)
const volunteers = ref<{ id: number; username: string; name: string; email: string; city: string; volunteer_hours: number }[]>([])
const volunteersLoading = ref(false)
const volunteerSearch = ref('')
const filteredVolunteers = computed(() =>
  volunteers.value.filter(v => {
    const q = volunteerSearch.value.toLowerCase()
    return !q || v.name.toLowerCase().includes(q) || v.username.toLowerCase().includes(q) || v.email.toLowerCase().includes(q)
  })
)

// Tab state — default to first available tab after load
const activeTab = ref<'volunteers' | 'hours' | 'certificates'>('hours')

// Hours tab
const hoursRecords = ref<any[]>([])
const hoursTableLoading = ref(false)
const hoursFilter = ref<number | ''>('')
const hoursForm = ref({ volunteer: '' as number | '', hours: 1, date: today(), description: '' })
const hoursLoading = ref(false)
const hoursError = ref('')
const hoursSuccess = ref('')

// Certificates tab
const certificates = ref<any[]>([])
const certsLoading = ref(false)
const certFilter = ref<number | ''>('')
const certForm = ref({ volunteer: '' as number | '', title: '', issued_by: '', issued_at: '', description: '' })
const certFile = ref<File | null>(null)
const certLoading = ref(false)
const certError = ref('')
const certSuccess = ref('')

function today() {
  return new Date().toISOString().slice(0, 10)
}

onMounted(async () => {
  await loadProfile()
  await loadVolunteers()
  if (profile.value?.can_view_volunteers) activeTab.value = 'volunteers'
  else if (profile.value?.can_manage_hours) activeTab.value = 'hours'
  else if (profile.value?.can_manage_certificates) activeTab.value = 'certificates'

  await Promise.all([
    profile.value?.can_manage_hours ? loadHours() : Promise.resolve(),
    profile.value?.can_manage_certificates ? loadCertificates() : Promise.resolve(),
  ])
})

async function loadProfile() {
  try {
    const data = await apiService.getModeratorProfile()
    profile.value = data
  } catch {
    // Профиль не создан — показываем все табы по умолчанию
    profile.value = { department: '', can_view_volunteers: true, can_manage_hours: true, can_manage_certificates: true }
  }
}

async function loadVolunteers() {
  try {
    volunteersLoading.value = true
    volunteers.value = await apiService.getVolunteerList()
  } catch {
    // ignore
  } finally {
    volunteersLoading.value = false
  }
}

async function loadHours() {
  try {
    hoursTableLoading.value = true
    hoursRecords.value = await apiService.getVolunteerHours(
      hoursFilter.value ? { volunteer_id: hoursFilter.value as number } : undefined
    )
  } finally {
    hoursTableLoading.value = false
  }
}

async function submitHours() {
  hoursError.value = ''
  hoursSuccess.value = ''
  if (!hoursForm.value.volunteer) { hoursError.value = 'Выберите волонтёра'; return }
  try {
    hoursLoading.value = true
    await apiService.createVolunteerHours({
      volunteer: hoursForm.value.volunteer as number,
      hours: hoursForm.value.hours,
      description: hoursForm.value.description,
      date: hoursForm.value.date,
    })
    hoursSuccess.value = 'Часы добавлены'
    hoursForm.value = { volunteer: '', hours: 1, date: today(), description: '' }
    await Promise.all([loadHours(), loadVolunteers()])
  } catch (e: any) {
    hoursError.value = e?.response?.data?.detail || 'Ошибка сохранения'
  } finally {
    hoursLoading.value = false
  }
}

async function deleteHours(id: number) {
  if (!confirm('Удалить запись?')) return
  await apiService.deleteVolunteerHours(id)
  await Promise.all([loadHours(), loadVolunteers()])
}

async function loadCertificates() {
  try {
    certsLoading.value = true
    certificates.value = await apiService.getCertificatesForModerator(
      certFilter.value ? { volunteer_id: certFilter.value as number } : undefined
    )
  } finally {
    certsLoading.value = false
  }
}

function onCertFile(e: Event) {
  const input = e.target as HTMLInputElement
  certFile.value = input.files?.[0] ?? null
}

async function submitCertificate() {
  certError.value = ''
  certSuccess.value = ''
  if (!certForm.value.volunteer) { certError.value = 'Выберите волонтёра'; return }
  if (!certFile.value) { certError.value = 'Прикрепите файл'; return }
  try {
    certLoading.value = true
    const fd = new FormData()
    fd.append('volunteer', String(certForm.value.volunteer))
    fd.append('title', certForm.value.title)
    fd.append('file', certFile.value)
    if (certForm.value.issued_by) fd.append('issued_by', certForm.value.issued_by)
    if (certForm.value.issued_at) fd.append('issued_at', certForm.value.issued_at)
    if (certForm.value.description) fd.append('description', certForm.value.description)
    await apiService.uploadCertificate(fd)
    certSuccess.value = 'Сертификат добавлен'
    certForm.value = { volunteer: '', title: '', issued_by: '', issued_at: '', description: '' }
    certFile.value = null
    await loadCertificates()
  } catch (e: any) {
    certError.value = e?.response?.data?.detail || JSON.stringify(e?.response?.data) || 'Ошибка загрузки'
  } finally {
    certLoading.value = false
  }
}

function formatDate(d: string) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}
</script>
