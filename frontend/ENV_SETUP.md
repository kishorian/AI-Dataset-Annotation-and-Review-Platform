# Environment Variables Setup

## Configuration

Create a `.env` file in the `frontend/` directory with the following:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENV=development
```

## Environment Variables

### VITE_API_BASE_URL
- **Description**: Base URL for the FastAPI backend
- **Default**: `http://localhost:8000`
- **Example**: `http://localhost:8000` or `https://api.example.com`

### VITE_ENV
- **Description**: Environment name (development, production, etc.)
- **Default**: `development`
- **Usage**: Used for environment-specific configurations

## Usage

The environment variables are accessed via `import.meta.env` in Vite:

```javascript
import config from './config/env'

console.log(config.apiBaseURL) // http://localhost:8000
```

## Production

For production builds, set the environment variable before building:

```bash
VITE_API_BASE_URL=https://api.production.com npm run build
```

Or create a `.env.production` file:

```env
VITE_API_BASE_URL=https://api.production.com
VITE_ENV=production
```

## Important Notes

- All Vite environment variables must be prefixed with `VITE_`
- Environment variables are embedded at build time
- Restart the dev server after changing `.env` files
- Never commit `.env` files with sensitive data
