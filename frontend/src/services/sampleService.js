/**
 * Data Sample Service
 * Handles all data sample-related API calls
 */

import apiService from './apiService'

class SampleService {
  /**
   * Get all samples
   * @param {object} params - Query parameters (project_id, status, skip, limit)
   * @returns {Promise} API response
   */
  async getSamples(params = {}) {
    const queryParams = new URLSearchParams()
    if (params.project_id) queryParams.append('project_id', params.project_id)
    if (params.status) queryParams.append('status', params.status)
    if (params.skip) queryParams.append('skip', params.skip)
    if (params.limit) queryParams.append('limit', params.limit)

    const queryString = queryParams.toString()
    const endpoint = queryString ? `/samples/?${queryString}` : '/samples/'
    
    return await apiService.get(endpoint)
  }

  /**
   * Get samples by status
   * @param {string} status - Sample status (pending, annotated, reviewed)
   * @param {object} params - Additional query parameters
   * @returns {Promise} API response
   */
  async getSamplesByStatus(status, params = {}) {
    const queryParams = new URLSearchParams()
    if (params.project_id) queryParams.append('project_id', params.project_id)
    if (params.skip) queryParams.append('skip', params.skip)
    if (params.limit) queryParams.append('limit', params.limit)

    const queryString = queryParams.toString()
    const endpoint = queryString 
      ? `/samples/status/${status}?${queryString}` 
      : `/samples/status/${status}`
    
    return await apiService.get(endpoint)
  }

  /**
   * Get sample by ID
   * @param {string} sampleId - Sample UUID
   * @returns {Promise} API response
   */
  async getSample(sampleId) {
    return await apiService.get(`/samples/${sampleId}`)
  }

  /**
   * Create new sample
   * @param {object} sampleData - Sample data (project_id, text_content)
   * @returns {Promise} API response
   */
  async createSample(sampleData) {
    return await apiService.post('/samples/', sampleData)
  }
}

export default new SampleService()
