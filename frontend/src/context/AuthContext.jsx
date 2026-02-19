import React, { createContext, useContext, useState, useEffect } from 'react'
import { authService } from '../services'
import { getUserFromToken, isTokenExpired } from '../utils/jwt'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(null)

  // Initialize auth state from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      // Check if token is expired
      if (isTokenExpired(storedToken)) {
        // Token expired, remove it
        localStorage.removeItem('token')
        setLoading(false)
        return
      }

      // Decode token to get user info immediately
      const userFromToken = getUserFromToken(storedToken)
      if (userFromToken) {
        setUser(userFromToken)
        setToken(storedToken)
        api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
        
      // Verify with backend to get full user data
      fetchCurrentUser()
      } else {
        localStorage.removeItem('token')
        setLoading(false)
      }
    } else {
      setLoading(false)
    }
  }, [])

  // Fetch current user from backend to verify token and get full user data
  const fetchCurrentUser = async () => {
    const result = await authService.getCurrentUser()
    
    if (result.success) {
      // Update user with full data from backend
      setUser(result.data)
    } else {
      // Token invalid on backend, clear everything
      localStorage.removeItem('token')
      setUser(null)
      setToken(null)
    }
    
    setLoading(false)
  }

  const login = async (email, password) => {
    const result = await authService.login(email, password)
    
    if (result.success) {
      const { access_token } = result.data
      
      // Store token in localStorage
      localStorage.setItem('token', access_token)
      setToken(access_token)
      
      // Decode token to get user info immediately
      const userFromToken = getUserFromToken(access_token)
      if (userFromToken) {
        setUser(userFromToken)
      }

      // Fetch full user data from backend
      await fetchCurrentUser()
      
      return result.data
    } else {
      throw new Error(result.error)
    }
  }

  const register = async (email, password, role = 'annotator') => {
    const result = await authService.register(email, password, role)
    
    if (result.success) {
      // Auto-login after registration
      await login(email, password)
      return result.data
    } else {
      throw new Error(result.error)
    }
  }

  const logout = () => {
    // Remove token from localStorage
    localStorage.removeItem('token')
    
    // Clear state
    setUser(null)
    setToken(null)
  }

  // Check if user has specific role
  const hasRole = (role) => {
    return user?.role === role
  }

  // Check if user has any of the specified roles
  const hasAnyRole = (roles) => {
    return roles.includes(user?.role)
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    hasRole,
    hasAnyRole,
    // Convenience role checks
    isAdmin: user?.role === 'admin',
    isAnnotator: user?.role === 'annotator',
    isReviewer: user?.role === 'reviewer',
    // Check if authenticated
    isAuthenticated: !!user && !!token,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
