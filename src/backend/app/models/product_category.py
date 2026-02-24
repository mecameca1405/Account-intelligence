from sqlalchemy import Column, Integer, String, Text
from ..db.database import Base
from sqlalchemy.orm import relationship

class ProductCategory(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    description = Column(Text, nullable=True)

    products = relationship("Product", back_populates="category")