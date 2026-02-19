/**
 * Custom hook for API calls with loading and error states
 */

import { useState, useCallback } from 'react'

/**
 * Custom hook for handling API calls with loading and error states
 * 
 * @param {Function} apiCall - API service function to call
 * @returns {object} { data, loading, error, execute, reset }
 */
export const useApi = (apiCall) => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const execute = useCallback(
    async (...args) => {
      setLoading(true)
      setError(null)
      setData(null)

      try {
        const result = await apiCall(...args)
        
        if (result.success) {
          setData(result.data)
          return { success: true, data: result.data }
        } else {
          setError(result.error)
          return { success: false, error: result.error }
        }
      } catch (err) {
        const errorMessage = err.message || 'An unexpected error occurred'
        setError(errorMessage)
        return { success: false, error: errorMessage }
      } finally {
        setLoading(false)
      }
    },
    [apiCall]
  )

  const reset = useCallback(() => {
    setData(null)
    setError(null)
    setLoading(false)
  }, [])

  return { data, loading, error, execute, reset }
}

/**
 * Custom hook for handling API mutations (POST, PUT, DELETE)
 * Includes success state for showing success messages
 * 
 * @param {Function} apiCall - API service function to call
 * @returns {object} { data, loading, error, success, execute, reset }
 */
export const useMutation = (apiCall) => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  const execute = useCallback(
    async (...args) => {
      setLoading(true)
      setError(null)
      setSuccess(false)
      setData(null)

      try {
        const result = await apiCall(...args)
        
        if (result.success) {
          setData(result.data)
          setSuccess(true)
          return { success: true, data: result.data }
        } else {
          setError(result.error)
          setSuccess(false)
          return { success: false, error: result.error }
        }
      } catch (err) {
        const errorMessage = err.message || 'An unexpected error occurred'
        setError(errorMessage)
        setSuccess(false)
        return { success: false, error: errorMessage }
      } finally {
        setLoading(false)
      }
    },
    [apiCall]
  )

  const reset = useCallback(() => {
    setData(null)
    setError(null)
    setSuccess(false)
    setLoading(false)
  }, [])

  return { data, loading, error, success, execute, reset }
}
