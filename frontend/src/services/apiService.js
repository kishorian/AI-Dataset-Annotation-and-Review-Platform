/**
 * API Service Layer
 * Centralized API calls with error handling
 */

import api from '../utils/api'
import { getErrorMessage, isNetworkError, isAuthError } from '../utils/errorHandler'

/**
 * Base API service class
 */
class ApiService {
  /**
   * Generic GET request
   */
  async get(endpoint, config = {}) {
    try {
      const response = await api.get(endpoint, config)
      return {
        success: true,
        data: response.data,
        status: response.status,
      }
    } catch (error) {
      return this.handleError(error)
    }
  }

  /**
   * Generic POST request
   */
  async post(endpoint, data = {}, config = {}) {
    try {
      const response = await api.post(endpoint, data, config)
      return {
        success: true,
        data: response.data,
        status: response.status,
      }
    } catch (error) {
      return this.handleError(error)
    }
  }

  /**
   * Generic PUT request
   */
  async put(endpoint, data = {}, config = {}) {
    try {
      const response = await api.put(endpoint, data, config)
      return {
        success: true,
        data: response.data,
        status: response.status,
      }
    } catch (error) {
      return this.handleError(error)
    }
  }

  /**
   * Generic DELETE request
   */
  async delete(endpoint, config = {}) {
    try {
      const response = await api.delete(endpoint, config)
      return {
        success: true,
        data: response.data,
        status: response.status,
      }
    } catch (error) {
      return this.handleError(error)
    }
  }

  /**
   * Handle API errors
   */
  handleError(error) {
    const message = getErrorMessage(error)
    
    return {
      success: false,
      error: message,
      status: error.response?.status || null,
      isNetworkError: isNetworkError(error),
      isAuthError: isAuthError(error),
      originalError: error,
    }
  }
}

// Create singleton instance
const apiService = new ApiService()

export default apiService
