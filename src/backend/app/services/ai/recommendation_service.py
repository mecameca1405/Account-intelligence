import logging
from sqlalchemy import delete
from ...models.insight import Insight
from ...models.recommendation import Recommendation
from ...models.hpe_product import HPEProduct
from ...clients.embedding_client import EmbeddingClient
from ...clients.pinecone_client import PineconeClient
from ...clients.llm_client import LLMClient
# =========================
# LLM Structured Output
# =========================
from ...schemas.ranking import RankedProduct, RankingOutput


logger = logging.getLogger(__name__)


# =========================
# Recommendation Service
# =========================

class RecommendationService:

    def __init__(self, db):
        self.db = db
        self.embedding_client = EmbeddingClient()
        self.pinecone_client = PineconeClient()
        self.llm_client = LLMClient()

    def generate_for_insight(self, insight_id: int, top_k: int = 3):

        logger.info(f"[Recommendation] Starting for insight_id={insight_id}")

        insight = self.db.get(Insight, insight_id)

        if not insight:
            logger.error(f"[Recommendation] Insight {insight_id} not found")
            raise ValueError("Insight not found")

        logger.info(
            f"[Recommendation] Insight title='{insight.title}' severity='{insight.severity}'"
        )

        # --------------------------------------------------
        # Delete previous recommendations (idempotent behavior)
        # --------------------------------------------------
        self.db.execute(
            delete(Recommendation).where(
                Recommendation.insight_id == insight_id
            )
        )

        logger.info(f"[Recommendation] Cleared previous recommendations")

        query_text = f"{insight.title}. {insight.description}"

        # --------------------------------------------------
        # Semantic Retrieval (Recall Layer)
        # --------------------------------------------------
        query_vector = self.embedding_client.embed_text(query_text)

        matches = self.pinecone_client.similarity_search(
            query_vector=query_vector,
            namespace="products",
            top_k=top_k
        )

        logger.info(f"[Recommendation] Pinecone returned {len(matches)} matches")

        # Collect candidate products
        candidates = []

        for match in matches:
            product_id = int(match["metadata"]["product_id"])
            semantic_score = float(match["score"])

            product = self.db.get(HPEProduct, product_id)
            if not product:
                logger.warning(
                    f"[Recommendation] Skipping product_id={product_id} (not found in DB)"
                )
                continue

            candidates.append({
                "product": product,
                "semantic_score": semantic_score
            })

        if not candidates:
            logger.warning("[Recommendation] No valid candidates found")
            return

        # --------------------------------------------------
        # LLM Re-Ranking (Decision Layer)
        # --------------------------------------------------

        products_context = "\n\n".join([
            f"""
            Product ID: {c['product'].id}
            Name: {c['product'].name}
            Category ID: {c['product'].category_id}
            Description: {c['product'].description}
            """
            for c in candidates
        ])

        prompt = f"""
        You are an enterprise AI strategist.

        Rank the following products by strategic alignment with the insight.

        Return:
        - product_id
        - strategic_score (0-100)
        - reasoning

        Insight:
        Title: {insight.title}
        Description: {insight.description}
        Severity: {insight.severity}

        Candidate products:
        {products_context}
        """

        try:
            ranking_result = self.llm_client.generate_structured_output(
                prompt=prompt,
                output_schema=RankingOutput
            )
        except Exception:
            logger.warning("LLM quota exceeded — falling back to semantic ranking")
            ranking_result = None

        # --------------------------------------------------
        # Hybrid Scoring
        # --------------------------------------------------
        # Final Score = 
        # 0.5 * semantic_score +
        # 0.4 * llm_score +
        # 0.1 * financial_weight_adjustment
        # --------------------------------------------------

        severity_multiplier = {
            "low": 1.0,
            "medium": 1.1,
            "high": 1.25
        }.get(insight.severity.lower(), 1.0)

        for rank_position, item in enumerate(ranking_result.ranked_products, start=1):

            product = self.db.get(HPEProduct, item.product_id)
            if not product:
                continue

            # Find semantic score
            semantic_score = next(
                c["semantic_score"]
                for c in candidates
                if c["product"].id == item.product_id
            )

            llm_score = item.strategic_score / 100

            # --- Financial Weighting (Example: AI & Infrastructure prioritized) ---
            financial_weight = 1.0
            if product.category_id in [1, 5]:  # Example: Cloud & AI
                financial_weight = 1.1

            # --- Category misalignment penalty ---
            category_penalty = 1.0
            if insight.severity.lower() == "high" and product.category_id == 4:
                # Example: networking less aligned to strategic AI insights
                category_penalty = 0.9

            # Hybrid score calculation
            hybrid_score = (
                (0.5 * semantic_score) +
                (0.4 * llm_score) +
                (0.1 * financial_weight)
            )

            # Apply severity boost
            hybrid_score *= severity_multiplier

            # Apply category penalty
            hybrid_score *= category_penalty

            final_percentage = min(100, int(hybrid_score * 100))

            recommendation = Recommendation(
                insight_id=insight_id,
                product_id=product.id,
                match_percentage=final_percentage,
                reasoning=item.reasoning,
                confidence_score=hybrid_score,
                llm_rank_position=rank_position
            )

            self.db.add(recommendation)

            logger.info(
                f"[Recommendation] Final score for product_id={product.id} "
                f"= {final_percentage}% (rank {rank_position})"
            )

        logger.info(f"[Recommendation] Completed for insight_id={insight_id}")