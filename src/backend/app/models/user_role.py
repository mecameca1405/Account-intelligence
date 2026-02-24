from sqlalchemy import Column, Integer, String, Text
from ..db.database import Base
from sqlalchemy.orm import relationship

class UserRole(Base):

    """
    Represents a role.
    
    """

    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(Text, nullable=True)

    # Relationships
    users = relationship("User", back_populates="role_obj")