from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DailyPriorityBase(BaseModel):
    rank_position: int
    reason_short: str

class DailyPriorityCreate(DailyPriorityBase):
    user_id: int
    company_id: int

class DailyPriorityUpdate(BaseModel):
    rank_position: Optional[int]
    reason_short: Optional[str]

class DailyPriorityRead(DailyPriorityBase):
    id: int
    date: datetime
    user_id: int
    company_id: int

    model_config = dict(from_attributes=True)