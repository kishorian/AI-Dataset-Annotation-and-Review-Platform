import axios from 'axios'
import config from '../config/env'

/**
 * Create axios instance with base configuration
 */
// Construct base URL: if apiBaseURL is empty (production), use '/api', otherwise append '/api'
const baseURL = config.apiBaseURL 
  ? `${config.apiBaseURL}/api` 
  : '/api'

const api = axios.create({
  baseURL: baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
})

/**
 * Request interceptor
 * Automatically attaches authentication token to all requests
 */
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = localStorage.getItem('token')
    
    // Attach token to Authorization header if available
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    // Handle request error
    return Promise.reject(error)
  }
)

/**
 * Response interceptor
 * Handles common response errors and token expiration
 */
api.interceptors.response.use(
  (response) => {
    // Return successful response as-is
    return response
  },
  (error) => {
    // Handle response errors
    const { response } = error
    
    // Handle 401 Unauthorized - token expired or invalid
    if (response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
      
      // Only redirect if not already on login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    
    // Return error for component-level handling
    return Promise.reject(error)
  }
)

export default api
