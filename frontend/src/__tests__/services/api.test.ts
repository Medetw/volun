import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'

// Mock axios
vi.mock('axios', () => {
  const mockAxiosInstance = {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
    defaults: {
      baseURL: '/api',
    },
  }

  return {
    default: {
      create: vi.fn(() => mockAxiosInstance),
      post: vi.fn(),
    },
  }
})

describe('ApiService', () => {
  let apiService: any
  let mockAxiosInstance: any

  beforeEach(async () => {
    vi.clearAllMocks()
    localStorage.clear()

    // Re-import to get a fresh instance
    vi.resetModules()
    mockAxiosInstance = {
      get: vi.fn(),
      post: vi.fn(),
      patch: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
      defaults: {
        baseURL: '/api',
      },
    }
    vi.mocked(axios.create).mockReturnValue(mockAxiosInstance as any)

    const module = await import('@/services/api')
    apiService = module.apiService
  })

  describe('constructor', () => {
    it('should create axios instance with correct config', () => {
      expect(axios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          timeout: 10000,
          headers: { 'Content-Type': 'application/json' },
        })
      )
    })

    it('should set up request and response interceptors', () => {
      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled()
      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled()
    })
  })

  describe('login', () => {
    it('should call login endpoint and store tokens', async () => {
      const mockResponse = {
        data: {
          user: { id: 1, email: 'test@test.com' },
          tokens: { access: 'access-123', refresh: 'refresh-456' },
        },
      }
      mockAxiosInstance.post.mockResolvedValue(mockResponse)

      const result = await apiService.login({
        email: 'test@test.com',
        password: 'password',
      })

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/auth/login/', {
        email: 'test@test.com',
        password: 'password',
      })
      expect(localStorage.setItem).toHaveBeenCalledWith('access_token', 'access-123')
      expect(localStorage.setItem).toHaveBeenCalledWith('refresh_token', 'refresh-456')
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('logout', () => {
    it('should call logout endpoint and clear tokens', async () => {
      localStorage.setItem('refresh_token', 'some-refresh-token')
      mockAxiosInstance.post.mockResolvedValue({})

      await apiService.logout()

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/auth/logout/', {
        refresh: 'some-refresh-token',
      })
      expect(localStorage.removeItem).toHaveBeenCalledWith('access_token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('refresh_token')
    })

    it('should clear tokens even if API call fails', async () => {
      mockAxiosInstance.post.mockRejectedValue(new Error('Network error'))

      // logout() uses try/finally, so tokens are cleared even on API failure
      await apiService.logout().catch(() => {})

      expect(localStorage.removeItem).toHaveBeenCalledWith('access_token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('refresh_token')
    })
  })

  describe('getCurrentUser', () => {
    it('should fetch current user', async () => {
      const mockUser = { id: 1, email: 'test@test.com', role: 'volunteer' }
      mockAxiosInstance.get.mockResolvedValue({ data: mockUser })

      const result = await apiService.getCurrentUser()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/auth/me/')
      expect(result).toEqual(mockUser)
    })
  })

  describe('projects', () => {
    it('should get projects list with params', async () => {
      const mockData = { results: [], count: 0 }
      mockAxiosInstance.get.mockResolvedValue({ data: mockData })

      const result = await apiService.getProjects({ status: 'active' })

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/projects/projects/', {
        params: { status: 'active' },
      })
      expect(result).toEqual(mockData)
    })

    it('should create a project', async () => {
      const projectData = { title: 'New Project' }
      const mockResponse = { data: { id: 1, ...projectData } }
      mockAxiosInstance.post.mockResolvedValue(mockResponse)

      const result = await apiService.createProject(projectData)

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/projects/projects/', projectData)
      expect(result).toEqual(mockResponse.data)
    })

    it('should delete a project', async () => {
      mockAxiosInstance.delete.mockResolvedValue({})

      await apiService.deleteProject(1)

      expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/projects/projects/1/')
    })
  })

  describe('applications', () => {
    it('should create an application', async () => {
      const appData = { project: 1, cover_letter: 'Hello', hours_committed: 10 }
      const mockResponse = { data: { id: 1, ...appData } }
      mockAxiosInstance.post.mockResolvedValue(mockResponse)

      const result = await apiService.createApplication(appData)

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/applications/applications/', appData)
      expect(result).toEqual(mockResponse.data)
    })

    it('should approve an application', async () => {
      const mockResponse = { data: { id: 1, status: 'approved' } }
      mockAxiosInstance.post.mockResolvedValue(mockResponse)

      const result = await apiService.approveApplication(1)

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/applications/applications/1/approve/')
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('notifications', () => {
    it('should mark notification as read', async () => {
      mockAxiosInstance.post.mockResolvedValue({})

      await apiService.markNotificationAsRead(5)

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/notifications/notifications/5/mark_read/')
    })

    it('should mark all notifications as read', async () => {
      mockAxiosInstance.post.mockResolvedValue({})

      await apiService.markAllNotificationsAsRead()

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/notifications/notifications/mark_all_read/')
    })

    it('should get notification stats', async () => {
      const mockStats = { total: 10, unread: 3, read: 7, today: 2 }
      mockAxiosInstance.get.mockResolvedValue({ data: mockStats })

      const result = await apiService.getNotificationStats()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/notifications/notifications/stats/')
      expect(result).toEqual(mockStats)
    })
  })
})
