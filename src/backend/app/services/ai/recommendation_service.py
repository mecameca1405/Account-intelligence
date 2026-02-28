import logging
from sqlalchemy import delete
from ...models.insight import Insight
from ...models.recommendation import Recommendation
from ...models.hpe_product import HPEProduct
from ...clients.embedding_client import EmbeddingClient
from ...clients.pinecone_client import PineconeClient

logger = logging.getLogger(__name__)


class RecommendationService:

    def __init__(self, db):
        self.db = db
        self.embedding_client = EmbeddingClient()
        self.pinecone_client = PineconeClient()

    def generate_for_insight(self, insight_id: int, top_k: int = 3):

        logger.info(f"[Recommendation] Starting for insight_id={insight_id}")

        insight = self.db.get(Insight, insight_id)

        if not insight:
            logger.error(f"[Recommendation] Insight {insight_id} not found")
            raise ValueError("Insight not found")

        logger.info(
            f"[Recommendation] Insight title='{insight.title}' severity='{insight.severity}'"
        )

        # Delete previous recommendations
        self.db.execute(
            delete(Recommendation).where(
                Recommendation.insight_id == insight_id
            )
        )

        logger.info(f"[Recommendation] Cleared previous recommendations")

        query_text = f"{insight.title}. {insight.description}"

        # Embedding
        query_vector = self.embedding_client.embed_text(query_text)

        # Semantic search
        matches = self.pinecone_client.similarity_search(
            query_vector=query_vector,
            namespace="products",
            top_k=top_k
        )

        logger.info(f"[Recommendation] Pinecone returned {len(matches)} matches")

        for match in matches:
            product_id = int(match["metadata"]["product_id"])
            product_name = match["metadata"].get("name")
            score = match["score"]

            logger.info(
                f"[Recommendation] Match -> product='{product_name}' "
                f"product_id={product_id} score={round(score, 4)}"
            )

            # Defensive FK validation
            product = self.db.get(HPEProduct, product_id)
            if not product:
                logger.warning(
                    f"[Recommendation] Skipping product_id={product_id} "
                    f"(not found in DB)"
                )
                continue

            recommendation = Recommendation(
                insight_id=insight_id,
                product_id=product_id,
                match_percentage=int(score * 100),
                reasoning=(
                    f"Semantic similarity match ({round(score, 2)}) "
                    f"between insight and product value proposition."
                ),
                confidence_score=score
            )

            self.db.add(recommendation)

        logger.info(f"[Recommendation] Completed for insight_id={insight_id}")