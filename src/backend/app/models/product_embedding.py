from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from ..db.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class ProductEmbedding(Base):
    __tablename__ = "product_embeddings"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("hpe_products.id"))

    embedding_id = Column(String(255))
    version = Column(Integer, default=1)

    content_hash = Column(String(64))
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("HPEProduct", back_populates="embeddings")