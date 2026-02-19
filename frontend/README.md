# AI Dataset Annotation Platform - Frontend

A modern React application for the AI Dataset Annotation and Review Platform.

## Features

- React Router v6 for navigation
- Axios for API communication
- Context API for authentication state management
- Role-based protected routes
- Responsive sidebar layout
- Clean, minimal UI design
- Functional components with hooks

## Pages

- **Login** - User authentication
- **Register** - New user registration
- **Dashboard** - Overview with statistics
- **Projects** - Project management
- **Annotation** - Data sample annotation (Annotator only)
- **Review** - Annotation review (Reviewer only)
- **Analytics** - System analytics (Admin only)

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Configuration

The app is configured to proxy API requests to `http://localhost:8000` (FastAPI backend).

To change the backend URL, update `vite.config.js`:

```javascript
proxy: {
  '/api': {
    target: 'http://your-backend-url:8000',
    changeOrigin: true
  }
}
```

## Build

```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable components
│   │   ├── Layout.jsx
│   │   └── ProtectedRoute.jsx
│   ├── context/         # Context providers
│   │   └── AuthContext.jsx
│   ├── pages/           # Page components
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Projects.jsx
│   │   ├── Annotation.jsx
│   │   ├── Review.jsx
│   │   └── Analytics.jsx
│   ├── utils/           # Utility functions
│   │   └── api.js
│   ├── App.jsx          # Main app component
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── package.json
└── vite.config.js
```

## Authentication

The app uses JWT tokens stored in localStorage. The token is automatically included in API requests via Axios interceptors.

## Role-Based Access

Routes are protected based on user roles:
- **Admin**: Access to all pages including Analytics
- **Annotator**: Access to Dashboard, Projects, and Annotation
- **Reviewer**: Access to Dashboard, Projects, and Review
