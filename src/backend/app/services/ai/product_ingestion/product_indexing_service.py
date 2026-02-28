import hashlib
from typing import Dict

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from ....models import HPEProduct
from ....clients.embedding_client import EmbeddingClient
from ....clients.pinecone_client import PineconeClient


class ProductIndexingService:
    def __init__(
        self,
        db: Session,
        embedding_client: EmbeddingClient,
        pinecone_client: PineconeClient,
    ):
        self.db = db
        self.embedding_client = embedding_client
        self.pinecone_client = pinecone_client

    # ===============================
    # PUBLIC METHOD
    # ===============================

    def index_all_products(self) -> Dict[str, int]:
        """
        Index products incrementally based on embedding hash.
        Returns summary stats.
        """

        stmt = (
            select(HPEProduct)
            .options(selectinload(HPEProduct.category))
        )

        products = self.db.execute(stmt).scalars().all()

        total = len(products)
        indexed = 0
        skipped = 0

        for product in products:
            try:
                product_text = self._build_product_text(product)
                new_hash = self._compute_hash(product_text)

                if product.embedding_hash == new_hash:
                    skipped += 1
                    continue

                embedding = self.embedding_client.embed_text(product_text)

                self._upsert_vector(product, embedding)

                product.embedding_hash = new_hash
                self.db.commit()

                indexed += 1

            except Exception as e:
                # Don't break all the flow only for one product
                print(f"[ProductIndexingService] Error indexing product {product.id}: {e}")
                self.db.rollback()

        return {
            "total": total,
            "indexed": indexed,
            "skipped": skipped,
        }

    # ===============================
    # INTERNAL HELPERS
    # ===============================

    def _build_product_text(self, product: HPEProduct) -> str:
        category_name = product.category.name if product.category else "Unknown"

        parts = [
            f"Product Name: {product.name}",
            f"Category: {category_name}",
            f"Description: {product.description or ''}",
            f"Business Value: {product.business_value or ''}",
        ]

        return "\n".join(parts)

    def _compute_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _upsert_vector(self, product: HPEProduct, embedding: list[float]) -> None:
        category_name = product.category.name if product.category else "Unknown"

        metadata = {
            "product_id": product.id,
            "name": product.name,
            "category": category_name,
            "is_simulated": product.is_simulated,
        }

        vector_id = f"product-{product.id}"

        self.pinecone_client.upsert_vector(
            vector_id=vector_id,
            values=embedding,
            metadata=metadata,
            namespace="products",
        )