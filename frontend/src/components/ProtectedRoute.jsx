import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/**
 * ProtectedRoute component that protects routes based on authentication and role.
 * 
 * @param {React.ReactNode} children - Child components to render if authorized
 * @param {string|null} requiredRole - Required role ('admin', 'annotator', 'reviewer') or null for any authenticated user
 * @param {string[]} allowedRoles - Array of allowed roles (alternative to requiredRole)
 */
const ProtectedRoute = ({ children, requiredRole = null, allowedRoles = null }) => {
  const { user, loading, isAuthenticated, hasRole, hasAnyRole } = useAuth()

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <div>Loading...</div>
      </div>
    )
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />
  }

  // Check role-based access
  if (allowedRoles && allowedRoles.length > 0) {
    // Use allowedRoles array if provided
    if (!hasAnyRole(allowedRoles)) {
      return <Navigate to="/dashboard" replace />
    }
  } else if (requiredRole) {
    // Use single requiredRole if provided
    if (!hasRole(requiredRole)) {
      return <Navigate to="/dashboard" replace />
    }
  }

  return children
}

export default ProtectedRoute
