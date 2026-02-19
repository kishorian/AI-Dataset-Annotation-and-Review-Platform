from app.core.logging import logger
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    verify_token,
    validate_password_strength
)
from app.core.dependencies import (
    get_current_user,
    get_current_active_user,
    require_admin,
    require_reviewer,
    require_annotator,
    require_roles,
    can_create_project,
    can_add_dataset_samples,
    can_view_analytics,
    can_submit_annotations,
    can_review_annotations
)
from app.core.exceptions import (
    AppException,
    NotFoundError,
    ConflictError,
    UnauthorizedError,
    ForbiddenError,
    handle_app_exception
)

__all__ = [
    "logger",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
    "verify_token",
    "validate_password_strength",
    "get_current_user",
    "get_current_active_user",
    "require_admin",
    "require_reviewer",
    "require_annotator",
    "require_roles",
    "can_create_project",
    "can_add_dataset_samples",
    "can_view_analytics",
    "can_submit_annotations",
    "can_review_annotations",
    "AppException",
    "NotFoundError",
    "ConflictError",
    "UnauthorizedError",
    "ForbiddenError",
    "handle_app_exception",
]
