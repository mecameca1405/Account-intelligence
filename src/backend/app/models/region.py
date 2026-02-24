from sqlalchemy import Column, Integer, String
from ..db.database import Base
from sqlalchemy.orm import relationship

class Region(Base):

    """
    Represents a world region.
    """

    __tablename__ = "regions"
    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True)   # LATAM, NA, etc.
    name = Column(String(100))               # Latin America, North America

    # Relationships
    users = relationship("User", back_populates="region_obj")