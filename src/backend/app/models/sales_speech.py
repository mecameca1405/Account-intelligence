from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey, String, JSON
from ..db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class SalesSpeech(Base):
    """
    Stores generated sales scripts. Allows versioning (regenerations).
    """
    __tablename__ = "sales_speeches"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    
    version = Column(Integer, default=1)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Configuration used to generate this speech
    tone = Column(String(50))   # 'Formal', 'Consultative'
    focus_points = Column(JSON) # List of key points emphasized
    
    # Relationships
    analysis = relationship("Analysis", back_populates="speeches")