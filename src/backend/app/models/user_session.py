from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..db.database import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    refresh_token_hash = Column(String, nullable=False, index=True)

    device = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)

    expires_at = Column(DateTime(timezone=True), nullable=False)

    revoked = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    user = relationship("User")