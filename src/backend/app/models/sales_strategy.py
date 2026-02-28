from sqlalchemy import Column, Integer, ForeignKey, Text, String, DateTime, Boolean
from sqlalchemy.sql import func
from ..db.database import Base
from sqlalchemy.orm import relationship


class SalesStrategy(Base):
    __tablename__ = "sales_strategies"

    id = Column(Integer, primary_key=True)

    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, unique=True)

    status = Column(String, default="generated")  # draft | generated | finalized

    # Structured sections
    account_strategic_overview = Column(Text)
    priority_initiatives = Column(Text)  # JSON string
    financial_positioning = Column(Text)
    technical_enablement_summary = Column(Text)
    objection_handling = Column(Text)  # JSON string
    strategic_roadmap_90_days = Column(Text)
    executive_closing_statement = Column(Text)
    executive_conversation_version = Column(Text)

    email_version = Column(Text)

    generated_by_llm = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    analysis = relationship("Analysis", back_populates="sales_strategy")