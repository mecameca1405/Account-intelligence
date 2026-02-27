from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from ..db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .enums import AnalysisStatus


class Analysis(Base):
    """
    The core fact table. Stores the result of an AI analysis session.
    """
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    status = Column(String(50), default=AnalysisStatus.PENDING)

    # --- AI Generated Scores ---
    strategic_score = Column(Integer, default=0)   # 0-100 (Overall health)
    propensity_score = Column(Integer, default=0)  # 0-100 (Likelihood to buy)
    
    # Stores the breakdown graph data
    # Structure: {"tech_intensity": 80, "operational_complexity": 60}
    score_breakdown = Column(JSON, nullable=True)

    # --- 360 Profile Summaries (Generated via RAG/Tavily) ---
    summary_financial = Column(Text, nullable=True)
    summary_tech_stack = Column(Text, nullable=True)
    summary_strategy = Column(Text, nullable=True)

    celery_task_id = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    
    error_stage = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="analyses")
    company = relationship("Company", back_populates="analyses")
    insights = relationship("Insight", back_populates="analysis", cascade="all, delete-orphan")
    speeches = relationship("SalesSpeech", back_populates="analysis", cascade="all, delete-orphan")
    research_documents = relationship("ResearchDocument", back_populates="analysis", cascade="all, delete-orphan")