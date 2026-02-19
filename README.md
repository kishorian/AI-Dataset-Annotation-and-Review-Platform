# AI Dataset Annotation & Review Platform

A production-ready full-stack application for managing AI dataset annotation workflows with role-based access control, automated status management, and comprehensive analytics.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [Workflow](#workflow)
- [Local Setup](#local-setup)
- [Deployment](#deployment)
- [Assumptions](#assumptions)
- [Future Improvements](#future-improvements)

## 🎯 Project Overview

The AI Dataset Annotation & Review Platform is a comprehensive solution for managing the complete lifecycle of AI dataset annotation projects. It provides a structured workflow where administrators create projects and upload data samples, annotators label the data, and reviewers validate the annotations before final approval.

### Key Features

- **Role-Based Access Control**: Three distinct user roles (Admin, Annotator, Reviewer) with granular permissions
- **Automated Workflow Management**: Automatic status transitions based on user actions
- **JWT Authentication**: Secure token-based authentication with role-based authorization
- **Real-time Analytics**: Comprehensive dashboard with approval rates, contribution metrics, and status tracking
- **Full-Stack Integration**: Seamless React frontend with FastAPI backend
- **Production-Ready**: Docker support, health checks, connection pooling, and optimized for cloud deployment

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Browser                          │
│              (React SPA - React Router v6)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              FastAPI Application Server                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Static File Server (React Build)                      │  │
│  │  - Serves /assets/* (JS, CSS, images)                 │  │
│  │  - Serves index.html for SPA routes                   │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Layer (/api/*)                                    │  │
│  │  - Authentication & Authorization                     │  │
│  │  - Project Management                                   │  │
│  │  - Data Sample Management                               │  │
│  │  - Annotation Submission                                │  │
│  │  - Review Workflow                                     │  │
│  │  - Analytics & Reporting                               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Business Logic Layer (Services)                       │  │
│  │  - Transaction Management                              │  │
│  │  - Status Transitions                                  │  │
│  │  - Data Validation                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Data Access Layer (SQLAlchemy ORM)                   │  │
│  │  - Model Definitions                                   │  │
│  │  - Relationship Management                             │  │
│  │  - Query Optimization                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Connection Pool
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              PostgreSQL Database                              │
│  - Users, Projects, Data Samples                             │
│  - Annotations, Reviews                                      │
│  - Indexes for Performance                                   │
└──────────────────────────────────────────────────────────────┘
```

### Application Layers

1. **Presentation Layer (Frontend)**
   - React 18 with functional components
   - React Router v6 for client-side routing
   - Context API for state management
   - Axios for API communication
   - Role-based route protection

2. **API Layer (Backend)**
   - FastAPI with async/await support
   - RESTful API design
   - Automatic OpenAPI documentation
   - Request/response validation with Pydantic
   - Dependency injection for authentication and authorization

3. **Business Logic Layer**
   - Service classes encapsulating business rules
   - Transaction management for data consistency
   - Automatic status transitions
   - Aggregate queries for analytics

4. **Data Access Layer**
   - SQLAlchemy ORM for database abstraction
   - Alembic for schema migrations
   - Connection pooling for performance
   - Optimized indexes for query speed

### Request Flow

```
User Action → React Component → API Call (Axios)
    ↓
FastAPI Router → Dependency Injection (Auth/Role Check)
    ↓
Service Layer → Business Logic + Transaction
    ↓
SQLAlchemy ORM → Database Query
    ↓
PostgreSQL → Result
    ↓
Response Chain (Reverse) → User Interface Update
```

## 🛠️ Tech Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Programming language |
| **FastAPI** | 0.109.0 | Web framework |
| **Uvicorn** | 0.27.0 | ASGI server |
| **SQLAlchemy** | 2.0.25 | ORM |
| **Alembic** | 1.13.1 | Database migrations |
| **PostgreSQL** | 15+ | Database |
| **psycopg2-binary** | 2.9.9 | PostgreSQL adapter |
| **Pydantic** | 2.5.3 | Data validation |
| **python-jose** | 3.3.0 | JWT handling |
| **passlib** | 1.7.4 | Password hashing (bcrypt) |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.2.0 | UI library |
| **React Router** | 6.20.0 | Client-side routing |
| **Axios** | 1.6.2 | HTTP client |
| **Vite** | 5.0.8 | Build tool |
| **Node.js** | 18+ | Runtime |

### DevOps & Deployment

- **Docker** - Containerization
- **Docker Compose** - Local development
- **Render** - Cloud deployment platform
- **Alembic** - Database migrations

## 🗄️ Database Schema

### Entity Relationship Diagram

```
┌─────────────┐
│    User     │
├─────────────┤
│ id (UUID)   │◄─────┐
│ email       │      │
│ password    │      │
│ role        │      │
│ created_at  │      │
└─────────────┘      │
       │              │
       │              │
       ├──────────────┼──────────────┐
       │              │              │
       │              │              │
┌──────▼──────┐  ┌────▼──────┐  ┌───▼──────┐
│   Project   │  │Annotation │  │  Review  │
├─────────────┤  ├───────────┤  ├──────────┤
│ id (UUID)   │  │ id (UUID)  │  │ id (UUID)│
│ name        │  │ sample_id │  │annotation│
│ description │  │ annotator │  │_id       │
│ created_by  │  │ label     │  │ reviewer │
│ created_at  │  │ created_at│  │ decision │
└──────┬──────┘  └─────┬─────┘  │ feedback │
       │               │         │created_at│
       │               │         └──────────┘
       │               │
┌──────▼───────────────▼──────┐
│      DataSample              │
├──────────────────────────────┤
│ id (UUID)                    │
│ project_id                   │
│ text_content                 │
│ status (pending/annotated/   │
│          reviewed)           │
│ created_at                   │
└──────────────────────────────┘
```

### Tables

#### Users
- **Primary Key**: `id` (UUID)
- **Fields**: `email` (unique), `hashed_password`, `role` (enum), `created_at`
- **Relationships**: 
  - One-to-many with Projects (creator)
  - One-to-many with Annotations (annotator)
  - One-to-many with Reviews (reviewer)

#### Projects
- **Primary Key**: `id` (UUID)
- **Fields**: `name`, `description`, `created_by` (FK), `created_at`
- **Relationships**: 
  - Many-to-one with User (creator)
  - One-to-many with DataSamples

#### DataSamples
- **Primary Key**: `id` (UUID)
- **Fields**: `project_id` (FK), `text_content`, `status` (enum), `created_at`
- **Relationships**: 
  - Many-to-one with Project
  - One-to-many with Annotations

#### Annotations
- **Primary Key**: `id` (UUID)
- **Fields**: `sample_id` (FK), `annotator_id` (FK), `label` (enum), `created_at`
- **Relationships**: 
  - Many-to-one with DataSample
  - Many-to-one with User (annotator)
  - One-to-many with Reviews

#### Reviews
- **Primary Key**: `id` (UUID)
- **Fields**: `annotation_id` (FK), `reviewer_id` (FK), `decision` (enum), `feedback`, `created_at`
- **Relationships**: 
  - Many-to-one with Annotation
  - Many-to-one with User (reviewer)

### Enums

- **UserRole**: `admin`, `annotator`, `reviewer`
- **SampleStatus**: `pending`, `annotated`, `reviewed`
- **AnnotationLabel**: `positive`, `negative`, `neutral`
- **ReviewDecision**: `approved`, `rejected`

### Indexes

Optimized indexes on:
- Foreign keys (for join performance)
- Status fields (for filtering)
- Composite indexes for common query patterns
- Email and role fields (for authentication queries)

## 🔄 Workflow

### Complete Annotation Workflow

```
1. ADMIN creates Project
   └─> Project created with metadata

2. ADMIN adds Data Samples to Project
   └─> Samples created with status: PENDING

3. ANNOTATOR views pending samples
   └─> Filters by status: PENDING

4. ANNOTATOR submits Annotation
   └─> Annotation created
   └─> Sample status automatically changes: PENDING → ANNOTATED

5. REVIEWER views annotated samples
   └─> Filters by status: ANNOTATED

6. REVIEWER reviews Annotation
   ├─> If APPROVED:
   │   └─> Review created with decision: APPROVED
   │   └─> Sample status automatically changes: ANNOTATED → REVIEWED
   │
   └─> If REJECTED:
       └─> Review created with decision: REJECTED + feedback
       └─> Sample status automatically changes: ANNOTATED → PENDING
       └─> Workflow returns to step 3 (re-annotation)

7. ADMIN views Analytics
   └─> Dashboard shows:
       - Total samples by status
       - Approval/rejection rates
       - Annotator contribution counts
       - Project-level statistics
```

### Status Transitions

```
PENDING ──[Annotator submits]──> ANNOTATED
                                      │
                                      ├─[Reviewer approves]──> REVIEWED
                                      │
                                      └─[Reviewer rejects]──> PENDING
```

### Role Permissions

| Action | Admin | Annotator | Reviewer |
|--------|-------|-----------|----------|
| Create Project | ✅ | ❌ | ❌ |
| Add Data Samples | ✅ | ❌ | ❌ |
| View Projects | ✅ | ✅ | ✅ |
| View Samples | ✅ | ✅ | ✅ |
| Submit Annotation | ❌ | ✅ | ❌ |
| Review Annotation | ❌ | ❌ | ✅ |
| View Analytics | ✅ | ❌ | ❌ |

## 🚀 Local Setup

### Prerequisites

- **Python** 3.11 or higher
- **Node.js** 18 or higher
- **PostgreSQL** 15 or higher
- **Git** (for cloning)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd "AI Dataset Annotation & Review Platform"
```

### Step 2: Backend Setup

#### Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=AI Dataset Annotation Platform
APP_VERSION=1.0.0
DEBUG=True
LOG_LEVEL=INFO

# CORS (for development)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# Database Pool (optional)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=True
DB_ECHO=False
```

#### Set Up Database

```bash
# Create PostgreSQL database
createdb dbname

# Run migrations
alembic upgrade head
```

#### Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Step 3: Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Configure Environment (Optional)

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

#### Start Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Step 4: Create Initial User

Use the registration endpoint or create via API:

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePassword123!",
    "role": "admin"
  }'
```

### Alternative: Docker Setup

#### Using Docker Compose (Recommended)

```bash
# Start all services (backend + database)
docker-compose up -d

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec web alembic upgrade head

# Stop services
docker-compose down
```

Application will be available at `http://localhost:8000`

## 📦 Deployment

### Render Deployment (Docker)

#### Prerequisites

- Render account
- PostgreSQL database on Render
- GitHub repository (optional, can use Render's Git integration)

#### Step 1: Prepare Repository

Ensure your repository includes:
- `Dockerfile`
- `render.yaml` (optional, for configuration)
- All source code

#### Step 2: Create PostgreSQL Database

1. Go to Render Dashboard
2. Click "New +" → "PostgreSQL"
3. Configure database settings
4. Copy the **Internal Database URL** (for environment variable)

#### Step 3: Create Web Service

1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your repository
4. Configure service:

   **Settings:**
   - **Name**: `ai-dataset-annotation-platform`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`
   - **Docker Context**: `.`

   **Environment Variables:**
   ```
   DATABASE_URL=<render-postgres-internal-url>
   SECRET_KEY=<generate-strong-random-key>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   APP_NAME=AI Dataset Annotation Platform
   APP_VERSION=1.0.0
   DEBUG=False
   LOG_LEVEL=INFO
   ```

   **Generate SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

#### Step 4: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Build Docker image
   - Start container
   - Run health checks

#### Step 5: Run Migrations

**Option 1: Post-Deploy Script (Recommended)**

Add to Render's post-deploy script:
```bash
alembic upgrade head
```

**Option 2: Manual**

SSH into container or use Render shell:
```bash
alembic upgrade head
```

#### Step 6: Verify Deployment

- Check health endpoint: `https://your-app.onrender.com/health`
- Access application: `https://your-app.onrender.com`
- API docs: `https://your-app.onrender.com/api/docs`

### Render Deployment (Native)

Alternatively, use native deployment without Docker:

1. **Build Command:**
   ```bash
   cd frontend && npm install && npm run build && cd .. && pip install -r requirements.txt
   ```

2. **Start Command:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. Configure environment variables (same as Docker)

### Health Checks

The application includes a health check endpoint:

```
GET /health
```

Returns:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

Render automatically monitors this endpoint.

## 📝 Assumptions

### Business Logic Assumptions

1. **Single Annotation per Sample**: Each data sample can have one annotation at a time. When rejected, the sample returns to pending for re-annotation.

2. **Review Workflow**: Each annotation requires review before final approval. Rejected annotations require re-annotation.

3. **Role Hierarchy**: 
   - Admins have full access
   - Annotators can only annotate
   - Reviewers can only review
   - No role escalation or delegation

4. **Status Management**: Status transitions are automatic and transactional. Manual status changes are not supported.

5. **Project Ownership**: Projects are owned by the creating admin. Multiple admins can create projects independently.

### Technical Assumptions

1. **Database**: PostgreSQL is required. The application uses PostgreSQL-specific features (UUID, enums).

2. **Authentication**: JWT tokens are stateless. No refresh token mechanism is implemented.

3. **Frontend-Backend Coupling**: Frontend and backend are deployed together. API is not designed for external consumption.

4. **Concurrency**: The application assumes moderate concurrency. No distributed locking for status transitions.

5. **Data Volume**: Designed for moderate dataset sizes. No pagination limits are enforced (should be added for production).

6. **File Storage**: Text content is stored in database. No file upload mechanism for large datasets.

7. **Email**: No email notifications. Users must check the platform for updates.

8. **Audit Trail**: Created timestamps are tracked, but no update timestamps or change history.

## 🔮 Future Improvements

### Feature Enhancements

1. **Multi-Annotation Support**
   - Allow multiple annotators to annotate the same sample
   - Consensus mechanism (majority vote, weighted average)
   - Inter-annotator agreement metrics

2. **Advanced Analytics**
   - Time-series analytics (annotations per day, trends)
   - Annotator performance metrics (accuracy, speed)
   - Project completion timelines
   - Export capabilities (CSV, JSON, Excel)

3. **Notification System**
   - Email notifications for status changes
   - In-app notifications
   - Webhook support for integrations

4. **File Upload Support**
   - Bulk CSV/JSON import for data samples
   - File attachment support for samples
   - Image/video annotation support

5. **Enhanced Review Workflow**
   - Multi-reviewer consensus
   - Review comments and discussions
   - Review history and audit trail
   - Review assignment and load balancing

6. **User Management**
   - User profiles and preferences
   - Activity history
   - Performance dashboards per user
   - Team management and assignments

### Technical Improvements

1. **Performance**
   - Implement pagination for all list endpoints
   - Add caching layer (Redis) for frequently accessed data
   - Database query optimization and indexing
   - Background job processing (Celery) for heavy operations

2. **Security**
   - Refresh token mechanism
   - Rate limiting
   - API key authentication for external access
   - Two-factor authentication (2FA)
   - Audit logging for sensitive operations

3. **Scalability**
   - Horizontal scaling support
   - Database read replicas
   - CDN for static assets
   - Microservices architecture (if needed)

4. **Testing**
   - Unit tests for services
   - Integration tests for API endpoints
   - Frontend component tests
   - End-to-end testing
   - Load testing

5. **Monitoring & Observability**
   - Application Performance Monitoring (APM)
   - Error tracking (Sentry)
   - Log aggregation (ELK stack)
   - Metrics dashboard (Prometheus + Grafana)

6. **DevOps**
   - CI/CD pipeline (GitHub Actions, GitLab CI)
   - Automated testing in pipeline
   - Blue-green deployment
   - Automated database backups
   - Infrastructure as Code (Terraform)

7. **Documentation**
   - API documentation improvements
   - User guides and tutorials
   - Video walkthroughs
   - Developer onboarding documentation

8. **Internationalization**
   - Multi-language support (i18n)
   - Localized date/time formats
   - RTL language support

9. **Accessibility**
   - WCAG 2.1 compliance
   - Screen reader support
   - Keyboard navigation
   - High contrast mode

10. **Mobile Support**
    - Responsive design improvements
    - Progressive Web App (PWA)
    - Mobile app (React Native)

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue in the repository.

---

**Built with ❤️ using FastAPI and React**
