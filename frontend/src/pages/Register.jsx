import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useMessage } from '../hooks/useMessage'
import Message from '../components/Message'
import './Auth.css'

const Register = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('annotator')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()
  const { message, type, visible, showError, clearMessage } = useMessage()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    clearMessage()

    try {
      await register(email, password, role)
      navigate('/dashboard')
    } catch (err) {
      const errorMessage = err.message || err.response?.data?.detail || 'Registration failed. Please try again.'
      showError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <Message
        type={type}
        message={message}
        visible={visible}
        onClose={clearMessage}
      />
      
      <div className="auth-card">
        <h1>Register</h1>
        <p className="auth-subtitle">Create a new account</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="your@email.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Min 8 chars, uppercase, lowercase, digit"
              minLength={8}
            />
          </div>

          <div className="form-group">
            <label htmlFor="role">Role</label>
            <select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              required
            >
              <option value="annotator">Annotator</option>
              <option value="reviewer">Reviewer</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  )
}

export default Register
