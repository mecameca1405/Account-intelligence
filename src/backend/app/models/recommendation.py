from sqlalchemy import Column, Integer, Boolean, Text, ForeignKey
from ..db.database import Base
from sqlalchemy.orm import relationship

class Recommendation(Base):
    """
    Links a detected Insight (Problem) to an HPE Product (Solution).
    """
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    insight_id = Column(Integer, ForeignKey("insights.id"))
    product_id = Column(Integer, ForeignKey("hpe_products.id"))
    
    match_percentage = Column(Integer)  # e.g., 89
    reasoning = Column(Text)            # Why AI selected this product
    
    # User Feedback (Requirement: 'Thumbs up/down')
    is_accepted = Column(Boolean, nullable=True)  # Null=No Action, True=Liked, False=Disliked
    
    # Relationships
    insight = relationship("Insight", back_populates="recommendations")
    product = relationship("HPEProduct", back_populates="recommendations")