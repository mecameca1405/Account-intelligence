from pydantic import BaseModel


class TopCompanyResponse(BaseModel):
    analysis_id: int
    company_id: int
    company_name: str | None = None
    industry: str | None = None
    score: float


class DashboardSummaryResponse(BaseModel):
    prioritized_companies: int
    total_analyses: int