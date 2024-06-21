from abc import ABC, abstractmethod
import traceback
import uuid
from uuid import UUID
from typing import Optional, List
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user_subscription_plan import UserSubscriptionPlan
from app.common.logger import setup_logger
from app.crud.crud_revenue import crud_revenue
from app.schemas.revenue import *
from app.services.abc.user_session_service import UserSessionService
from datetime import date
from sqlalchemy import Column, ForeignKey, Float, Integer, Date
from sqlalchemy.orm import Session

from uuid import UUID


class RevenueService(ABC):
    @abstractmethod
    def create(self, db: Session, revenue_create: RevenueCreate) -> RevenueOut:
        pass

    @abstractmethod
    def update_revenue_by_plan(self, db: Session, subscription_plan_id: uuid.UUID, revenue_update: RevenueUpdate) -> RevenueOut:
        pass

    @abstractmethod
    def get_one_with_filter_or_none(self, db: Session, filter: dict) -> Optional[RevenueOut]:
        pass

    # @abstractmethod
    # def get_all_or_none(self, db: Session):
    #     pass
