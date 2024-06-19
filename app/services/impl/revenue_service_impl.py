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
from app.services.impl.user_session_service_impl import UserSessionServiceImpl
from app.services.abc.revenue_service import RevenueService
from datetime import date
from sqlalchemy import Column, ForeignKey, Float, Integer, Date
logger = setup_logger()


class RevenueServiceImpl(RevenueService):

    def __init__(self):
        self.__crud_revenue = crud_revenue
        self.__user_session_service : UserSessionService = UserSessionServiceImpl()


    def create(self, db: Session, revenue_create: RevenueCreate) -> RevenueOut:
        try:
            return self.__crud_revenue.create(db, obj_in=revenue_create)
        except:
            traceback.print_exc()
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.create_record: Invalid token: "
            ),
            raise HTTPException(
                detail="Create Record failed: Invalid token", status_code=401
            )

    def update_revenue_by_plan(
        self, db: Session, subscription_plan_id: uuid.UUID, revenue_update: RevenueUpdate
    ) -> RevenueOut:
        try:
            # Check for current record
            today = date.today()
            revenue = self.get_one_with_filter_or_none(db=db, filter={'subscription_plan_id': subscription_plan_id, 'date': today})
            if revenue:
                if revenue_update.income:
                    revenue_update.income += revenue.income
                revenue_updated = self.__crud_revenue.update_one_by(
                    db=db, filter={'subscription_plan_id': subscription_plan_id, 'date': today}, obj_in=revenue_update
                )
            else:
                # Create record and update
                revenue_create = RevenueCreate(subscription_plan_id=subscription_plan_id, date=today)
                revenue_created = self.create(db=db, revenue_create=revenue_create)
                if revenue_created:
                    revenue_updated = self.__crud_revenue.update_one_by(
                        db=db, filter={'subscription_plan_id': subscription_plan_id, 'date': today}, obj_in=revenue_update
                    )
        except Exception as subscription_plan_exec:
            logger.error(
                f"Error in {__name__}.{self.__class__.__name__}.update_one_with_filter: {subscription_plan_exec}"
            )
            raise subscription_plan_exec
        if revenue_updated:
            result: RevenueOut = RevenueOut(
                **revenue_updated.__dict__
            )
        return result


    def get_one_with_filter_or_none(self, db: Session, filter: dict) -> Optional[RevenueOut]:
        try:
            return self.__crud_revenue.get_one_by(db=db, filter=filter)
        except:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.get_one_with_filter_or_none"
            )
            return None


    # def get_all_or_none(self, db: Session):
    #     try:
    #         from app.services.impl.subscription_plan_service_impl import SubscriptionPlanServiceImpl
    #         subscription_plan_service = SubscriptionPlanServiceImpl()
    #         subscription_plans = subscription_plan_service.get_all(db=db)
    #         if subscription_plans:
    #             results = []
    #             for plan in subscription_plans:
    #                 record_data = []
    #                 records = self.__crud_revenue.get_revenue_by_plan_id(db=db, subscription_plan_id=plan.id)
    #                 plan_revenue = 0
    #                 if records:
    #                     for record in records:
    #                         _record = {
    #                             'date': record.date,
    #                             'income': record.income
    #                         }
    #                         plan_revenue += record.income
    #                         record_data.append(_record)
    #                 from app.services.impl.subscription_plan_service_impl import SubscriptionPlanServiceImpl
    #                 subscription_plan_service = SubscriptionPlanServiceImpl()
    #                 plan_info = subscription_plan_service.get_one_with_filter_or_none(db=db, filter={"id": plan.id})
    #                 result = {
    #                     'plan_id': plan.id,
    #                     'plan_title': plan_info.plan_title,
    #                     'plan_revenue': plan_revenue,
    #                     'data': record_data
    #                 }
    #                 results.append(result)
    #             return results
    #         return None
    #     except:
    #         logger.exception(
    #             f"Exception in {__name__}.{self.__class__.__name__}.get_all_or_none"
    #         )
    #         return None

