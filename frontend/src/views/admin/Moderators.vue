<template>
  <div class="min-h-screen bg-gray-50 py-6">
    <div class="container-custom max-w-5xl">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Управление модераторами</h1>
          <p class="text-gray-600 mt-1">Добавляйте новых модераторов и управляйте их правами</p>
        </div>
        <button class="btn btn-primary" @click="showForm = !showForm">
          {{ showForm ? 'Скрыть форму' : '+ Добавить модератора' }}
        </button>
      </div>

      <div v-if="message" class="mb-4 p-3 bg-green-50 border border-green-200 rounded text-sm text-green-700">
        {{ message }}
      </div>
      <div v-if="errorMsg" class="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
        {{ errorMsg }}
      </div>

      <!-- Create form -->
      <div v-if="showForm" class="bg-white p-6 rounded-lg shadow mb-6">
        <h2 class="text-lg font-semibold mb-4">Новый модератор</h2>
        <form class="grid grid-cols-1 md:grid-cols-2 gap-4" @submit.prevent="submit">
          <div>
            <label class="form-label">Username *</label>
            <input v-model="form.username" type="text" class="form-input w-full" required />
          </div>
          <div>
            <label class="form-label">Email *</label>
            <input v-model="form.email" type="email" class="form-input w-full" required />
          </div>
          <div>
            <label class="form-label">Пароль * (мин. 8 символов)</label>
            <input v-model="form.password" type="password" class="form-input w-full" minlength="8" required />
          </div>
          <div>
            <label class="form-label">Отдел / направление</label>
            <input v-model="form.department" type="text" class="form-input w-full" placeholder="Например: IT, SMM, Ивенты" />
          </div>
          <div class="md:col-span-2 grid grid-cols-1 md:grid-cols-3 gap-3 bg-gray-50 p-3 rounded">
            <label class="flex items-center gap-2">
              <input v-model="form.can_view_volunteers" type="checkbox" class="h-4 w-4" />
              <span class="text-sm">Просмотр волонтёров</span>
            </label>
            <label class="flex items-center gap-2">
              <input v-model="form.can_manage_hours" type="checkbox" class="h-4 w-4" />
              <span class="text-sm">Учёт часов</span>
            </label>
            <label class="flex items-center gap-2">
              <input v-model="form.can_manage_certificates" type="checkbox" class="h-4 w-4" />
              <span class="text-sm">Выдача сертификатов</span>
            </label>
          </div>
          <div class="md:col-span-2 flex gap-3 justify-end">
            <button type="button" class="btn btn-outline" @click="showForm = false">Отмена</button>
            <button type="submit" :disabled="submitting" class="btn btn-primary">
              {{ submitting ? 'Создание...' : 'Создать' }}
            </button>
          </div>
        </form>
      </div>

      <!-- List -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div v-if="loading" class="p-12 text-center text-gray-500">Загрузка...</div>
        <div v-else-if="moderators.length === 0" class="p-12 text-center text-gray-500">
          Модераторов пока нет.
        </div>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 text-left text-xs uppercase text-gray-600">
            <tr>
              <th class="p-3">Username</th>
              <th class="p-3">Email</th>
              <th class="p-3">Отдел</th>
              <th class="p-3">Разрешения</th>
              <th class="p-3">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in moderators" :key="m.id" class="border-b hover:bg-gray-50">
              <td class="p-3 font-medium">{{ m.username }}</td>
              <td class="p-3">{{ m.email }}</td>
              <td class="p-3">{{ m.department || '—' }}</td>
              <td class="p-3 space-x-1">
                <span v-if="m.can_view_volunteers" class="badge badge-primary text-xs">Волонтёры</span>
                <span v-if="m.can_manage_hours" class="badge badge-primary text-xs">Часы</span>
                <span v-if="m.can_manage_certificates" class="badge badge-primary text-xs">Сертификаты</span>
              </td>
              <td class="p-3">
                <button
                  class="btn btn-sm bg-red-500 text-white hover:bg-red-600"
                  :disabled="removingId === m.id"
                  @click="remove(m)"
                >
                  {{ removingId === m.id ? '...' : 'Удалить' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import apiService from '@/services/api'

interface Moderator {
  id: number
  username: string
  email: string
  department: string
  can_view_volunteers: boolean
  can_manage_hours: boolean
  can_manage_certificates: boolean
}

const moderators = ref<Moderator[]>([])
const loading = ref(true)
const submitting = ref(false)
const removingId = ref<number | null>(null)
const showForm = ref(false)
const message = ref('')
const errorMsg = ref('')

const form = reactive({
  username: '',
  email: '',
  password: '',
  department: '',
  can_view_volunteers: true,
  can_manage_hours: true,
  can_manage_certificates: true,
})

onMounted(load)

async function load() {
  loading.value = true
  errorMsg.value = ''
  try {
    moderators.value = await apiService.listModerators()
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.error || 'Не удалось загрузить список'
  } finally {
    loading.value = false
  }
}

function flash(text: string) {
  message.value = text
  setTimeout(() => (message.value = ''), 3000)
}

function reset() {
  form.username = ''
  form.email = ''
  form.password = ''
  form.department = ''
  form.can_view_volunteers = true
  form.can_manage_hours = true
  form.can_manage_certificates = true
}

async function submit() {
  submitting.value = true
  errorMsg.value = ''
  try {
    await apiService.createModerator({
      username: form.username.trim(),
      email: form.email.trim(),
      password: form.password,
      department: form.department.trim(),
      can_view_volunteers: form.can_view_volunteers,
      can_manage_hours: form.can_manage_hours,
      can_manage_certificates: form.can_manage_certificates,
    })
    flash('Модератор создан')
    reset()
    showForm.value = false
    await load()
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.error || 'Ошибка создания'
  } finally {
    submitting.value = false
  }
}

async function remove(m: Moderator) {
  if (!confirm(`Удалить модератора ${m.username}? Роль будет понижена до волонтёра.`)) return
  removingId.value = m.id
  errorMsg.value = ''
  try {
    await apiService.removeModerator(m.id)
    flash('Модератор удалён')
    await load()
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.error || 'Ошибка'
  } finally {
    removingId.value = null
  }
}
</script>
