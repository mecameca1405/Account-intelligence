from pydantic import BaseModel
from typing import Optional

class RecommendationBase(BaseModel):
    match_score: Optional[int]
    reasoning: Optional[str]
    is_accepted: Optional[bool]

class RecommendationCreate(RecommendationBase):
    insight_id: int
    product_id: int

class RecommendationUpdate(RecommendationBase):
    pass

class RecommendationRead(RecommendationBase):
    id: int
    product_id: int

    model_config = dict(from_attributes=True)