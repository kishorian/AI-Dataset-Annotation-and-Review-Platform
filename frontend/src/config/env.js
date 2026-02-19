/**
 * Environment configuration
 * Access environment variables via import.meta.env in Vite
 */

// Determine API base URL
// In production (when served from same origin), use relative URL
// In development, use localhost or environment variable
const getApiBaseURL = () => {
  // If explicitly set via environment variable, use it
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  
  // In production, use relative URL (same origin)
  if (import.meta.env.PROD) {
    return '' // Empty string means relative URL (same origin)
  }
  
  // In development, default to localhost
  return 'http://localhost:8000'
}

export const config = {
  // API Configuration
  apiBaseURL: getApiBaseURL(),
  
  // Environment
  env: import.meta.env.VITE_ENV || import.meta.env.MODE || 'development',
  
  // Check if running in development
  isDevelopment: import.meta.env.DEV,
  
  // Check if running in production
  isProduction: import.meta.env.PROD,
}

export default config
