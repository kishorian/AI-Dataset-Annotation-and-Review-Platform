# API Service Layer

This directory contains the service layer for all API calls. Services provide a clean abstraction over the API client and handle error responses consistently.

## Structure

- `apiService.js` - Base API service class with common HTTP methods
- `authService.js` - Authentication-related API calls
- `projectService.js` - Project-related API calls
- `sampleService.js` - Data sample-related API calls
- `annotationService.js` - Annotation-related API calls
- `reviewService.js` - Review-related API calls
- `analyticsService.js` - Analytics-related API calls
- `index.js` - Centralized exports

## Usage

### Basic Usage

```jsx
import { projectService } from '../services'

// In component
const result = await projectService.getProjects()

if (result.success) {
  console.log(result.data)
} else {
  console.error(result.error)
}
```

### With useApi Hook

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

### With useMutation Hook

```jsx
import { useMutation } from '../hooks/useApi'
import { annotationService } from '../services'

function MyComponent() {
  const { loading, success, error, execute } = useMutation(annotationService.submitAnnotation)

  const handleSubmit = async () => {
    const result = await execute({ sample_id: '...', label: 'positive' })
    if (result.success) {
      // Handle success
    }
  }
}
```

## Response Format

All service methods return a consistent response format:

```javascript
{
  success: true,  // or false
  data: {...},    // Response data (if success)
  error: "...",   // Error message (if !success)
  status: 200,    // HTTP status code
  isNetworkError: false,
  isAuthError: false,
  originalError: error  // Original error object
}
```

## Error Handling

Errors are automatically handled by the service layer:

- Network errors are detected and formatted
- Authentication errors (401/403) are identified
- Validation errors are extracted
- User-friendly error messages are provided

## Adding New Services

1. Create a new service file (e.g., `newService.js`)
2. Import `apiService` from `./apiService`
3. Create a class with methods that call `apiService.get/post/put/delete`
4. Export a singleton instance
5. Add to `index.js` exports

Example:

```javascript
import apiService from './apiService'

class NewService {
  async getItems() {
    return await apiService.get('/items/')
  }
}

export default new NewService()
```
