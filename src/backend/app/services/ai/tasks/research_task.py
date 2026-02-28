from ....core.celery_app import celery
from ....db.database import SyncSessionLocal
from ....models.analysis import Analysis
from ....models.company import Company
from ....models.research_document import ResearchDocument
from ....clients.tavily_client import TavilyClient
from ....clients.embedding_client import EmbeddingClient
from ....clients.pinecone_client import PineconeClient
from ....models.enums import AnalysisStatus
from .insight_task import run_insights

@celery.task(bind=True)
def run_research(self, analysis_id: int):

    db = SyncSessionLocal()

    try:
        # ─────────────────────────────────────────────
        # Load analysis + company
        # ─────────────────────────────────────────────
        analysis = db.get(Analysis, analysis_id)

        if not analysis:
            return

        company = db.get(Company, analysis.company_id)

        if not company:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = "Company not found"
            db.commit()
            return

        # ─────────────────────────────────────────────
        # Update status → RESEARCHING
        # ─────────────────────────────────────────────
        analysis.status = AnalysisStatus.RESEARCHING
        db.commit()

        tavily = TavilyClient()
        embedding_client = EmbeddingClient()
        pinecone = PineconeClient()

        namespace = f"analysis_{analysis_id}"

        # ─────────────────────────────────────────────
        # Strategic queries
        # ─────────────────────────────────────────────
        if company.website_url:
            base_query = f"site:{company.website_url}"
        else:
            base_query = company.name
        
        queries = [
            f"{base_query} financial performance 2024",
            f"{base_query} technology stack infrastructure",
            f"{base_query} business strategy challenges news",
        ]

        for query in queries:

            results = tavily.search(query=query, max_results=3)

            for result in results:

                doc = ResearchDocument(
                    analysis_id=analysis_id,
                    title=result.get("title"),
                    source_url=result.get("url"),
                    raw_content=result.get("raw_content") or result.get("content"),
                )

                db.add(doc)
                db.flush()  # get doc.id without full commit

                # ─────────────────────────────────────────────
                # Generate embedding (truncate to reduce quota usage)
                # ─────────────────────────────────────────────
                text_for_embedding = (doc.raw_content or "")[:1500]

                if text_for_embedding.strip():
                    vector = embedding_client.embed_text(text_for_embedding)

                    # ─────────────────────────────────────────────
                    # Upsert to Pinecone
                    # ─────────────────────────────────────────────
                    pinecone.upsert_vector(
                        vector_id=str(doc.id),
                        values=vector,
                        metadata={
                            "research_document_id": doc.id,
                            "analysis_id": analysis_id,
                            "source_url": doc.source_url,
                        },
                        namespace=namespace,
                    )

        db.commit()

        # ─────────────────────────────────────────────
        # Move to next stage → INSIGHT_PROCESSING
        # ─────────────────────────────────────────────
        analysis.status = AnalysisStatus.INSIGHT_PROCESSING
        db.commit()

        run_insights.delay(analysis.id)

    except Exception as e:
        # ─────────────────────────────────────────────
        # Failure handling (important for production)
        # ─────────────────────────────────────────────
        analysis = db.get(Analysis, analysis_id)
        if analysis:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            analysis.error_stage = "research"
            db.commit()
        raise e

    finally:
        db.close()