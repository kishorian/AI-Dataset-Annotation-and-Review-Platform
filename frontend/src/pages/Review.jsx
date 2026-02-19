import React, { useState, useEffect } from 'react'
import { annotationService, reviewService } from '../services'
import { useApi, useMutation } from '../hooks/useApi'
import { useMessage } from '../hooks/useMessage'
import Message from '../components/Message'
import './Review.css'

const Review = () => {
  const [selectedAnnotation, setSelectedAnnotation] = useState(null)
  const [feedback, setFeedback] = useState('')
  
  const { data: annotations, loading, execute: fetchAnnotations } = useApi(
    annotationService.getAnnotations
  )
  
  const { 
    loading: submitting, 
    success, 
    error: submitError,
    execute: approveAnnotation,
    reset: resetApprove
  } = useMutation(reviewService.approveAnnotation)
  
  const { 
    loading: rejecting,
    success: rejectSuccess,
    error: rejectError,
    execute: rejectAnnotation,
    reset: resetReject
  } = useMutation(reviewService.rejectAnnotation)
  
  const { message, type, visible, showSuccess, showError, clearMessage } = useMessage()

  useEffect(() => {
    fetchAnnotations()
  }, [fetchAnnotations])

  useEffect(() => {
    if (success) {
      showSuccess('Annotation approved successfully!')
      setSelectedAnnotation(null)
      setFeedback('')
      fetchAnnotations()
      resetApprove()
    }
  }, [success, showSuccess, fetchAnnotations, resetApprove])

  useEffect(() => {
    if (rejectSuccess) {
      showSuccess('Annotation rejected successfully!')
      setSelectedAnnotation(null)
      setFeedback('')
      fetchAnnotations()
      resetReject()
    }
  }, [rejectSuccess, showSuccess, fetchAnnotations, resetReject])

  useEffect(() => {
    if (submitError) {
      showError(submitError)
      resetApprove()
    }
  }, [submitError, showError, resetApprove])

  useEffect(() => {
    if (rejectError) {
      showError(rejectError)
      resetReject()
    }
  }, [rejectError, showError, resetReject])

  const handleApprove = async () => {
    if (!selectedAnnotation) return

    clearMessage()
    await approveAnnotation(selectedAnnotation.id, feedback || null)
  }

  const handleReject = async () => {
    if (!selectedAnnotation || !feedback.trim()) {
      showError('Feedback is required for rejection')
      return
    }

    clearMessage()
    await rejectAnnotation(selectedAnnotation.id, feedback)
  }

  if (loading) {
    return (
      <div className="page-container">
        <div style={{ textAlign: 'center', padding: '40px' }}>Loading...</div>
      </div>
    )
  }

  return (
    <div className="page-container">
      <Message
        type={type}
        message={message}
        visible={visible}
        onClose={clearMessage}
      />
      
      <div className="page-header">
        <h1>Review</h1>
        <p>Review and approve/reject annotations</p>
      </div>

      <div className="review-layout">
        <div className="annotations-list">
          <h3>Annotations ({annotations?.length || 0})</h3>
          {annotations && annotations.map((annotation) => (
            <div
              key={annotation.id}
              className={`annotation-item ${selectedAnnotation?.id === annotation.id ? 'active' : ''}`}
              onClick={() => {
                setSelectedAnnotation(annotation)
                setFeedback('')
                setMessage('')
              }}
            >
              <div className="annotation-label">{annotation.label}</div>
              <div className="annotation-date">
                {new Date(annotation.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
          {(!annotations || annotations.length === 0) && <p className="empty-state">No annotations to review</p>}
        </div>

        <div className="review-form-container">
          {selectedAnnotation ? (
            <div className="review-form">
              <div className="form-section">
                <h3>Annotation Details</h3>
                <div className="detail-row">
                  <span className="detail-label">Label:</span>
                  <span className="detail-value">{selectedAnnotation.label}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Created:</span>
                  <span className="detail-value">
                    {new Date(selectedAnnotation.created_at).toLocaleString()}
                  </span>
                </div>
              </div>

              <div className="form-section">
                <label htmlFor="feedback">Feedback (required for rejection)</label>
                <textarea
                  id="feedback"
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="Enter your feedback..."
                  rows={4}
                />
              </div>

              <div className="review-actions">
                <button
                  type="button"
                  className="approve-button"
                  onClick={handleApprove}
                  disabled={submitting || rejecting}
                >
                  {(submitting || rejecting) ? 'Processing...' : 'Approve'}
                </button>
                <button
                  type="button"
                  className="reject-button"
                  onClick={handleReject}
                  disabled={submitting || rejecting || !feedback.trim()}
                >
                  {(submitting || rejecting) ? 'Processing...' : 'Reject'}
                </button>
              </div>
            </div>
          ) : (
            <div className="empty-form">
              <p>Select an annotation to review</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Review
