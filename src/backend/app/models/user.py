from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
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
    role_id = Column(Integer, ForeignKey("roles.id"), default=3)
    region_id = Column(Integer, ForeignKey("regions.id"))  # e.g., 'LATAM', 'NA' for localization
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    updated_by = Column(Integer, nullable=True)
    token_version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    role = relationship("UserRole", back_populates="users", lazy="selectin")
    region = relationship("Region", back_populates="users")
    analyses = relationship("Analysis", back_populates="user")
    daily_priorities = relationship("DailyPriority", back_populates="user")