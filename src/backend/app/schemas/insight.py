from pydantic import BaseModel
from typing import Optional, List
from .recommendation import RecommendationRead

class InsightBase(BaseModel):
    title: str
    description: Optional[str]
    category: Optional[str]
    severity: Optional[str]
    source_url: Optional[str]
    source_snippet: Optional[str]

class InsightCreate(InsightBase):
    analysis_id: int

class InsightUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    category: Optional[str]
    severity: Optional[str]
    source_url: Optional[str]
    source_snippet: Optional[str]

class InsightRead(InsightBase):
    id: int
    recommendations: List[RecommendationRead] = []

    model_config = dict(from_attributes=True)




class InsightItem(BaseModel):
    title: str
    description: str
    category: str
    severity: str
    tech_intensity: int
    operational_complexity: int
    financial_pressure: int


class InsightOutput(BaseModel):
    insights: List[InsightItem]