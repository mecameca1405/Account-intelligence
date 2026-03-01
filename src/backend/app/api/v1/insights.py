from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from ...models.insight import Insight
from ...models.analysis import Analysis
from ...schemas.insight import InsightResponse
from ...dependencies.deps import get_db
from ...dependencies.deps_auth import get_current_user
from ...models.user import User

api_router = APIRouter()


@api_router.get("/", response_model=List[InsightResponse])
async def list_user_insights(
    company_id: Optional[int] = Query(None),
    severity: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    query = (
        select(Insight)
        .join(Analysis)
        .where(Analysis.user_id == current_user.id)
    )

    if company_id:
        query = query.where(Analysis.company_id == company_id)

    if severity:
        query = query.where(Insight.severity == severity)

    result = await db.execute(query)
    insights = result.scalars().all()

    return insights