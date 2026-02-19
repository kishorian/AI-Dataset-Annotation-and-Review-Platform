import React, { useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { analyticsService } from '../services'
import { useApi } from '../hooks/useApi'
import './Dashboard.css'

const Dashboard = () => {
  const { user } = useAuth()
  const { data: stats, loading, error, execute: fetchStats } = useApi(analyticsService.getAnalytics)

  useEffect(() => {
    fetchStats()
  }, [fetchStats])

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
        <h1>Dashboard</h1>
        <p>Welcome back, {user?.email}</p>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <h3>Total Samples</h3>
              <p className="stat-value">{stats.total_samples}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">⏳</div>
            <div className="stat-content">
              <h3>Pending</h3>
              <p className="stat-value">{stats.pending_samples}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">✏️</div>
            <div className="stat-content">
              <h3>Annotated</h3>
              <p className="stat-value">{stats.annotated_samples}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <h3>Reviewed</h3>
              <p className="stat-value">{stats.reviewed_samples}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">👍</div>
            <div className="stat-content">
              <h3>Approval Rate</h3>
              <p className="stat-value">{stats.approval_rate}%</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">👥</div>
            <div className="stat-content">
              <h3>Annotators</h3>
              <p className="stat-value">{stats.annotator_contribution_count}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
