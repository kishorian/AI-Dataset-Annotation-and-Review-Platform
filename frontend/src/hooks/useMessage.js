import { useState, useCallback } from 'react'

/**
 * Custom hook for managing success/error messages
 * 
 * @returns {object} { message, type, showMessage, showSuccess, showError, clearMessage }
 */
export const useMessage = () => {
  const [message, setMessage] = useState('')
  const [type, setType] = useState('info')
  const [visible, setVisible] = useState(false)

  const showMessage = useCallback((msg, msgType = 'info') => {
    setMessage(msg)
    setType(msgType)
    setVisible(true)
  }, [])

  const showSuccess = useCallback((msg) => {
    showMessage(msg, 'success')
  }, [showMessage])

  const showError = useCallback((msg) => {
    showMessage(msg, 'error')
  }, [showMessage])

  const clearMessage = useCallback(() => {
    setVisible(false)
    // Clear message after animation
    setTimeout(() => {
      setMessage('')
    }, 300)
  }, [])

  return {
    message,
    type,
    visible,
    showMessage,
    showSuccess,
    showError,
    clearMessage,
  }
}
