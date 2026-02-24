from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SpeechBase(BaseModel):
    content_text: Optional[str]
    tone: Optional[str]
    focus_points: Optional[List[str]]

class SpeechCreate(SpeechBase):
    analysis_id: int

class SpeechUpdate(SpeechBase):
    pass

class SpeechRead(SpeechBase):
    id: int
    created_at: datetime
    version_number: int

    model_config = dict(from_attributes=True)