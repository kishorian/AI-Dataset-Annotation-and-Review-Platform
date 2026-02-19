/**
 * Example usage and test cases for JWT utilities
 * 
 * This file demonstrates how to use the JWT utility functions.
 * In a real project, you would use a testing framework like Jest.
 */

import { decodeToken, isTokenExpired, getUserFromToken } from './jwt'

// Example JWT token (this is a sample, not a real token)
const exampleToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'

// Usage examples:
// const decoded = decodeToken(exampleToken)
// const expired = isTokenExpired(exampleToken)
// const user = getUserFromToken(exampleToken)

export { exampleToken }
