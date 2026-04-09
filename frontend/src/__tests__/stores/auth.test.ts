import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

// Mock the API service
vi.mock('@/services/api', () => {
  return {
    default: {
      login: vi.fn(),
      registerVolunteer: vi.fn(),
      registerOrganization: vi.fn(),
      logout: vi.fn(),
      getCurrentUser: vi.fn(),
      updateProfile: vi.fn(),
      requestPasswordReset: vi.fn(),
      confirmPasswordReset: vi.fn(),
      changePassword: vi.fn(),
    },
  }
})

import apiService from '@/services/api'

const mockVolunteer = {
  id: 1,
  username: 'volunteer1',
  email: 'volunteer@test.com',
  role: 'volunteer' as const,
  first_name: 'Test',
  last_name: 'User',
}

const mockOrganization = {
  id: 2,
  username: 'org1',
  email: 'org@test.com',
  role: 'organization' as const,
  first_name: 'Test',
  last_name: 'Org',
}

const mockAdmin = {
  id: 3,
  username: 'admin1',
  email: 'admin@test.com',
  role: 'admin' as const,
  first_name: 'Test',
  last_name: 'Admin',
}

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('initial state', () => {
    it('should have null user initially', () => {
      const store = useAuthStore()
      expect(store.user).toBeNull()
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should not be authenticated initially', () => {
      const store = useAuthStore()
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('role getters', () => {
    it('should detect volunteer role', () => {
      const store = useAuthStore()
      store.user = mockVolunteer as any
      expect(store.isVolunteer).toBe(true)
      expect(store.isOrganization).toBe(false)
      expect(store.isAdmin).toBe(false)
      expect(store.userRole).toBe('volunteer')
    })

    it('should detect organization role', () => {
      const store = useAuthStore()
      store.user = mockOrganization as any
      expect(store.isVolunteer).toBe(false)
      expect(store.isOrganization).toBe(true)
      expect(store.isAdmin).toBe(false)
      expect(store.userRole).toBe('organization')
    })

    it('should detect admin role', () => {
      const store = useAuthStore()
      store.user = mockAdmin as any
      expect(store.isVolunteer).toBe(false)
      expect(store.isOrganization).toBe(false)
      expect(store.isAdmin).toBe(true)
      expect(store.userRole).toBe('admin')
    })

    it('should return null role when no user', () => {
      const store = useAuthStore()
      expect(store.userRole).toBeNull()
    })
  })

  describe('login', () => {
    it('should set user on successful login', async () => {
      const store = useAuthStore()
      const mockResponse = {
        user: mockVolunteer,
        tokens: { access: 'access-token', refresh: 'refresh-token' },
      }
      vi.mocked(apiService.login).mockResolvedValue(mockResponse as any)

      await store.login({ email: 'test@test.com', password: 'password' })

      expect(store.user).toEqual(mockVolunteer)
      expect(store.isAuthenticated).toBe(true)
      expect(store.error).toBeNull()
    })

    it('should set error on failed login', async () => {
      const store = useAuthStore()
      vi.mocked(apiService.login).mockRejectedValue({
        response: { data: { non_field_errors: ['Invalid credentials'] } },
      })

      await expect(
        store.login({ email: 'test@test.com', password: 'wrong' })
      ).rejects.toBeTruthy()

      expect(store.user).toBeNull()
      expect(store.error).toBe('Invalid credentials')
    })

    it('should set loading state during login', async () => {
      const store = useAuthStore()
      vi.mocked(apiService.login).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      const promise = store.login({ email: 'test@test.com', password: 'pass' })
      expect(store.isLoading).toBe(true)

      await promise.catch(() => {})
      expect(store.isLoading).toBe(false)
    })
  })

  describe('registerVolunteer', () => {
    it('should set user on successful registration', async () => {
      const store = useAuthStore()
      const mockResponse = {
        user: mockVolunteer,
        tokens: { access: 'access-token', refresh: 'refresh-token' },
      }
      vi.mocked(apiService.registerVolunteer).mockResolvedValue(mockResponse as any)

      await store.registerVolunteer({
        email: 'test@test.com',
        username: 'test',
        password: 'password',
        password_confirm: 'password',
      } as any)

      expect(store.user).toEqual(mockVolunteer)
      expect(store.isAuthenticated).toBe(true)
    })
  })

  describe('logout', () => {
    it('should clear user on logout', async () => {
      const store = useAuthStore()
      store.user = mockVolunteer as any
      vi.mocked(apiService.logout).mockResolvedValue()

      await store.logout()

      expect(store.user).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })

    it('should clear user even if API call fails', async () => {
      const store = useAuthStore()
      store.user = mockVolunteer as any
      vi.mocked(apiService.logout).mockRejectedValue(new Error('Network error'))

      await store.logout()

      expect(store.user).toBeNull()
    })
  })

  describe('fetchCurrentUser', () => {
    it('should fetch and set current user', async () => {
      const store = useAuthStore()
      vi.mocked(apiService.getCurrentUser).mockResolvedValue(mockVolunteer as any)

      await store.fetchCurrentUser()

      expect(store.user).toEqual(mockVolunteer)
    })

    it('should clear user on fetch failure', async () => {
      const store = useAuthStore()
      store.user = mockVolunteer as any
      vi.mocked(apiService.getCurrentUser).mockRejectedValue(new Error('Unauthorized'))

      await expect(store.fetchCurrentUser()).rejects.toBeTruthy()
      expect(store.user).toBeNull()
    })
  })

  describe('initializeAuth', () => {
    it('should fetch user if token exists in localStorage', async () => {
      const store = useAuthStore()
      localStorage.setItem('access_token', 'some-token')
      vi.mocked(apiService.getCurrentUser).mockResolvedValue(mockVolunteer as any)

      await store.initializeAuth()

      expect(apiService.getCurrentUser).toHaveBeenCalled()
      expect(store.user).toEqual(mockVolunteer)
    })

    it('should not fetch user if no token', async () => {
      const store = useAuthStore()

      await store.initializeAuth()

      expect(apiService.getCurrentUser).not.toHaveBeenCalled()
      expect(store.user).toBeNull()
    })

    it('should clear tokens if fetch fails', async () => {
      const store = useAuthStore()
      localStorage.setItem('access_token', 'invalid-token')
      vi.mocked(apiService.getCurrentUser).mockRejectedValue(new Error('Invalid'))

      await store.initializeAuth()

      expect(localStorage.removeItem).toHaveBeenCalledWith('access_token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('refresh_token')
      expect(store.user).toBeNull()
    })
  })

  describe('clearError', () => {
    it('should clear error state', () => {
      const store = useAuthStore()
      store.error = 'Some error' as any
      store.clearError()
      expect(store.error).toBeNull()
    })
  })
})
