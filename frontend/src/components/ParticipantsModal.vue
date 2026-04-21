<template>
  <div
    v-if="open"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-lg w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="px-6 py-4 border-b flex justify-between items-center">
        <div>
          <h2 class="text-xl font-semibold">
            Участники проекта
          </h2>
          <p class="text-sm text-gray-500">
            {{ projectTitle }}
          </p>
        </div>
        <button
          class="text-gray-500 hover:text-gray-900"
          @click="$emit('close')"
        >
          <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <!-- Messages -->
      <div
        v-if="message"
        class="mx-6 mt-4 p-3 bg-green-50 border border-green-200 rounded text-sm text-green-700"
      >
        {{ message }}
      </div>
      <div
        v-if="errorMsg"
        class="mx-6 mt-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700"
      >
        {{ errorMsg }}
      </div>

      <!-- Table -->
      <div class="flex-1 overflow-auto p-6">
        <div
          v-if="loading"
          class="text-center py-12 text-gray-500"
        >
          Загрузка...
        </div>
        <div
          v-else-if="participants.length === 0"
          class="text-center py-12 text-gray-500"
        >
          Нет утверждённых волонтёров.
        </div>
        <table
          v-else
          class="w-full text-sm"
        >
          <thead class="bg-gray-50 text-left text-xs uppercase text-gray-600">
            <tr>
              <th class="p-3">
                Волонтёр
              </th>
              <th class="p-3">
                Обещано
              </th>
              <th class="p-3">
                Всего часов
              </th>
              <th class="p-3">
                Сертификат
              </th>
              <th class="p-3">
                Действия
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="p in participants"
              :key="p.volunteer_id"
              :class="['border-b', p.is_banned ? 'bg-red-50' : '']"
            >
              <td class="p-3">
                <div :class="p.is_banned ? 'text-red-700 font-semibold' : ''">
                  {{ p.name }}
                  <span
                    v-if="p.is_banned"
                    class="ml-1 badge bg-red-500 text-white text-xs"
                  >ЧС</span>
                </div>
                <div class="text-xs text-gray-500">
                  {{ p.email }}
                </div>
              </td>
              <td class="p-3">
                {{ p.hours_committed }} ч
              </td>
              <td class="p-3 font-medium">
                {{ p.total_hours }} ч
              </td>
              <td class="p-3">
                <span
                  v-if="p.has_certificate"
                  class="badge badge-success text-xs"
                >Есть</span>
                <span
                  v-else
                  class="text-xs text-gray-400"
                >—</span>
              </td>
              <td class="p-3">
                <div class="flex gap-2 flex-wrap">
                  <button
                    class="btn btn-outline btn-sm"
                    @click="openHoursForm(p)"
                  >
                    Часы
                  </button>
                  <button
                    class="btn btn-outline btn-sm"
                    @click="openCertForm(p)"
                  >
                    Сертификат
                  </button>
                  <button
                    v-if="!p.is_banned"
                    class="btn btn-sm bg-red-500 text-white hover:bg-red-600"
                    @click="openBanForm(p)"
                  >
                    В ЧС
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Hours sub-form -->
      <div
        v-if="hoursTarget"
        class="px-6 py-4 border-t bg-gray-50"
      >
        <h3 class="font-semibold mb-2">
          Добавить часы: {{ hoursTarget.name }}
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input
            v-model.number="hoursForm.hours"
            type="number"
            min="1"
            placeholder="Часы"
            class="form-input"
          >
          <input
            v-model="hoursForm.date"
            type="date"
            class="form-input"
          >
          <input
            v-model="hoursForm.description"
            type="text"
            placeholder="Описание (необязательно)"
            class="form-input"
          >
        </div>
        <div class="flex gap-2 mt-3">
          <button
            class="btn btn-primary btn-sm"
            :disabled="submitting"
            @click="submitHours"
          >
            {{ submitting ? '...' : 'Сохранить' }}
          </button>
          <button
            class="btn btn-outline btn-sm"
            @click="hoursTarget = null"
          >
            Отмена
          </button>
        </div>
      </div>

      <!-- Cert sub-form -->
      <div
        v-if="certTarget"
        class="px-6 py-4 border-t bg-gray-50"
      >
        <h3 class="font-semibold mb-2">
          Добавить сертификат: {{ certTarget.name }}
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <input
            v-model="certForm.title"
            type="text"
            placeholder="Название *"
            class="form-input"
          >
          <input
            v-model="certForm.issued_by"
            type="text"
            placeholder="Кем выдан"
            class="form-input"
          >
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            class="form-input"
            @change="onCertFile"
          >
        </div>
        <div class="flex gap-2 mt-3">
          <button
            class="btn btn-primary btn-sm"
            :disabled="submitting"
            @click="submitCert"
          >
            {{ submitting ? '...' : 'Сохранить' }}
          </button>
          <button
            class="btn btn-outline btn-sm"
            @click="certTarget = null"
          >
            Отмена
          </button>
        </div>
      </div>

      <!-- Ban sub-form -->
      <div
        v-if="banTarget"
        class="px-6 py-4 border-t bg-red-50"
      >
        <h3 class="font-semibold mb-2 text-red-700">
          Добавить в ЧС: {{ banTarget.name }}
        </h3>
        <textarea
          v-model="banForm.reason"
          rows="2"
          placeholder="Причина (обязательно) *"
          class="form-input w-full"
        />
        <div class="mt-2">
          <label class="text-sm text-gray-600">Заблокировать до (необязательно):</label>
          <input
            v-model="banForm.banned_until"
            type="datetime-local"
            class="form-input"
          >
        </div>
        <div class="flex gap-2 mt-3">
          <button
            class="btn bg-red-500 text-white hover:bg-red-600 btn-sm"
            :disabled="submitting || !banForm.reason.trim()"
            @click="submitBan"
          >
            {{ submitting ? '...' : 'Заблокировать' }}
          </button>
          <button
            class="btn btn-outline btn-sm"
            @click="banTarget = null"
          >
            Отмена
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import apiService from '@/services/api'
import type { ProjectParticipant } from '@/types/api'

