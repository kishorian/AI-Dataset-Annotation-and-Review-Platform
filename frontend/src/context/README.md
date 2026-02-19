# AuthContext Documentation

## Overview

The `AuthContext` provides authentication state management for the React application. It handles JWT token storage, automatic token attachment to API requests, role-based access control, and route protection.

## Features

✅ **JWT Token Storage**: Tokens are stored in `localStorage` for persistence across page refreshes  
✅ **Automatic Token Attachment**: Tokens are automatically added to all Axios requests  
✅ **Token Decoding**: JWT tokens are decoded to extract user information (ID, email, role)  
✅ **Role-Based Access**: Helper functions for checking user roles  
✅ **Route Protection**: Integration with `ProtectedRoute` component for role-based route access  
✅ **Token Expiration**: Automatic detection and handling of expired tokens  

## Usage

### Basic Usage

```jsx
import { useAuth } from '../context/AuthContext'

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth()

  if (!isAuthenticated) {
    return <div>Please login</div>
  }

  return (
    <div>
      <p>Welcome, {user.email}</p>
      <p>Role: {user.role}</p>
      <button onClick={logout}>Logout</button>
    </div>
  )
}
```

### Login

```jsx
const { login } = useAuth()

const handleLogin = async () => {
  try {
    await login(email, password)
    // User is now authenticated
    navigate('/dashboard')
  } catch (error) {
    console.error('Login failed:', error)
  }
}
```

### Register

```jsx
const { register } = useAuth()

const handleRegister = async () => {
  try {
    await register(email, password, 'annotator')
    // User is automatically logged in after registration
    navigate('/dashboard')
  } catch (error) {
    console.error('Registration failed:', error)
  }
}
```

### Role Checking

```jsx
const { isAdmin, isAnnotator, isReviewer, hasRole, hasAnyRole } = useAuth()

// Convenience properties
if (isAdmin) {
  // Admin-only code
}

// Custom role check
if (hasRole('admin')) {
  // Admin-only code
}

// Multiple roles
if (hasAnyRole(['admin', 'reviewer'])) {
  // Admin or reviewer code
}
```

## API Reference

### AuthContext Value

The context provides the following values:

| Property | Type | Description |
|----------|------|-------------|
| `user` | `object\|null` | Current user object with `id`, `email`, `role` |
| `token` | `string\|null` | Current JWT token |
| `loading` | `boolean` | Whether auth state is being loaded |
| `isAuthenticated` | `boolean` | Whether user is authenticated |
| `login` | `function` | Login function `(email, password) => Promise` |
| `register` | `function` | Register function `(email, password, role) => Promise` |
| `logout` | `function` | Logout function (clears token and user) |
| `hasRole` | `function` | Check if user has specific role `(role) => boolean` |
| `hasAnyRole` | `function` | Check if user has any of the roles `(roles[]) => boolean` |
| `isAdmin` | `boolean` | Convenience: `user?.role === 'admin'` |
| `isAnnotator` | `boolean` | Convenience: `user?.role === 'annotator'` |
| `isReviewer` | `boolean` | Convenience: `user?.role === 'reviewer'` |

## Token Management

### Storage

Tokens are stored in `localStorage` with the key `'token'`:

```javascript
localStorage.setItem('token', access_token)
```

### Automatic Attachment

The token is automatically attached to all Axios requests via:

1. **Axios Interceptor** (`src/utils/api.js`): Adds `Authorization: Bearer <token>` header
2. **AuthContext**: Sets token in `api.defaults.headers.common['Authorization']`

### Token Decoding

The JWT token is decoded using utility functions in `src/utils/jwt.js`:

- `decodeToken(token)`: Decodes JWT payload
- `getUserFromToken(token)`: Extracts user info (id, email, role)
- `isTokenExpired(token)`: Checks if token is expired

The token payload structure:
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "role": "annotator",
  "exp": 1234567890,
  "iat": 1234567890
}
```

## Route Protection

### Using ProtectedRoute

```jsx
import ProtectedRoute from './components/ProtectedRoute'

// Protect route for any authenticated user
<ProtectedRoute>
  <MyComponent />
</ProtectedRoute>

// Protect route for specific role
<ProtectedRoute requiredRole="admin">
  <AdminComponent />
</ProtectedRoute>

// Protect route for multiple roles
<ProtectedRoute allowedRoles={['admin', 'reviewer']}>
  <AdminOrReviewerComponent />
</ProtectedRoute>
```

### Route Configuration in App.jsx

```jsx
<Route 
  path="analytics" 
  element={
    <ProtectedRoute requiredRole="admin">
      <Analytics />
    </ProtectedRoute>
  } 
/>

<Route 
  path="annotation" 
  element={
    <ProtectedRoute allowedRoles={['annotator', 'admin']}>
      <Annotation />
    </ProtectedRoute>
  } 
/>
```

## Flow Diagram

```
1. User logs in
   ↓
2. Token received from API
   ↓
3. Token stored in localStorage
   ↓
4. Token decoded to get user info
   ↓
5. User state updated
   ↓
6. Token attached to all API requests
   ↓
7. Protected routes check authentication/role
   ↓
8. User accesses protected content
```

## Security Considerations

1. **Token Storage**: Tokens are stored in `localStorage` which is accessible to JavaScript. For enhanced security, consider:
   - Using httpOnly cookies (requires backend changes)
   - Implementing token refresh mechanism
   - Adding CSRF protection

2. **Token Decoding**: The current implementation decodes tokens without verification. This is acceptable for client-side role checks, but:
   - Backend always verifies token signature
   - Never trust client-side role checks for sensitive operations
   - Always verify permissions on the backend

3. **Token Expiration**: Expired tokens are automatically detected and removed. Users are redirected to login.

4. **Automatic Logout**: On 401 responses, users are automatically logged out and redirected to login.

## Error Handling

The AuthContext handles various error scenarios:

- **Invalid Token**: Token is removed, user is logged out
- **Expired Token**: Token is removed, user must login again
- **401 Response**: Automatic logout and redirect to login
- **Network Errors**: Handled gracefully with error messages

## Example: Complete Authentication Flow

```jsx
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

function LoginPage() {
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (error) {
      alert('Login failed')
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input 
        type="email" 
        value={email} 
        onChange={(e) => setEmail(e.target.value)} 
      />
      <input 
        type="password" 
        value={password} 
        onChange={(e) => setPassword(e.target.value)} 
      />
      <button type="submit">Login</button>
    </form>
  )
}
```
