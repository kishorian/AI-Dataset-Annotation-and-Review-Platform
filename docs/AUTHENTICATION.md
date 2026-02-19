# JWT Authentication System

This document describes the JWT authentication system implemented in the FastAPI backend.

## Overview

The authentication system uses:
- **JWT (JSON Web Tokens)** for stateless authentication
- **bcrypt** for password hashing
- **python-jose** for JWT encoding/decoding
- **Role-based access control (RBAC)** for authorization

## Endpoints

### 1. Register User

**POST** `/api/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "role": "annotator"  // optional, defaults to "annotator"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "annotator",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Password Requirements:**
- Minimum 8 characters
- Maximum 128 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

### 2. Login

**POST** `/api/auth/login`

Authenticate and receive an access token.

**Request Body (Form Data):**
```
username: user@example.com  # Note: OAuth2 uses 'username' field for email
password: SecurePass123
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Verify Token

**POST** `/api/auth/verify-token`

Verify if an access token is valid.

**Request Body:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "valid": true,
  "message": "Token is valid"
}
```

### 4. Get Current User

**GET** `/api/auth/me`

Get information about the currently authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "annotator",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Using Authentication in Routes

### Basic Authentication

Protect a route to require any authenticated user:

```python
from app.core.dependencies import get_current_user
from app.models.user import User

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    return {"message": f"Hello {current_user.email}"}
```

### Role-Based Access Control

#### Require Admin Role

```python
from app.core.dependencies import require_admin

@router.delete("/admin-only")
async def admin_route(
    current_user: User = Depends(require_admin)
):
    return {"message": "Admin operation"}
```

#### Require Reviewer Role

```python
from app.core.dependencies import require_reviewer

@router.post("/review")
async def review_route(
    current_user: User = Depends(require_reviewer)
):
    return {"message": "Review operation"}
```

#### Require Annotator Role

```python
from app.core.dependencies import require_annotator

@router.post("/annotate")
async def annotate_route(
    current_user: User = Depends(require_annotator)
):
    return {"message": "Annotation operation"}
```

#### Custom Role Requirements

```python
from app.core.dependencies import require_roles
from app.models.enums import UserRole

@router.get("/custom")
async def custom_route(
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.REVIEWER]))
):
    return {"message": "Custom role check"}
```

## Token Structure

The JWT token contains:

```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "role": "annotator",
  "type": "access",
  "iat": 1234567890,
  "exp": 1234567890
}
```

- **sub**: User ID (subject)
- **email**: User email
- **role**: User role
- **type**: Token type ("access")
- **iat**: Issued at timestamp
- **exp**: Expiration timestamp

## Token Expiration

Tokens expire after the time specified in `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 30 minutes).

When a token expires, you'll receive a `401 Unauthorized` response. The client should prompt the user to login again.

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials"
}
```

**Causes:**
- Missing or invalid token
- Expired token
- Invalid token signature

### 403 Forbidden

```json
{
  "detail": "Operation requires admin role"
}
```

**Causes:**
- User doesn't have required role
- Insufficient permissions

### 400 Bad Request

```json
{
  "detail": "Password must be at least 8 characters long"
}
```

**Causes:**
- Invalid request data
- Password doesn't meet requirements

### 409 Conflict

```json
{
  "detail": "User with email user@example.com already exists"
}
```

**Causes:**
- User already exists during registration

## Security Best Practices

1. **Always use HTTPS** in production
2. **Store tokens securely** (e.g., httpOnly cookies or secure storage)
3. **Don't expose tokens** in URLs or logs
4. **Implement token refresh** for better UX (future enhancement)
5. **Use strong passwords** (enforced by validation)
6. **Rotate SECRET_KEY** regularly in production
7. **Monitor authentication failures** for security threats

## Example: Using Token in Requests

### cURL

```bash
# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePass123"

# Use token
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

### Python (requests)

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={
        "username": "user@example.com",
        "password": "SecurePass123"
    }
)
token = response.json()["access_token"]

# Use token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/auth/me",
    headers=headers
)
print(response.json())
```

### JavaScript (fetch)

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    username: 'user@example.com',
    password: 'SecurePass123'
  })
});

const { access_token } = await loginResponse.json();

// Use token
const userResponse = await fetch('http://localhost:8000/api/auth/me', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});

const user = await userResponse.json();
console.log(user);
```

## Configuration

Authentication settings can be configured in `.env`:

```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Important:** Use a strong, random `SECRET_KEY` in production. Generate one with:

```python
import secrets
print(secrets.token_urlsafe(32))
```
