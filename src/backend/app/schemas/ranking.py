from pydantic import BaseModel
from typing import List

class RankedProduct(BaseModel):
    product_id: int
    strategic_score: int
    reasoning: str

class RankingOutput(BaseModel):
    ranked_products: List[RankedProduct]