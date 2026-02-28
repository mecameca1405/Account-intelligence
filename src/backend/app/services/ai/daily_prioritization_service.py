import logging
from sqlalchemy import select, func
from ...models.insight import Insight
from ...models.recommendation import Recommendation

logger = logging.getLogger(__name__)


class DailyPrioritizationService:

    def __init__(self, db):
        self.db = db  # AsyncSession

    async def generate_daily_top(self, analyses, limit: int = 5):

        ranked_companies = []

        for analysis in analyses:

            highest_severity_weight = await self._get_highest_severity_weight(analysis.id)
            max_recommendation_confidence = await self._get_max_recommendation_confidence(analysis.id)

            daily_score = (
                0.35 * (analysis.strategic_score or 0) +
                0.25 * (analysis.propensity_score or 0) +
                0.25 * highest_severity_weight +
                0.15 * max_recommendation_confidence
            )

            ranked_companies.append({
                "analysis_id": analysis.id,
                "company_id": analysis.company_id,
                "daily_score": round(daily_score, 4)
            })

        ranked_companies.sort(
            key=lambda x: x["daily_score"],
            reverse=True
        )

        return ranked_companies[:limit]

    async def _get_highest_severity_weight(self, analysis_id: int):

        severity_map = {
            "high": 1.25,
            "medium": 1.1,
            "low": 1.0
        }

        result = await self.db.execute(
            select(Insight.severity)
            .where(Insight.analysis_id == analysis_id)
        )

        severities = result.scalars().all()

        if not severities:
            return 1.0

        return max(
            severity_map.get(sev.lower(), 1.0)
            for sev in severities
        )

    async def _get_max_recommendation_confidence(self, analysis_id: int):

        result = await self.db.execute(
            select(func.max(Recommendation.confidence_score))
            .join(Insight, Recommendation.insight_id == Insight.id)
            .where(Insight.analysis_id == analysis_id)
        )

        value = result.scalar()
        return value or 0