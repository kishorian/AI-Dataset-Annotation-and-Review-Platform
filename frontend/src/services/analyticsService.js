/**
 * Analytics Service
 * Handles all analytics-related API calls
 */

import apiService from './apiService'

class AnalyticsService {
  /**
   * Get system-wide analytics
   * @returns {Promise} API response
   */
  async getAnalytics() {
    return await apiService.get('/analytics/')
  }

  /**
   * Get project-specific analytics
   * @param {string} projectId - Project UUID
   * @returns {Promise} API response
   */
  async getProjectAnalytics(projectId) {
    return await apiService.get(`/analytics/project/${projectId}`)
  }
}

export default new AnalyticsService()
