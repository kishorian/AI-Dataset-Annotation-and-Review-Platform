/**
 * Project Service
 * Handles all project-related API calls
 */

import apiService from './apiService'

class ProjectService {
  /**
   * Get all projects
   * @param {object} params - Query parameters (skip, limit, created_by)
   * @returns {Promise} API response
   */
  async getProjects(params = {}) {
    const queryParams = new URLSearchParams()
    if (params.skip) queryParams.append('skip', params.skip)
    if (params.limit) queryParams.append('limit', params.limit)
    if (params.created_by) queryParams.append('created_by', params.created_by)

    const queryString = queryParams.toString()
    const endpoint = queryString ? `/projects/?${queryString}` : '/projects/'
    
    return await apiService.get(endpoint)
  }

  /**
   * Get project by ID
   * @param {string} projectId - Project UUID
   * @returns {Promise} API response
   */
  async getProject(projectId) {
    return await apiService.get(`/projects/${projectId}`)
  }

  /**
   * Create new project
   * @param {object} projectData - Project data (name, description)
   * @returns {Promise} API response
   */
  async createProject(projectData) {
    return await apiService.post('/projects/', projectData)
  }

  /**
   * Get project statistics
   * @param {string} projectId - Project UUID
   * @returns {Promise} API response
   */
  async getProjectStats(projectId) {
    return await apiService.get(`/projects/${projectId}/stats`)
  }
}

export default new ProjectService()
