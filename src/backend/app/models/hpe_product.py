from sqlalchemy import Column, Integer, String, Text, ForeignKey
from ..db.database import Base
from sqlalchemy.orm import relationship


class HPEProduct(Base):
    """
    Catalog of HPE Solutions (GreenLake, Alletra, ProLiant, etc.).
    
    """
    __tablename__ = "hpe_products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))  # Compute, Storage, Networking, AI
    description = Column(Text)
    
    # Value proposition used by RAG to match customer pain points
    business_value = Column(Text)   # e.g., "Reduces CapEx by moving to consumption model"
    product_url = Column(String(500))

    # Relationships
    category = relationship("ProductCategory", back_populates="products")
    recommendations = relationship("Recommendation", back_populates="product")