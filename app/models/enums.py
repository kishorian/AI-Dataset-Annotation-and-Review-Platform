import enum


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    ANNOTATOR = "annotator"
    REVIEWER = "reviewer"


class SampleStatus(str, enum.Enum):
    """Data sample status enumeration."""
    PENDING = "pending"
    ANNOTATED = "annotated"
    REVIEWED = "reviewed"


class AnnotationLabel(str, enum.Enum):
    """Annotation label enumeration."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ReviewDecision(str, enum.Enum):
    """Review decision enumeration."""
    APPROVED = "approved"
    REJECTED = "rejected"
