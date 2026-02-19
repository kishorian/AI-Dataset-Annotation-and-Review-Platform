/**
 * JWT token utility functions
 */

/**
 * Decode a JWT token without verification.
 * Note: This only decodes the payload, it does NOT verify the signature.
 * For production, consider using a library like jwt-decode for proper handling.
 * 
 * @param {string} token - JWT token string
 * @returns {object|null} Decoded token payload or null if invalid
 */
export const decodeToken = (token) => {
  try {
    if (!token) return null

    // JWT format: header.payload.signature
    const parts = token.split('.')
    if (parts.length !== 3) {
      return null
    }

    // Decode the payload (second part)
    const payload = parts[1]
    
    // Base64 URL decode
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )

    return JSON.parse(jsonPayload)
  } catch (error) {
    console.error('Error decoding token:', error)
    return null
  }
}

/**
 * Check if a JWT token is expired.
 * 
 * @param {string} token - JWT token string
 * @returns {boolean} True if token is expired or invalid
 */
export const isTokenExpired = (token) => {
  const decoded = decodeToken(token)
  if (!decoded || !decoded.exp) {
    return true
  }

  // exp is in seconds, Date.now() is in milliseconds
  const expirationTime = decoded.exp * 1000
  return Date.now() >= expirationTime
}

/**
 * Get user information from a JWT token.
 * 
 * @param {string} token - JWT token string
 * @returns {object|null} User info object with id, email, role, or null if invalid
 */
export const getUserFromToken = (token) => {
  const decoded = decodeToken(token)
  if (!decoded) {
    return null
  }

  // Check if token is expired
  if (isTokenExpired(token)) {
    return null
  }

  return {
    id: decoded.sub, // User ID from 'sub' claim
    email: decoded.email || null,
    role: decoded.role || null,
  }
}
