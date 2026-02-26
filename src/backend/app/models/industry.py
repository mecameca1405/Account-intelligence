from sqlalchemy import Column, Integer, String, Text
from ..db.database import Base
from sqlalchemy.orm import relationship


class Industry(Base):
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    companies = relationship("Company", back_populates="industry")