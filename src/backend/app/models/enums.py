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

PROGRESS_MAP = {
    AnalysisStatus.PENDING: 5,
    AnalysisStatus.RESEARCHING: 20,
    AnalysisStatus.INSIGHT_PROCESSING: 40,
    AnalysisStatus.RECOMMENDING: 60,
    AnalysisStatus.STRATEGY_GENERATING: 85,
    AnalysisStatus.COMPLETED: 100,
    AnalysisStatus.FAILED: 100,
}