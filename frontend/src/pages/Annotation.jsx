import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { sampleService, annotationService } from '../services'
import { useApi, useMutation } from '../hooks/useApi'
import { useMessage } from '../hooks/useMessage'
import Message from '../components/Message'
import './Annotation.css'

const Annotation = () => {
  const { user } = useAuth()
  const [selectedSample, setSelectedSample] = useState(null)
  const [label, setLabel] = useState('positive')
  
  const { data: samples, loading, execute: fetchPendingSamples } = useApi(
    () => sampleService.getSamplesByStatus('pending')
  )
  
  const { 
    loading: submitting, 
    success, 
    error: submitError,
    execute: submitAnnotation,
    reset: resetSubmit
  } = useMutation(annotationService.submitAnnotation)
  
  const { message, type, visible, showSuccess, showError, clearMessage } = useMessage()

  useEffect(() => {
    fetchPendingSamples()
  }, [fetchPendingSamples])

  useEffect(() => {
    if (success) {
      showSuccess('Annotation submitted successfully!')
      setSelectedSample(null)
      fetchPendingSamples()
      resetSubmit()
    }
  }, [success, showSuccess, fetchPendingSamples, resetSubmit])

  useEffect(() => {
    if (submitError) {
      showError(submitError)
      resetSubmit()
    }
  }, [submitError, showError, resetSubmit])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!selectedSample) return

    clearMessage()
    await submitAnnotation({
      sample_id: selectedSample.id,
      label: label,
    })
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
        <h1>Annotation</h1>
        <p>Annotate pending data samples</p>
      </div>

      <div className="annotation-layout">
        <div className="samples-list">
          <h3>Pending Samples ({samples?.length || 0})</h3>
          {samples && samples.map((sample) => (
            <div
              key={sample.id}
              className={`sample-item ${selectedSample?.id === sample.id ? 'active' : ''}`}
              onClick={() => setSelectedSample(sample)}
            >
              <p className="sample-text">{sample.text_content.substring(0, 100)}...</p>
            </div>
          ))}
          {(!samples || samples.length === 0) && <p className="empty-state">No pending samples</p>}
        </div>

        <div className="annotation-form-container">
          {selectedSample ? (
            <form onSubmit={handleSubmit} className="annotation-form">
              <div className="form-section">
                <h3>Sample Text</h3>
                <div className="sample-display">{selectedSample.text_content}</div>
              </div>

              <div className="form-section">
                <label htmlFor="label">Label</label>
                <select
                  id="label"
                  value={label}
                  onChange={(e) => setLabel(e.target.value)}
                  required
                >
                  <option value="positive">Positive</option>
                  <option value="negative">Negative</option>
                  <option value="neutral">Neutral</option>
                </select>
              </div>

              <button type="submit" className="submit-button" disabled={submitting}>
                {submitting ? 'Submitting...' : 'Submit Annotation'}
              </button>
            </form>
          ) : (
            <div className="empty-form">
              <p>Select a sample to annotate</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Annotation
