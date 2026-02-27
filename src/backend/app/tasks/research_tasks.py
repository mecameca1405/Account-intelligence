from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.database import sessionLocal
from ..models.analysis import Analysis
from ..models.company import Company
from ..models.research_document import ResearchDocument
from ..clients.tavily_client import TavilyClient
from ..clients.embedding_client import EmbeddingClient
from ..clients.pinecone_client import PineconeClient
from ..models.enums import AnalysisStatus


@shared_task(bind=True)
def run_research(self, analysis_id: int):

    async def _run():
        async with sessionLocal() as db:  # type: AsyncSession

            # Load analysis + company
            analysis = await db.get(Analysis, analysis_id)
            company = await db.get(Company, analysis.company_id)

            # Update status
            analysis.status = AnalysisStatus.RESEARCHING
            await db.commit()

            tavily = TavilyClient()
            embedding_client = EmbeddingClient()
            pinecone = PineconeClient()

            namespace = f"analysis_{analysis_id}"

            # Strategic queries
            queries = [
                f"{company.name} financial performance 2024",
                f"{company.name} technology stack infrastructure",
                f"{company.name} business strategy challenges news",
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
                    await db.flush()  # get doc.id

                    # Generate embedding
                    vector = embedding_client.embed_text(doc.raw_content)

                    # Upsert to Pinecone
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

            await db.commit()

            # Move to next stage
            analysis.status = AnalysisStatus.INSIGHT_PROCESSING
            await db.commit()

    import asyncio
    asyncio.run(_run())