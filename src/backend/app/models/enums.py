# ==============================================================================
# ENUMS (for strict typing)
# ==============================================================================
import enum


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class InsightSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    RESEARCHING = "researching"
    INSIGHT_PROCESSING = "insight_processing"
    RECOMMENDING = "recommending"
    ANALYSIS_COMPLETED = "analysis_completed"
    STRATEGY_GENERATING = "strategy_generating"
    COMPLETED = "completed"
    FAILED = "failed"