# Frontend-Backend Connection Guide

This guide explains how the React frontend connects to the FastAPI backend.

## Architecture Overview

```
React Components
    ↓
Custom Hooks (useApi, useMutation)
    ↓
Service Layer (authService, projectService, etc.)
    ↓
API Service (apiService)
    ↓
Axios Instance (api.js)
    ↓
FastAPI Backend
```

## Environment Configuration

### 1. Create `.env` file

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENV=development
```

### 2. Environment Variables

- **VITE_API_BASE_URL**: Backend API base URL (default: `http://localhost:8000`)
- All Vite env vars must be prefixed with `VITE_`
- Variables are embedded at build time

## Service Layer

### Structure

All API calls go through the service layer:

```
src/services/
├── apiService.js       # Base service with HTTP methods
├── authService.js      # Authentication endpoints
├── projectService.js   # Project endpoints
├── sampleService.js    # Data sample endpoints
├── annotationService.js # Annotation endpoints
├── reviewService.js    # Review endpoints
└── analyticsService.js # Analytics endpoints
```

### Usage Example

```jsx
import { projectService } from '../services'

// In component
const result = await projectService.getProjects()

if (result.success) {
  // Handle success
  console.log(result.data)
} else {
  // Handle error
  console.error(result.error)
}
```

## Custom Hooks

### useApi Hook

For GET requests with loading/error states:

```jsx
import { useApi } from '../hooks/useApi'
import { projectService } from '../services'

function MyComponent() {
  const { data, loading, error, execute } = useApi(projectService.getProjects)

  useEffect(() => {
    execute()
  }, [execute])

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>

  return <div>{/* Render data */}</div>
}
```

### useMutation Hook

For POST/PUT/DELETE with success states:

```jsx
import { useMutation } from '../hooks/useApi'
import { annotationService } from '../services'

function MyComponent() {
  const { loading, success, error, execute } = useMutation(
    annotationService.submitAnnotation
  )

  const handleSubmit = async () => {
    await execute({ sample_id: '...', label: 'positive' })
  }

  return (
    <div>
      {success && <div>Success!</div>}
      {error && <div>Error: {error}</div>}
      <button onClick={handleSubmit} disabled={loading}>
        Submit
      </button>
    </div>
  )
}
```

## Error Handling

### Automatic Error Handling

- **Network errors**: Detected and formatted
- **401 Unauthorized**: Automatic logout and redirect
- **403 Forbidden**: Error message displayed
- **Validation errors**: Extracted and displayed

### Error Message Component

```jsx
import { useMessage } from '../hooks/useMessage'
import Message from '../components/Message'

function MyComponent() {
  const { message, type, visible, showError, showSuccess, clearMessage } = useMessage()

  return (
    <>
      <Message
        type={type}
        message={message}
        visible={visible}
        onClose={clearMessage}
      />
      {/* Component content */}
    </>
  )
}
```

## Authentication Headers

### Automatic Token Attachment

Tokens are automatically attached to all requests:

1. **Request Interceptor** (`src/utils/api.js`):
   - Reads token from `localStorage`
   - Adds `Authorization: Bearer <token>` header

2. **AuthContext**:
   - Stores token after login
   - Token persists across page refreshes

### Manual Token Management

```javascript
// Token is automatically managed, but you can access it:
const token = localStorage.getItem('token')

// Token is automatically attached to all API calls
// No manual header setting needed
```

## Response Format

All service methods return a consistent format:

```javascript
{
  success: true,           // Boolean indicating success
  data: {...},             // Response data (if success)
  error: "Error message",  // Error message (if !success)
  status: 200,             // HTTP status code
  isNetworkError: false,   // True if network error
  isAuthError: false,      // True if 401/403
  originalError: error     // Original error object
}
```

## Loading States

### Component-Level Loading

```jsx
const { loading, data } = useApi(service.getData)

if (loading) {
  return <div>Loading...</div>
}
```

### Button-Level Loading

```jsx
const { loading, execute } = useMutation(service.submitData)

<button onClick={execute} disabled={loading}>
  {loading ? 'Submitting...' : 'Submit'}
</button>
```

## Success Messages

### Using useMessage Hook

```jsx
import { useMessage } from '../hooks/useMessage'
import Message from '../components/Message'

function MyComponent() {
  const { showSuccess, showError, message, type, visible, clearMessage } = useMessage()

  const handleSuccess = () => {
    showSuccess('Operation completed successfully!')
  }

  return (
    <>
      <Message
        type={type}
        message={message}
        visible={visible}
        onClose={clearMessage}
      />
      <button onClick={handleSuccess}>Do Something</button>
    </>
  )
}
```

### Using useMutation Hook

```jsx
const { success, execute } = useMutation(service.submitData)

useEffect(() => {
  if (success) {
    showSuccess('Data submitted successfully!')
  }
}, [success])
```

## Testing the Connection

### 1. Start Backend

```bash
cd <project-root>
uvicorn app.main:app --reload
```

Backend should be running at `http://localhost:8000`

### 2. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend should be running at `http://localhost:3000`

### 3. Verify Connection

1. Open browser console
2. Check Network tab for API calls
3. Verify `Authorization: Bearer <token>` header is present
4. Check for CORS errors (should be handled by proxy)

## Troubleshooting

### CORS Issues

If you see CORS errors:
- Ensure backend CORS is configured correctly
- Check `CORS_ORIGINS` in backend `.env`
- Verify frontend is using correct `VITE_API_BASE_URL`

### 401 Unauthorized

- Check if token exists in `localStorage`
- Verify token is not expired
- Check backend `SECRET_KEY` matches

### Network Errors

- Verify backend is running
- Check `VITE_API_BASE_URL` is correct
- Ensure no firewall blocking requests

### Proxy Issues (Development)

If using Vite proxy, ensure `vite.config.js` proxy is configured:

```javascript
proxy: {
  '/api': {
    target: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
    changeOrigin: true
  }
}
```

## Production Deployment

### Environment Variables

Set environment variables in your hosting platform:

- **Vercel**: Add in project settings
- **Netlify**: Add in site settings
- **Render**: Add in environment variables

### Build Command

```bash
npm run build
```

### Build Output

The `dist/` folder contains the production build.

## Best Practices

1. **Always use service layer**: Don't call `api` directly from components
2. **Use custom hooks**: `useApi` and `useMutation` for state management
3. **Handle errors**: Always check `result.success` before using data
4. **Show loading states**: Provide user feedback during API calls
5. **Display messages**: Use `Message` component for success/error feedback
6. **Environment variables**: Use `.env` files for configuration
