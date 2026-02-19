/**
 * Authentication Service
 * Handles all authentication-related API calls
 */

import apiService from './apiService'

class AuthService {
  /**
   * Login user
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise} API response
   */
  async login(email, password) {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    return await apiService.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
  }

  /**
   * Register new user
   * @param {string} email - User email
   * @param {string} password - User password
   * @param {string} role - User role (default: 'annotator')
   * @returns {Promise} API response
   */
  async register(email, password, role = 'annotator') {
    return await apiService.post('/auth/register', {
      email,
      password,
      role,
    })
  }

  /**
   * Get current user information
   * @returns {Promise} API response
   */
  async getCurrentUser() {
    return await apiService.get('/auth/me')
  }

  /**
   * Verify token
   * @param {string} token - JWT token
   * @returns {Promise} API response
   */
  async verifyToken(token) {
    return await apiService.post('/auth/verify-token', { token })
  }
}

export default new AuthService()
