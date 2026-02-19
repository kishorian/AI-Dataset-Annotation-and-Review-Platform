from fastapi import HTTPException, status


class AppException(Exception):
    """Base exception for application-specific errors."""
    pass


class NotFoundError(AppException):
    """Raised when a resource is not found."""
    pass


class ConflictError(AppException):
    """Raised when a resource conflict occurs."""
    pass


class UnauthorizedError(AppException):
    """Raised when authentication fails."""
    pass


class ForbiddenError(AppException):
    """Raised when access is forbidden."""
    pass


def handle_app_exception(exc: AppException) -> HTTPException:
    """
    Convert application exceptions to HTTP exceptions.
    """
    if isinstance(exc, NotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc) or "Resource not found"
        )
    elif isinstance(exc, ConflictError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc) or "Resource conflict"
        )
    elif isinstance(exc, UnauthorizedError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc) or "Unauthorized"
        )
    elif isinstance(exc, ForbiddenError):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc) or "Forbidden"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc) or "Internal server error"
        )