const props = defineProps<{
  open: boolean
  projectId: number
  projectTitle: string
}>()
 
defineEmits(['close'])

const participants = ref<ProjectParticipant[]>([])
const loading = ref(false)
const submitting = ref(false)
const message = ref('')
const errorMsg = ref('')

const hoursTarget = ref<ProjectParticipant | null>(null)
const certTarget = ref<ProjectParticipant | null>(null)
const banTarget = ref<ProjectParticipant | null>(null)

const today = new Date().toISOString().slice(0, 10)
const hoursForm = reactive({ hours: 1, date: today, description: '' })
const certForm = reactive({ title: '', issued_by: '', file: null as File | null })
const banForm = reactive({ reason: '', banned_until: '' })

watch(() => props.open, async (v) => {
  if (v) await load()
})

async function load() {
  loading.value = true
  errorMsg.value = ''
  try {
    participants.value = await apiService.getProjectParticipants(props.projectId)
  } catch {
    errorMsg.value = 'Не удалось загрузить участников'
  } finally {
    loading.value = false
  }
}

function flash(text: string) {
  message.value = text
  setTimeout(() => (message.value = ''), 3000)
}

function openHoursForm(p: ProjectParticipant) {
  hoursTarget.value = p
  certTarget.value = null
  banTarget.value = null
  hoursForm.hours = 1
  hoursForm.date = today
  hoursForm.description = ''
}

function openCertForm(p: ProjectParticipant) {
  certTarget.value = p
  hoursTarget.value = null
  banTarget.value = null
  certForm.title = ''
  certForm.issued_by = ''
  certForm.file = null
}

function openBanForm(p: ProjectParticipant) {
  banTarget.value = p
  hoursTarget.value = null
  certTarget.value = null
  banForm.reason = ''
  banForm.banned_until = ''
}

function onCertFile(e: Event) {
  certForm.file = (e.target as HTMLInputElement).files?.[0] ?? null
}

async function submitHours() {
  if (!hoursTarget.value || hoursForm.hours < 1) return
  submitting.value = true
  errorMsg.value = ''
  try {
    await apiService.createVolunteerHours({
      volunteer: hoursTarget.value.volunteer_id,
      hours: hoursForm.hours,
      date: hoursForm.date,
      description: hoursForm.description,
    })
    flash('Часы добавлены')
    hoursTarget.value = null
    await load()
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.error || 'Ошибка при добавлении часов'
  } finally {
    submitting.value = false
  }
}

async function submitCert() {
  if (!certTarget.value || !certForm.title.trim() || !certForm.file) {
    errorMsg.value = 'Заполните название и файл'
    return
  }
  submitting.value = true
  errorMsg.value = ''
  try {
    const fd = new FormData()
    fd.append('volunteer', String(certTarget.value.volunteer_id))
    fd.append('title', certForm.title.trim())
    fd.append('issued_by', certForm.issued_by)
    fd.append('project', String(props.projectId))
    fd.append('file', certForm.file)
    await apiService.uploadCertificate(fd)
    flash('Сертификат добавлен')
    certTarget.value = null
    await load()
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.error || 'Ошибка при добавлении сертификата'
  } finally {
    submitting.value = false
  }
}

async function submitBan() {
  if (!banTarget.value || !banForm.reason.trim()) {
    errorMsg.value = 'Причина обязательна'
    return
  }
  submitting.value = true
  errorMsg.value = ''
  try {
    await apiService.banVolunteer({
      volunteer: banTarget.value.volunteer_id,
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
    submitting.value = false
  }
}
</script>
