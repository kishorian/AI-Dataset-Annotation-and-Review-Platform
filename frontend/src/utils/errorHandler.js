/**
 * Error handling utilities
 */

/**
 * Extract error message from API error response
 * 
 * @param {Error} error - Axios error object
 * @returns {string} User-friendly error message
 */
export const getErrorMessage = (error) => {
  // Network error (no response)
  if (!error.response) {
    if (error.request) {
      return 'Network error. Please check your connection and try again.'
    }
    return 'An unexpected error occurred. Please try again.'
  }

  // API error response
  const { status, data } = error.response

  // Extract detail from response
  if (data?.detail) {
    return typeof data.detail === 'string' 
      ? data.detail 
      : JSON.stringify(data.detail)
  }

  // Status code based messages
  const statusMessages = {
    400: 'Invalid request. Please check your input.',
    401: 'Authentication required. Please login.',
    403: 'You do not have permission to perform this action.',
    404: 'Resource not found.',
    409: 'Conflict. This resource already exists.',
    422: 'Validation error. Please check your input.',
    500: 'Server error. Please try again later.',
    503: 'Service unavailable. Please try again later.',
  }

  return statusMessages[status] || `Error ${status}: ${data?.message || 'An error occurred'}`
}

/**
 * Check if error is a network error
 * 
 * @param {Error} error - Error object
 * @returns {boolean} True if network error
 */
export const isNetworkError = (error) => {
  return !error.response && error.request
}

/**
 * Check if error is an authentication error
 * 
 * @param {Error} error - Error object
 * @returns {boolean} True if authentication error
 */
export const isAuthError = (error) => {
  return error.response?.status === 401 || error.response?.status === 403
}

/**
 * Check if error is a validation error
 * 
 * @param {Error} error - Error object
 * @returns {boolean} True if validation error
 */
export const isValidationError = (error) => {
  return error.response?.status === 400 || error.response?.status === 422
}

/**
 * Extract validation errors from response
 * 
 * @param {Error} error - Axios error object
 * @returns {object} Validation errors object
 */
export const getValidationErrors = (error) => {
  if (isValidationError(error) && error.response?.data?.detail) {
    const detail = error.response.data.detail
    
    // Handle array of validation errors
    if (Array.isArray(detail)) {
      const errors = {}
      detail.forEach((err) => {
        if (err.loc && err.msg) {
          const field = err.loc[err.loc.length - 1]
          errors[field] = err.msg
        }
      })
      return errors
    }
    
    // Handle object of validation errors
    if (typeof detail === 'object') {
      return detail
    }
  }
  
  return {}
}
