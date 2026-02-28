from ....core.celery_app import celery
from app.db.database import SyncSessionLocal
from app.models.analysis import Analysis
from app.models.insight import Insight
from app.models.insight_source import InsightSource
from app.models.enums import AnalysisStatus
from app.models.research_document import ResearchDocument

from ....clients.embedding_client import EmbeddingClient
from ....clients.pinecone_client import PineconeClient
from ....clients.llm_client import LLMClient

from pydantic import BaseModel
from typing import List


class InsightItem(BaseModel):
    title: str
    description: str
    category: str
    severity: str
    tech_intensity: int
    operational_complexity: int
    financial_pressure: int


class InsightOutput(BaseModel):
    insights: List[InsightItem]


@celery.task(bind=True)
def run_insights(self, analysis_id: int):

    db = SyncSessionLocal()

    try:
        # ─────────────────────────────────────────────
        # Load analysis
        # ─────────────────────────────────────────────
        analysis = db.get(Analysis, analysis_id)

        if not analysis:
            raise ValueError("Analysis not found")

        namespace = f"analysis_{analysis_id}"

        pinecone = PineconeClient()
        llm = LLMClient()
        embedding = EmbeddingClient()

        # ─────────────────────────────────────────────
        # Representative vector for RAG retrieval
        # ─────────────────────────────────────────────
        query_vector = embedding.embed_text(
            "Strategic company analysis overview"
        )

        matches = pinecone.similarity_search(
            query_vector=query_vector,
            namespace=namespace,
            top_k=8,
        )

        document_ids = [
            int(match["metadata"]["research_document_id"])
            for match in matches
        ]

        # ─────────────────────────────────────────────
        # Fetch raw documents
        # ─────────────────────────────────────────────
        documents = []
        research_documents = []

        for doc_id in document_ids:
            doc = db.get(ResearchDocument, doc_id)
            if doc:
                research_documents.append(doc)
                documents.append((doc.raw_content or "")[:4000])

        context = "\n\n".join(documents)

        prompt = f"""
        You are a strategic B2B AI analyst.

        Based on the following company research context,
        generate maximum 5 strategic insights.

        Each insight must include:
        - title
        - description
        - category
        - severity (low, medium, high)
        - tech_intensity (0-5)
        - operational_complexity (0-5)
        - financial_pressure (0-5)

        Research context:
        {context}
        """

        result = llm.generate_structured_output(
            prompt=prompt,
            output_schema=InsightOutput,
        )

        total_tech = 0
        total_ops = 0
        total_fin = 0

        created_insights = []

        # ─────────────────────────────────────────────
        # Create Insights
        # ─────────────────────────────────────────────
        for item in result.insights:

            insight = Insight(
                analysis_id=analysis_id,
                title=item.title,
                description=item.description,
                category=item.category,
                severity=item.severity,
            )

            db.add(insight)
            created_insights.append(insight)

            total_tech += item.tech_intensity
            total_ops += item.operational_complexity
            total_fin += item.financial_pressure

        # Flush to generate IDs before attaching sources
        db.flush()

        # ─────────────────────────────────────────────
        # Attach Insight Sources
        # ─────────────────────────────────────────────
        for insight in created_insights:
            for doc in research_documents:
                source = InsightSource(
                    insight_id=insight.id,
                    research_document_id=doc.id,
                    snippet=(doc.raw_content or "")[:500],
                )
                db.add(source)

        # ─────────────────────────────────────────────
        # Strategic score calculation
        # ─────────────────────────────────────────────
        strategic_score = min(
            100,
            int((total_tech + total_ops + total_fin) * 100 / 75),
        )

        analysis.strategic_score = strategic_score
        analysis.score_breakdown = {
            "tech_intensity": total_tech,
            "operational_complexity": total_ops,
            "financial_pressure": total_fin,
        }

        analysis.status = AnalysisStatus.RECOMMENDING

        db.commit()

        insight_ids = [insight.id for insight in created_insights]

    except Exception as e:
        analysis = db.get(Analysis, analysis_id)
        if analysis:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            analysis.error_stage = "insight_generation"
            db.commit()
        raise e

    finally:
        db.close()

    # ─────────────────────────────────────────────
    # Trigger recommendation tasks (outside DB session)
    # ─────────────────────────────────────────────
    from app.services.ai.tasks.recommendation_task import run_recommendations

    for insight_id in insight_ids:
        run_recommendations.delay(insight_id)