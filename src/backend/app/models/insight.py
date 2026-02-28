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
    card_size = Column(String)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="insights")
    recommendations = relationship("Recommendation", back_populates="insight", cascade="all, delete-orphan")
    sources = relationship("InsightSource", back_populates="insight", cascade="all, delete-orphan")