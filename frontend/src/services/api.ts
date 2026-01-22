import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const API_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = useAuthStore.getState().refreshToken
        if (!refreshToken) {
          throw new Error('No refresh token')
        }

        const response = await axios.post(`${API_URL}/auth/refresh/`, {
          refresh: refreshToken,
        })

        const { access } = response.data
        useAuthStore.getState().setTokens(access, refreshToken)

        originalRequest.headers.Authorization = `Bearer ${access}`
        return api(originalRequest)
      } catch {
        useAuthStore.getState().logout()
        window.location.href = '/login'
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  }
)

export default api

// Auth API
export const authApi = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login/', { email, password })
    return response.data
  },

  register: async (email: string, username: string, password: string) => {
    const response = await api.post('/auth/register/', {
      email,
      username,
      password,
      password_confirm: password,
    })
    return response.data
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me/')
    return response.data
  },
}

// Profile API
export const profileApi = {
  getProfile: async () => {
    const response = await api.get('/profiles/me/')
    return response.data
  },

  updateProfile: async (data: Record<string, unknown>) => {
    const response = await api.put('/profiles/me/', data)
    return response.data
  },
}

// Essay API
export const essayApi = {
  list: async () => {
    const response = await api.get('/essays/')
    return response.data
  },

  get: async (id: string) => {
    const response = await api.get(`/essays/${id}/`)
    return response.data
  },

  create: async (data: {
    prompt: string
    target_university_code: string
    essay_type?: string
    word_count_target?: number
  }) => {
    const response = await api.post('/essays/', data)
    return response.data
  },

  getStatus: async (id: string) => {
    const response = await api.get(`/essays/${id}/status/`)
    return response.data
  },

  cancel: async (id: string) => {
    const response = await api.post(`/essays/${id}/cancel/`)
    return response.data
  },

  delete: async (id: string) => {
    const response = await api.delete(`/essays/${id}/`)
    return response.data
  },
}

// University API
export const universityApi = {
  list: async () => {
    const response = await api.get('/essays/universities/')
    return response.data
  },
}

// VectorDB API
export const vectordbApi = {
  search: async (query: string, nResults = 5) => {
    const response = await api.post('/vectordb/search/', {
      query,
      n_results: nResults,
    })
    return response.data
  },

  getStats: async () => {
    const response = await api.get('/vectordb/stats/')
    return response.data
  },
}
