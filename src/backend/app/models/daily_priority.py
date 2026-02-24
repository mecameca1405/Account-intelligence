from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from ..db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class DailyPriority(Base):
    """
    Stores the pre-calculated 'Top 5 Accounts' for the dashboard.
    Populated by a nightly Cron Job.
    """
    __tablename__ = "daily_priorities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    
    report_date = Column(DateTime(timezone=True), server_default=func.now())
    rank_position = Column(Integer)  # 1 to 5
    reason_short = Column(String(255))  # e.g., "New CTO announced yesterday"
    
    # Relationships
    user = relationship("User", back_populates="daily_priorities")
    company = relationship("Company", back_populates="daily_priorities")