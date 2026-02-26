from app.core.celery_app import celery
from app.core.celery_utils import run_async_task
from app.services.ai.research_service import ResearchService


@celery.task(bind=True)
def run_research_task(self, analysis_id: int):

    self.update_state(state="PROGRESS", meta={"progress": 10})

    service = ResearchService(self)

    return run_async_task(service.execute(analysis_id))