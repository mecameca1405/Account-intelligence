from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from ...dependencies.deps import get_db
from ...dependencies.deps_auth import get_current_user
from ...models.user import User
from ...models.analysis import Analysis
from ...models.company import Company
from ...schemas.dashboard import TopCompanyResponse, DashboardSummaryResponse
from ...services.ai.daily_prioritization_service import DailyPrioritizationService
from ...models.enums import AnalysisStatus
from typing import List

api_router = APIRouter()


@api_router.get("/top-accounts", response_model=List[TopCompanyResponse])
async def get_top_accounts(
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    result = await db.execute(
        select(Analysis)
        .where(
            Analysis.status == AnalysisStatus.COMPLETED,
            Analysis.user_id == current_user.id
        )
    )

    analyses = result.scalars().all()

    service = DailyPrioritizationService(db)
    ranked = await service.generate_daily_top(analyses, limit)

    company_ids = [item["company_id"] for item in ranked]

    if not company_ids:
        return []

    companies_result = await db.execute(
        select(Company)
        .options(
            joinedload(Company.industry)
        )
        .where(Company.id.in_(company_ids))
    )

    companies = {c.id: c for c in companies_result.scalars().all()}

    response = []

    for item in ranked:
        company = companies.get(item["company_id"])

        response.append(
            TopCompanyResponse(
                analysis_id=item["analysis_id"],
                company_id=item["company_id"],
                company_name=company.name if company else None,
                industry=company.industry.name if company and company.industry else None,
                score=round(item["daily_score"], 2)
            )
        )

    return response


@api_router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    prioritized_result = await db.execute(
        select(func.count(Analysis.id))
        .where(
            Analysis.status == AnalysisStatus.COMPLETED,
            Analysis.user_id == current_user.id
        )
    )

    prioritized_companies = prioritized_result.scalar() or 0

    total_result = await db.execute(
        select(func.count(Analysis.id))
        .where(Analysis.user_id == current_user.id)
    )

    total_analyses = total_result.scalar() or 0

    return DashboardSummaryResponse(
        prioritized_companies=prioritized_companies,
        total_analyses=total_analyses
    )