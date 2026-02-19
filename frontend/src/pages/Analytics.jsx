import React, { useEffect } from 'react'
import { analyticsService } from '../services'
import { useApi } from '../hooks/useApi'
import './Analytics.css'

const Analytics = () => {
  const { data: analytics, loading, error, execute: fetchAnalytics } = useApi(
    analyticsService.getAnalytics
  )

  useEffect(() => {
    fetchAnalytics()
  }, [fetchAnalytics])

  if (loading) {
    return (
      <div className="page-container">
        <div style={{ textAlign: 'center', padding: '40px' }}>Loading...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="error-message">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Analytics</h1>
        <p>System-wide statistics and metrics</p>
      </div>

      {analytics && (
        <div className="analytics-content">
          <div className="analytics-section">
            <h2>Sample Statistics</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-label">Total Samples</div>
                <div className="stat-number">{analytics.total_samples}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Pending</div>
                <div className="stat-number">{analytics.pending_samples}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Annotated</div>
                <div className="stat-number">{analytics.annotated_samples}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Reviewed</div>
                <div className="stat-number">{analytics.reviewed_samples}</div>
              </div>
            </div>
          </div>

          <div className="analytics-section">
            <h2>Review Metrics</h2>
            <div className="metrics-grid">
              <div className="metric-card approval">
                <div className="metric-label">Approval Rate</div>
                <div className="metric-value">{analytics.approval_rate}%</div>
                <div className="metric-bar">
                  <div
                    className="metric-fill"
                    style={{ width: `${analytics.approval_rate}%` }}
                  />
                </div>
              </div>
              <div className="metric-card rejection">
                <div className="metric-label">Rejection Rate</div>
                <div className="metric-value">{analytics.rejection_rate}%</div>
                <div className="metric-bar">
                  <div
                    className="metric-fill"
                    style={{ width: `${analytics.rejection_rate}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="analytics-section">
            <h2>Contributors</h2>
            <div className="contributor-card">
              <div className="contributor-label">Active Annotators</div>
              <div className="contributor-value">{analytics.annotator_contribution_count}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Analytics
