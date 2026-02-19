/**
 * Review Service
 * Handles all review-related API calls
 */

import apiService from './apiService'

class ReviewService {
  /**
   * Get all reviews
   * @param {object} params - Query parameters (annotation_id, reviewer_id, decision, skip, limit)
   * @returns {Promise} API response
   */
  async getReviews(params = {}) {
    const queryParams = new URLSearchParams()
    if (params.annotation_id) queryParams.append('annotation_id', params.annotation_id)
    if (params.reviewer_id) queryParams.append('reviewer_id', params.reviewer_id)
    if (params.decision) queryParams.append('decision', params.decision)
    if (params.skip) queryParams.append('skip', params.skip)
    if (params.limit) queryParams.append('limit', params.limit)

    const queryString = queryParams.toString()
    const endpoint = queryString ? `/reviews/?${queryString}` : '/reviews/'
    
    return await apiService.get(endpoint)
  }

  /**
   * Get review by ID
   * @param {string} reviewId - Review UUID
   * @returns {Promise} API response
   */
  async getReview(reviewId) {
    return await apiService.get(`/reviews/${reviewId}`)
  }

  /**
   * Approve annotation
   * @param {string} annotationId - Annotation UUID
   * @param {string} feedback - Optional feedback
   * @returns {Promise} API response
   */
  async approveAnnotation(annotationId, feedback = null) {
    return await apiService.post('/reviews/approve', {
      annotation_id: annotationId,
      feedback,
    })
  }

  /**
   * Reject annotation
   * @param {string} annotationId - Annotation UUID
   * @param {string} feedback - Required feedback
   * @returns {Promise} API response
   */
  async rejectAnnotation(annotationId, feedback) {
    return await apiService.post('/reviews/reject', {
      annotation_id: annotationId,
      feedback,
    })
  }

  /**
   * Create review
   * @param {object} reviewData - Review data (annotation_id, decision, feedback)
   * @returns {Promise} API response
   */
  async createReview(reviewData) {
    return await apiService.post('/reviews/', reviewData)
  }
}

export default new ReviewService()
