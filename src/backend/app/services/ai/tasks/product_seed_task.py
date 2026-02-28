from ....core.celery_app import celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ....core.config import settings
from ....services.ai.product_ingestion.product_seed_service import (
    ProductSeedService,
)


@celery.task(bind=True)
def run_product_seed(self):
    print("[ProductSeedTask] Starting product seed...")

    sync_engine = create_engine(
        settings.DATABASE_URL.replace("+asyncpg", ""),
        pool_pre_ping=True,
    )

    SessionLocal = sessionmaker(bind=sync_engine)
    db = SessionLocal()

    try:
        service = ProductSeedService(db=db)
        result = service.seed_products()

        print(f"[ProductSeedTask] Result: {result}")
        return result

    except Exception as e:
        print(f"[ProductSeedTask] Failed: {e}")
        raise e

    finally:
        db.close()