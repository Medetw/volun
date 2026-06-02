import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginRequest, RegisterVolunteerRequest, RegisterOrganizationRequest } from '@/types/api'
import apiService from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!user.value)
  const isVolunteer = computed(() => user.value?.role === 'volunteer')
  const isOrganization = computed(() => user.value?.role === 'organization')
  const isModerator = computed(() => user.value?.role === 'moderator')
  const isAdmin = computed(() => user.value?.role === 'admin')
  const userRole = computed(() => user.value?.role || null)

  // Actions
  const login = async (credentials: LoginRequest) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiService.login(credentials)
      user.value = response.user
      
      return response
    } catch (err: any) {
      const backendMsg = err.response?.data?.non_field_errors?.[0] || err.response?.data?.detail
      if (backendMsg === 'Invalid email or password.') {
        error.value = 'Неверный email или пароль'
      } else {
        error.value = backendMsg || 'Ошибка входа'
      }
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const registerVolunteer = async (data: RegisterVolunteerRequest) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiService.registerVolunteer(data)
      user.value = response.user
      
      return response
    } catch (err: any) {
      error.value = 'Ошибка регистрации'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const registerOrganization = async (data: RegisterOrganizationRequest) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiService.registerOrganization(data)
      user.value = response.user
      
      return response
    } catch (err: any) {
      error.value = 'Ошибка регистрации'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      await apiService.logout()
    } catch (err) {
      // Игнорируем ошибки при выходе
      console.error('Logout error:', err)
    } finally {
      user.value = null
      error.value = null
    }
  }

  const fetchCurrentUser = async () => {
    try {
      isLoading.value = true
      error.value = null
      
      const currentUser = await apiService.getCurrentUser()
      user.value = currentUser
      
      return currentUser
    } catch (err: any) {
      error.value = 'Ошибка загрузки пользователя'
      user.value = null
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateProfile = async (data: Partial<User>) => {
    try {
      isLoading.value = true
      error.value = null
      
      const updatedUser = await apiService.updateProfile(data)
      user.value = updatedUser
      
      return updatedUser
    } catch (err: any) {
      error.value = 'Ошибка обновления профиля'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const requestPasswordReset = async (email: string) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiService.requestPasswordReset(email)
      
      return response
    } catch (err: any) {
      error.value = 'Ошибка запроса сброса пароля'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const confirmPasswordReset = async (data: {
    email: string
    reset_code: string
    new_password: string
    new_password_confirm: string
  }) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiService.confirmPasswordReset(data)
      
      return response
    } catch (err: any) {
      error.value = 'Ошибка сброса пароля'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const changePassword = async (data: {
    old_password: string
    new_password: string
    new_password_confirm: string
  }) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiService.changePassword(data)
      
      return response
    } catch (err: any) {
      error.value = 'Ошибка изменения пароля'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  // Инициализация при загрузке приложения
  const initializeAuth = async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        await fetchCurrentUser()
      } catch (err) {
        // Если токен невалидный, очищаем его
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        user.value = null
      }
    }
  }

  return {
    // State
    user,
    isLoading,
    error,
    
    // Getters
    isAuthenticated,
    isVolunteer,
    isOrganization,
    isModerator,
    isAdmin,
    userRole,
    
    // Actions
    login,
    registerVolunteer,
    registerOrganization,
    logout,
    fetchCurrentUser,
    updateProfile,
    requestPasswordReset,
    confirmPasswordReset,
    changePassword,
    clearError,
    initializeAuth
  }
})
