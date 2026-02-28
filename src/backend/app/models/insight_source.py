from sqlalchemy import Column, Integer, ForeignKey, Text
from ..db.database import Base
from sqlalchemy.orm import relationship

class InsightSource(Base):
    __tablename__ = "insight_sources"

    id = Column(Integer, primary_key=True)
    insight_id = Column(Integer, ForeignKey("insights.id"))
    research_document_id = Column(Integer, ForeignKey("research_documents.id", ondelete="CASCADE"))
    snippet = Column(Text)

    insight = relationship("Insight", back_populates="sources")
    research_document = relationship("ResearchDocument", back_populates="insight_sources")