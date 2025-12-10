import enum


class JobStatus(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    COMPLETED_W_E = "COMPLETED_WITH_ERRORS"
    FAILED = "FAILED"
    READY = "READY"
    MISSING_AD = "MISSING_AD"
