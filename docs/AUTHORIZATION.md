# Role-Based Authorization Guide

This document describes the role-based authorization system for the AI Dataset Annotation and Review Platform.

## Overview

The platform uses role-based access control (RBAC) with three user roles:
- **Admin**: Full system access
- **Annotator**: Can submit annotations
- **Reviewer**: Can review annotations

## Authorization Dependencies

### Admin-Only Operations

#### Create Project
**Dependency:** `can_create_project`

Only administrators can create new projects.

```python
from app.core.dependencies import can_create_project
from app.models.user import User

@router.post("/projects")
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(can_create_project)
):
    # Only admins can reach here
    return create_project_service(project_data, current_user)
```

#### Add Dataset Samples
**Dependency:** `can_add_dataset_samples`

Only administrators can add dataset samples to projects.

```python
from app.core.dependencies import can_add_dataset_samples
from app.models.user import User

@router.post("/projects/{project_id}/samples")
async def add_dataset_samples(
    project_id: uuid.UUID,
    samples: List[DataSampleCreate],
    current_user: User = Depends(can_add_dataset_samples)
):
    # Only admins can reach here
    return add_samples_service(project_id, samples, current_user)
```

#### View Analytics
**Dependency:** `can_view_analytics`

Only administrators can view system analytics and reports.

```python
from app.core.dependencies import can_view_analytics
from app.models.user import User

@router.get("/analytics")
async def get_analytics(
    current_user: User = Depends(can_view_analytics)
):
    # Only admins can reach here
    return get_analytics_service()
```

### Annotator-Only Operations

#### Submit Annotations
**Dependency:** `can_submit_annotations`

Only annotators can submit annotations for data samples.

```python
from app.core.dependencies import can_submit_annotations
from app.models.user import User

@router.post("/samples/{sample_id}/annotations")
async def submit_annotation(
    sample_id: uuid.UUID,
    annotation: AnnotationCreate,
    current_user: User = Depends(can_submit_annotations)
):
    # Only annotators can reach here
    return create_annotation_service(sample_id, annotation, current_user)
```

### Reviewer-Only Operations

#### Review Annotations
**Dependency:** `can_review_annotations`

Only reviewers can review and approve/reject annotations.

```python
from app.core.dependencies import can_review_annotations
from app.models.user import User

@router.post("/annotations/{annotation_id}/reviews")
async def review_annotation(
    annotation_id: uuid.UUID,
    review: ReviewCreate,
    current_user: User = Depends(can_review_annotations)
):
    # Only reviewers can reach here
    return create_review_service(annotation_id, review, current_user)
```

## General Role Dependencies

For more flexible role checking, you can use the general dependencies:

### Require Admin
```python
from app.core.dependencies import require_admin

@router.delete("/admin-only")
async def admin_operation(
    current_user: User = Depends(require_admin)
):
    # Admin only
    pass
```

### Require Reviewer (or Admin)
```python
from app.core.dependencies import require_reviewer

@router.get("/reviews")
async def list_reviews(
    current_user: User = Depends(require_reviewer)
):
    # Reviewer or admin
    pass
```

### Require Annotator (or Reviewer or Admin)
```python
from app.core.dependencies import require_annotator

@router.get("/annotations")
async def list_annotations(
    current_user: User = Depends(require_annotator)
):
    # Annotator, reviewer, or admin
    pass
```

### Custom Role Requirements
```python
from app.core.dependencies import require_roles
from app.models.enums import UserRole

@router.get("/custom")
async def custom_operation(
    current_user: User = Depends(
        require_roles([UserRole.ADMIN, UserRole.REVIEWER])
    )
):
    # Admin or reviewer only
    pass
```

## Error Responses

### 403 Forbidden

When a user attempts an operation they don't have permission for:

```json
{
  "detail": "Only administrators can create projects"
}
```

**Common 403 responses:**
- `"Only administrators can create projects"`
- `"Only administrators can add dataset samples"`
- `"Only administrators can view analytics"`
- `"Only annotators can submit annotations"`
- `"Only reviewers can review annotations"`

## Role Hierarchy

```
Admin
  ├── Can create projects
  ├── Can add dataset samples
  ├── Can view analytics
  ├── Can submit annotations (inherited)
  └── Can review annotations (inherited)

Reviewer
  ├── Can review annotations
  └── Can submit annotations (inherited)

Annotator
  └── Can submit annotations
```

## Usage Examples

### Example 1: Project Creation (Admin Only)

```python
from fastapi import APIRouter, Depends
from app.core.dependencies import can_create_project
from app.models.user import User
from app.schemas.project import ProjectCreate

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", status_code=201)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(can_create_project)
):
    """
    Create a new project.
    Requires admin role.
    """
    # Implementation here
    pass
```

### Example 2: Annotation Submission (Annotator Only)

```python
from fastapi import APIRouter, Depends
from app.core.dependencies import can_submit_annotations
from app.models.user import User
from app.schemas.annotation import AnnotationCreate
import uuid

router = APIRouter(prefix="/annotations", tags=["annotations"])

@router.post("/")
async def submit_annotation(
    sample_id: uuid.UUID,
    annotation: AnnotationCreate,
    current_user: User = Depends(can_submit_annotations)
):
    """
    Submit an annotation for a data sample.
    Requires annotator role.
    """
    # Implementation here
    pass
```

### Example 3: Review Submission (Reviewer Only)

```python
from fastapi import APIRouter, Depends
from app.core.dependencies import can_review_annotations
from app.models.user import User
from app.schemas.review import ReviewCreate
import uuid

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/")
async def submit_review(
    annotation_id: uuid.UUID,
    review: ReviewCreate,
    current_user: User = Depends(can_review_annotations)
):
    """
    Submit a review for an annotation.
    Requires reviewer role.
    """
    # Implementation here
    pass
```

## Best Practices

1. **Use specific dependencies** for operation-specific authorization
2. **Log authorization failures** for security monitoring
3. **Return clear error messages** to help users understand permissions
4. **Test all role combinations** to ensure proper access control
5. **Document role requirements** in API documentation

## Security Considerations

- All authorization checks happen at the dependency level
- Failed authorization attempts are logged for audit purposes
- 403 responses don't reveal sensitive information
- Token validation happens before role checking
- Role information is stored in the JWT token for performance

## Testing Authorization

When testing, ensure:

1. **Admin can access admin-only endpoints**
2. **Annotator cannot access admin-only endpoints** (403)
3. **Reviewer cannot access annotator-only endpoints** (403)
4. **Annotator cannot access reviewer-only endpoints** (403)
5. **Unauthenticated users cannot access any protected endpoints** (401)

Example test:

```python
def test_admin_can_create_project(admin_client):
    response = admin_client.post("/api/projects", json={...})
    assert response.status_code == 201

def test_annotator_cannot_create_project(annotator_client):
    response = annotator_client.post("/api/projects", json={...})
    assert response.status_code == 403
    assert "Only administrators" in response.json()["detail"]
```
