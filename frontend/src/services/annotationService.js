/**
 * Annotation Service
 * Handles all annotation-related API calls
 */

import apiService from './apiService'

class AnnotationService {
  /**
   * Get all annotations
   * @param {object} params - Query parameters (sample_id, annotator_id, skip, limit)
   * @returns {Promise} API response
   */
  async getAnnotations(params = {}) {
    const queryParams = new URLSearchParams()
    if (params.sample_id) queryParams.append('sample_id', params.sample_id)
    if (params.annotator_id) queryParams.append('annotator_id', params.annotator_id)
    if (params.skip) queryParams.append('skip', params.skip)
    if (params.limit) queryParams.append('limit', params.limit)

    const queryString = queryParams.toString()
    const endpoint = queryString ? `/annotations/?${queryString}` : '/annotations/'
    
    return await apiService.get(endpoint)
  }

  /**
   * Get annotation by ID
   * @param {string} annotationId - Annotation UUID
   * @returns {Promise} API response
   */
  async getAnnotation(annotationId) {
    return await apiService.get(`/annotations/${annotationId}`)
  }

  /**
   * Submit annotation
   * @param {object} annotationData - Annotation data (sample_id, label)
   * @returns {Promise} API response
   */
  async submitAnnotation(annotationData) {
    return await apiService.post('/annotations/', annotationData)
  }
}

export default new AnnotationService()
