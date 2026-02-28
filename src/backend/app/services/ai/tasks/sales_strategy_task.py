from ....core.celery_app import celery
from ....db.database import sessionLocal
from ..sales_strategy_service import SalesStrategyService
from ....models.analysis import Analysis
from ....models.enums import AnalysisStatus

@celery.task(bind=True)
def run_sales_strategy(self, analysis_id: int):

    async def _run():

        async with sessionLocal() as db:

            service = SalesStrategyService(db)

            await service.generate_for_analysis(analysis_id)

            # Mark analysis as completed
            analysis = await db.get(Analysis, analysis_id)
            analysis.status = AnalysisStatus.COMPLETED
            await db.commit()

    import asyncio
    asyncio.run(_run())