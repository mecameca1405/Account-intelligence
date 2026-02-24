from sqlalchemy import Column, Integer, String, Boolean, Text
from ..db.database import Base
from sqlalchemy.orm import relationship

class Company(Base):
    """
    Represents the target account/company being analyzed.
    """
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True, nullable=False)
    domain = Column(String(100), index=True)  # e.g., 'kavak.com'
    industry = Column(String(100))            # e.g., 'Fintech', 'Retail'
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # Flag to distinguish real data from simulated data (Project Requirement 9.2)
    is_simulated = Column(Boolean, default=False)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="company")
    daily_priorities = relationship("DailyPriority", back_populates="company")