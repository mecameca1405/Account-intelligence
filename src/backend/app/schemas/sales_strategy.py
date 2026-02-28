from pydantic import BaseModel
from typing import Optional


class SalesStrategyResponse(BaseModel):
    id: int
    status: str
    account_strategic_overview: Optional[str]
    priority_initiatives: Optional[str]
    financial_positioning: Optional[str]
    technical_enablement_summary: Optional[str]
    objection_handling: Optional[str]
    executive_conversation_version: Optional[str]
    email_version: Optional[str]