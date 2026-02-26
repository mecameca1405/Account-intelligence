from celery import Celery
from ..core.config import settings

celery = Celery(
    "eridani_ai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery.conf.update(
    task_track_started=True,
    task_time_limit=60 * 10,  # 10 min hard limit
    task_soft_time_limit=60 * 8,
    worker_max_tasks_per_child=50,
)

celery.autodiscover_tasks(["app.tasks"])