import axios, { AxiosInstance, AxiosResponse } from 'axios'
import type { 
  User, 
  Project, 
  Application, 
  News, 
  Statistics,
  Notification,
  NotificationPreference,
  ProjectReport,
  LoginRequest,
  LoginResponse,
  RegisterVolunteerRequest,
  RegisterOrganizationRequest,
  ApiResponse,
  PaginatedResponse,
  ProjectFilters,
  ApplicationFilters
} from '@/types/api'

class ApiService {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor для добавления токена
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor для обработки ошибок и обновления токена
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            await this.refreshToken()
            const token = localStorage.getItem('access_token')
            if (token) {
              originalRequest.headers.Authorization = `Bearer ${token}`
              return this.api(originalRequest)
            }
          } catch (refreshError) {
            // Если обновление токена не удалось, разлогиниваем пользователя
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await this.api.post('/auth/login/', credentials)
    const { access, refresh } = response.data.tokens
    
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    
    return response.data
  }

  async registerVolunteer(data: RegisterVolunteerRequest): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await this.api.post('/auth/register/volunteer/', data)
    const { access, refresh } = response.data.tokens
    
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    
    return response.data
  }

  async registerOrganization(data: RegisterOrganizationRequest): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await this.api.post('/auth/register/organization/', data)
    const { access, refresh } = response.data.tokens
    
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    
    return response.data
  }

  async refreshToken(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await axios.post(
      `${this.api.defaults.baseURL}/auth/token/refresh/`,
      { refresh: refreshToken }
    )

    const { access } = response.data
    localStorage.setItem('access_token', access)
  }

  async logout(): Promise<void> {
    try {
      await this.api.post('/auth/logout/', {
        refresh: localStorage.getItem('refresh_token')
      })
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get('/auth/me/')
    return response.data
  }

  async updateProfile(data: Partial<User>): Promise<User> {
    const response: AxiosResponse<User> = await this.api.patch('/auth/me/update/', data)
    return response.data
  }

  async requestPasswordReset(email: string): Promise<{ message: string; reset_code?: string }> {
    const response = await this.api.post('/auth/password/reset/', { email })
    return response.data
  }

  async confirmPasswordReset(data: {
    email: string
    reset_code: string
    new_password: string
    new_password_confirm: string
  }): Promise<{ message: string }> {
    const response = await this.api.post('/auth/password/reset/confirm/', data)
    return response.data
  }

  async changePassword(data: {
    old_password: string
    new_password: string
    new_password_confirm: string
  }): Promise<{ message: string }> {
    const response = await this.api.post('/auth/password/change/', data)
    return response.data
  }

  // Projects endpoints
  async getProjects(params?: ProjectFilters): Promise<PaginatedResponse<Project>> {
    const response: AxiosResponse<PaginatedResponse<Project>> = await this.api.get('/projects/', { params })
    return response.data
  }

  async getProject(id: number): Promise<Project> {
    const response: AxiosResponse<Project> = await this.api.get(`/projects/${id}/`)
    return response.data
  }

  async createProject(data: Partial<Project>): Promise<Project> {
    const response: AxiosResponse<Project> = await this.api.post('/projects/', data)
    return response.data
  }

  async updateProject(id: number, data: Partial<Project>): Promise<Project> {
    const response: AxiosResponse<Project> = await this.api.patch(`/projects/${id}/`, data)
    return response.data
  }

  async deleteProject(id: number): Promise<void> {
    await this.api.delete(`/projects/${id}/`)
  }

  async getMyProjects(): Promise<PaginatedResponse<Project>> {
    const response: AxiosResponse<PaginatedResponse<Project>> = await this.api.get('/projects/my/')
    return response.data
  }

  // Categories endpoints
  async getCategories(): Promise<ApiResponse<{ id: number; name: string; description: string }>> {
    const response = await this.api.get('/projects/categories/')
    return response.data
  }

  // Regions endpoints
  async getRegions(): Promise<ApiResponse<{ id: number; name: string; code: string }>> {
    const response = await this.api.get('/projects/regions/')
    return response.data
  }

  // Applications endpoints
  async getApplications(params?: ApplicationFilters): Promise<PaginatedResponse<Application>> {
    const response: AxiosResponse<PaginatedResponse<Application>> = await this.api.get('/applications/', { params })
    return response.data
  }

  async getApplication(id: number): Promise<Application> {
    const response: AxiosResponse<Application> = await this.api.get(`/applications/${id}/`)
    return response.data
  }

  async createApplication(data: {
    project: number
    cover_letter: string
    hours_committed: number
  }): Promise<Application> {
    const response: AxiosResponse<Application> = await this.api.post('/applications/', data)
    return response.data
  }

  async approveApplication(id: number): Promise<Application> {
    const response: AxiosResponse<Application> = await this.api.post(`/applications/${id}/approve/`)
    return response.data
  }

  async rejectApplication(id: number, data: { review_comment?: string }): Promise<Application> {
    const response: AxiosResponse<Application> = await this.api.post(`/applications/${id}/reject/`, data)
    return response.data
  }

  async cancelApplication(id: number): Promise<Application> {
    const response: AxiosResponse<Application> = await this.api.post(`/applications/${id}/cancel/`)
    return response.data
  }

  // News endpoints
  async getNews(params?: { category?: string; search?: string }): Promise<PaginatedResponse<News>> {
    const response: AxiosResponse<PaginatedResponse<News>> = await this.api.get('/news/', { params })
    return response.data
  }

  async getNewsItem(slug: string): Promise<News> {
    const response: AxiosResponse<News> = await this.api.get(`/news/${slug}/`)
    return response.data
  }

  async createNews(data: Partial<News>): Promise<News> {
    const response: AxiosResponse<News> = await this.api.post('/news/', data)
    return response.data
  }

  async updateNews(id: number, data: Partial<News>): Promise<News> {
    const response: AxiosResponse<News> = await this.api.patch(`/news/${id}/`, data)
    return response.data
  }

  async deleteNews(id: number): Promise<void> {
    await this.api.delete(`/news/${id}/`)
  }

  // Statistics endpoints
  async getStatistics(): Promise<Statistics> {
    const response: AxiosResponse<Statistics> = await this.api.get('/statistics/')
    return response.data
  }

  // Notifications endpoints
  async getNotifications(params?: { is_read?: boolean }): Promise<PaginatedResponse<Notification>> {
    const response: AxiosResponse<PaginatedResponse<Notification>> = await this.api.get('/notifications/', { params })
    return response.data
  }

  async getUnreadNotifications(): Promise<Notification[]> {
    const response: AxiosResponse<Notification[]> = await this.api.get('/notifications/unread/')
    return response.data
  }

  async markNotificationAsRead(id: number): Promise<void> {
    await this.api.post(`/notifications/${id}/mark_read/`)
  }

  async markAllNotificationsAsRead(): Promise<void> {
    await this.api.post('/notifications/mark_all_read/')
  }

  async getNotificationStats(): Promise<{ total: number; unread: number; read: number; today: number }> {
    const response = await this.api.get('/notifications/stats/')
    return response.data
  }

  async deleteNotification(id: number): Promise<void> {
    await this.api.delete(`/notifications/${id}/`)
  }

  async getNotificationPreferences(): Promise<NotificationPreference> {
    const response: AxiosResponse<NotificationPreference> = await this.api.get('/notification-preferences/')
    return response.data
  }

  async updateNotificationPreferences(data: Partial<NotificationPreference>): Promise<NotificationPreference> {
    const response: AxiosResponse<NotificationPreference> = await this.api.patch('/notification-preferences/', data)
    return response.data
  }

  // Reports endpoints
  async getReports(params?: { project?: number; status?: string; type?: string; period?: string; search?: string }): Promise<PaginatedResponse<ProjectReport>> {
    const response: AxiosResponse<PaginatedResponse<ProjectReport>> = await this.api.get('/reports/', { params })
    return response.data
  }

  async getReport(id: number): Promise<ProjectReport> {
    const response: AxiosResponse<ProjectReport> = await this.api.get(`/reports/${id}/`)
    return response.data
  }

  async createReport(data: Partial<ProjectReport>): Promise<ProjectReport> {
    const response: AxiosResponse<ProjectReport> = await this.api.post('/reports/', data)
    return response.data
  }

  async updateReport(id: number, data: Partial<ProjectReport>): Promise<ProjectReport> {
    const response: AxiosResponse<ProjectReport> = await this.api.patch(`/reports/${id}/`, data)
    return response.data
  }

  async generateReport(id: number): Promise<ProjectReport> {
    const response: AxiosResponse<ProjectReport> = await this.api.post(`/reports/${id}/generate/`)
    return response.data
  }

  async downloadReport(id: number): Promise<void> {
    const response = await this.api.get(`/reports/${id}/download/`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `report-${id}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  }

  async deleteReport(id: number): Promise<void> {
    await this.api.delete(`/reports/${id}/`)
  }

  async submitReport(id: number): Promise<ProjectReport> {
    const response: AxiosResponse<ProjectReport> = await this.api.post(`/reports/${id}/submit/`)
    return response.data
  }

  async approveReport(id: number, data: { review_comment?: string }): Promise<ProjectReport> {
    const response: AxiosResponse<ProjectReport> = await this.api.post(`/reports/${id}/approve/`, data)
    return response.data
  }

  async rejectReport(id: number, data: { review_comment?: string }): Promise<ProjectReport> {
    const response: AxiosResponse<ProjectReport> = await this.api.post(`/reports/${id}/reject/`, data)
    return response.data
  }
}

export const apiService = new ApiService()
export default apiService
