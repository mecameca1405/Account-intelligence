from ....core.celery_app import celery

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.core.config import settings
from app.services.ai.product_ingestion.product_indexing_service import (
    ProductIndexingService,
)
from app.clients.embedding_client import EmbeddingClient
from app.clients.pinecone_client import PineconeClient


@celery.task(bind=True)
def run_product_index(self):
    """
    Celery task to index all products incrementally in Pinecone.
    """

    print("[ProductIndexTask] Starting product indexing...")

    # We use Celery worker (sync context).
    # A sync session is needed.

    # As our engine is an async engine,
    # we need to initialize a sync one for Celery.

    sync_engine = create_engine(
        settings.DATABASE_URL.replace("+asyncpg", ""),
        pool_pre_ping=True,
    )

    SessionLocal = sessionmaker(bind=sync_engine)

    db = SessionLocal()

    try:
        embedding_client = EmbeddingClient()
        pinecone_client = PineconeClient()

        service = ProductIndexingService(
            db=db,
            embedding_client=embedding_client,
            pinecone_client=pinecone_client,
        )

        result = service.index_all_products()

        print(f"[ProductIndexTask] Finished indexing: {result}")

        return result

    except Exception as e:
        print(f"[ProductIndexTask] Failed: {e}")
        raise e

    finally:
        db.close()