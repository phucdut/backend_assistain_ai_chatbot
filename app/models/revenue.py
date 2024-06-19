from sqlalchemy import Column, ForeignKey, Float, Integer, Date
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Revenue(Base):
    __tablename__ = "revenue"
    subscription_plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    date = Column(Date, nullable=False)
    income = Column(Float, default=0)
    plan = relationship("SubscriptionPlan", back_populates="revenue")