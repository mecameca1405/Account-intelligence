from sqlalchemy import Column, Integer, String, Text, ForeignKey
from ..db.database import Base
from sqlalchemy.orm import relationship
from .enums import InsightSeverity

class Insight(Base):
    """
    Specific findings detected by the AI (e.g., 'Cloud Migration Detected').
    """
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100))  # Finance, Operations, Security
    severity = Column(String(50), default=InsightSeverity.MEDIUM)
    
    # Source attribution (Critical for 'Explainable AI')
    source_url = Column(String(500), nullable=True)
    source_snippet = Column(Text, nullable=True)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="insights")
    recommendations = relationship("Recommendation", back_populates="insight", cascade="all, delete-orphan")