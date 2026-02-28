import logging
from ....core.celery_app import celery
from app.db.database import SyncSessionLocal
from ..recommendation_service import RecommendationService

logger = logging.getLogger(__name__)


@celery.task(bind=True)
def run_recommendations(self, insight_id: int):

    logger.info(f"[Task] run_recommendations triggered for insight_id={insight_id}")

    db = SyncSessionLocal()

    try:
        service = RecommendationService(db)
        service.generate_for_insight(insight_id)

        db.commit()

    except Exception as e:
        db.rollback()
        logger.exception(
            f"[Task] run_recommendations failed for insight_id={insight_id}"
        )
        raise e

    finally:
        db.close()

    logger.info(f"[Task] run_recommendations finished for insight_id={insight_id}")