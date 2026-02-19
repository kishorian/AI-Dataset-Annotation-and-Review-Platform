/**
 * Environment configuration
 * Access environment variables via import.meta.env in Vite
 */

export const config = {
  // API Configuration
  apiBaseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  
  // Environment
  env: import.meta.env.VITE_ENV || import.meta.env.MODE || 'development',
  
  // Check if running in development
  isDevelopment: import.meta.env.DEV,
  
  // Check if running in production
  isProduction: import.meta.env.PROD,
}

// Validate required environment variables
if (!config.apiBaseURL) {
  console.warn('VITE_API_BASE_URL is not set, using default: http://localhost:8000')
}

export default config
