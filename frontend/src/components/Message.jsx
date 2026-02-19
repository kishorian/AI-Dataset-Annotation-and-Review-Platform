import React, { useEffect } from 'react'
import './Message.css'

/**
 * Message component for displaying success/error messages
 * 
 * @param {string} type - Message type: 'success' | 'error' | 'info'
 * @param {string} message - Message text
 * @param {boolean} visible - Whether message is visible
 * @param {Function} onClose - Callback when message is closed
 * @param {number} duration - Auto-close duration in milliseconds (0 = no auto-close)
 */
const Message = ({ type = 'info', message, visible, onClose, duration = 5000 }) => {
  useEffect(() => {
    if (visible && duration > 0) {
      const timer = setTimeout(() => {
        onClose?.()
      }, duration)

      return () => clearTimeout(timer)
    }
  }, [visible, duration, onClose])

  if (!visible || !message) {
    return null
  }

  return (
    <div className={`message message-${type}`}>
      <div className="message-content">
        <span className="message-icon">
          {type === 'success' && '✓'}
          {type === 'error' && '✕'}
          {type === 'info' && 'ℹ'}
        </span>
        <span className="message-text">{message}</span>
      </div>
      <button className="message-close" onClick={onClose}>
        ×
      </button>
    </div>
  )
}

export default Message
