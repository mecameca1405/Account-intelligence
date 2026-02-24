from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
from .insight import InsightRead
from .speech import SpeechRead

class AnalysisBase(BaseModel):
    status: Optional[str] = "processing"
    strategic_score: Optional[int]
    propensity_score: Optional[int]
    score_breakdown: Optional[Dict]
    summary_financial: Optional[str]
    summary_tech_stack: Optional[str]
    summary_strategy: Optional[str]

class AnalysisCreate(AnalysisBase):
    user_id: int
    company_id: int

class AnalysisUpdate(AnalysisBase):
    pass

class AnalysisRead(AnalysisBase):
    id: int
    user_id: int
    company_id: int
    created_at: datetime
    insights: List[InsightRead] = []
    speeches: List[SpeechRead] = []

    model_config = dict(from_attributes=True)