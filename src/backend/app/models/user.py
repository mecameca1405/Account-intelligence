from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from ..db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class User(Base):
    """
    Represents the Sales Representative (HPE Account Manager).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role_id = Column(Integer, ForeignKey("roles.id"))
    region_id = Column(Integer, ForeignKey("regions.id"))  # e.g., 'LATAM', 'NA' for localization
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    role = relationship("UserRole", back_populates="users")
    region = relationship("Region", back_populates="users")
    analyses = relationship("Analysis", back_populates="user")
    daily_priorities = relationship("DailyPriority", back_populates="user")