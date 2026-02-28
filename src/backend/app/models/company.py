from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from ..db.database import Base
from sqlalchemy.orm import relationship

class Company(Base):
    """
    Represents the target account/company being analyzed.
    """
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True, nullable=False)
    domain = Column(String(100), index=True, nullable=True)  # e.g., 'kavak.com'
    industry_id = Column(Integer, ForeignKey("industries.id"))
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    website_url = Column(String, nullable=True)
    last_research_at = Column(DateTime(timezone=True), nullable=True)
    
    # Flag to distinguish real data from simulated data (Project Requirement 9.2)
    is_simulated = Column(Boolean, default=False)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="company")
    industry = relationship("Industry", back_populates="companies")
    daily_priorities = relationship("DailyPriority", back_populates="company")