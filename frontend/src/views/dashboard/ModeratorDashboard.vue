<template>
  <div class="container-custom py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">
        Панель модератора
      </h1>
      <p class="mt-1 text-gray-500">
        Учёт волонтёрских часов
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Форма добавления часов -->
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
                v-model="form.volunteer"
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
                v-model.number="form.hours"
                type="number"
                min="1"
                class="form-input"
                placeholder="1"
                required
              >
            </div>

            <div>
              <label class="form-label">Дата активности</label>
              <input
                v-model="form.date"
                type="date"
                class="form-input"
                required
              >
            </div>

            <div>
              <label class="form-label">Описание деятельности</label>
              <textarea
                v-model="form.description"
                rows="3"
                class="form-input"
                placeholder="Краткое описание выполненной работы..."
              />
            </div>

            <p
              v-if="formError"
              class="text-sm text-red-600"
            >
              {{ formError }}
            </p>
            <p
              v-if="formSuccess"
              class="text-sm text-green-600"
            >
              {{ formSuccess }}
            </p>

            <button
              type="submit"
              class="btn btn-primary w-full"
              :disabled="formLoading"
            >
              {{ formLoading ? 'Сохранение...' : 'Добавить часы' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Таблица записей -->
      <div class="lg:col-span-2">
        <div class="card p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">
              Записи часов
            </h2>
            <div class="flex items-center gap-2">
              <select
                v-model="filterVolunteer"
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
          </div>

          <div
            v-if="hoursLoading"
            class="text-center py-8"
          >
            <div class="loading-spinner w-8 h-8 mx-auto mb-2" />
            <p class="text-gray-500 text-sm">
              Загрузка...
            </p>
          </div>

          <div
            v-else-if="hours.length === 0"
            class="text-center py-8 text-gray-500"
          >
            Записей пока нет
          </div>

          <div
            v-else
            class="overflow-x-auto"
          >
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-gray-200 text-left text-gray-500">
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
                  v-for="record in hours"
                  :key="record.id"
                  class="border-b border-gray-100 last:border-0"
                >
                  <td class="py-3 pr-4 font-medium text-gray-900">
                    {{ record.volunteer_name }}
                  </td>
                  <td class="py-3 pr-4">
                    <span class="inline-flex items-center rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-semibold text-emerald-700">
                      +{{ record.hours }}ч
                    </span>
                  </td>
                  <td class="py-3 pr-4 text-gray-500">
                    {{ formatDate(record.date) }}
                  </td>
                  <td class="py-3 pr-4 text-gray-500 max-w-xs truncate">
                    {{ record.description || '—' }}
                  </td>
                  <td class="py-3">
                    <button
                      class="text-red-400 hover:text-red-600 text-xs"
                      @click="deleteRecord(record.id)"
                    >
                      Удалить
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Итого по волонтёрам -->
        <div class="card p-6 mt-4">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">
            Итого часов по волонтёрам
          </h2>
          <div
            v-if="volunteers.length === 0"
            class="text-center py-4 text-gray-500 text-sm"
          >
            Нет данных
          </div>
          <ul
            v-else
            class="divide-y divide-gray-100"
          >
            <li
              v-for="v in volunteers"
              :key="v.id"
              class="flex items-center justify-between py-3"
            >
              <span class="text-gray-800 font-medium">{{ v.name }}</span>
              <span class="text-primary-600 font-semibold">{{ v.volunteer_hours }} ч</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiService from '@/services/api'

const volunteers = ref<{ id: number; username: string; name: string; volunteer_hours: number }[]>([])
const hours = ref<any[]>([])
const hoursLoading = ref(false)
const filterVolunteer = ref<number | ''>('')

const form = ref({
  volunteer: '' as number | '',
  hours: 1,
  date: new Date().toISOString().slice(0, 10),
  description: '',
})
const formLoading = ref(false)
const formError = ref('')
const formSuccess = ref('')

onMounted(async () => {
  await Promise.all([loadVolunteers(), loadHours()])
})

const loadVolunteers = async () => {
  try {
    volunteers.value = await apiService.getVolunteerList()
  } catch {
    // ignore
  }
}

const loadHours = async () => {
  try {
    hoursLoading.value = true
    hours.value = await apiService.getVolunteerHours(
      filterVolunteer.value ? { volunteer_id: filterVolunteer.value as number } : undefined
    )
  } catch {
    // ignore
  } finally {
    hoursLoading.value = false
  }
}

const submitHours = async () => {
  formError.value = ''
  formSuccess.value = ''
  if (!form.value.volunteer) {
    formError.value = 'Выберите волонтёра'
    return
  }
  try {
    formLoading.value = true
    await apiService.createVolunteerHours({
      volunteer: form.value.volunteer as number,
      hours: form.value.hours,
      description: form.value.description,
      date: form.value.date,
    })
    formSuccess.value = 'Часы успешно добавлены'
    form.value = {
      volunteer: '',
      hours: 1,
      date: new Date().toISOString().slice(0, 10),
      description: '',
    }
    await Promise.all([loadHours(), loadVolunteers()])
  } catch (e: any) {
    formError.value = e?.response?.data?.detail || 'Ошибка при сохранении'
  } finally {
    formLoading.value = false
  }
}

const deleteRecord = async (id: number) => {
  if (!confirm('Удалить запись?')) return
  try {
    await apiService.deleteVolunteerHours(id)
    await Promise.all([loadHours(), loadVolunteers()])
  } catch {
    // ignore
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}
</script>
