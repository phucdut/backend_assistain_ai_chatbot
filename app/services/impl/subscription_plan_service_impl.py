from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse



from app.common.logger import setup_logger
from app.schemas.user_subscription_plan import UserSubscriptionPlan
from app.crud.crud_subscription_plan import crud_subscription_plan
from app.schemas.subscription_plan import (SubscriptionPlanCreate,
                                           SubscriptionPlanOut,
                                           SubscriptionPlanUpdate)
from app.services.abc.subscription_plan_service import SubscriptionPlanService

logger = setup_logger()


class SubscriptionPlanServiceImpl(SubscriptionPlanService):

    def __init__(self):
        self.__crud_subscription_plan = crud_subscription_plan

    def create(
        self, db: Session, subscription_plan_create: SubscriptionPlanCreate
    ) -> SubscriptionPlanOut:
        subscription_plan_found = self.get_one_with_filter_or_none(
            db=db, filter={"plan_title": subscription_plan_create.plan_title}
        )
        if subscription_plan_found is not None:
            return subscription_plan_found
        try:
            subscription_plan_created = self.__crud_subscription_plan.create(
                db=db, obj_in=subscription_plan_create
            )
        except Exception as subscription_plan_exec:
            logger.error(
                f"Error in {__name__}.{self.__class__.__name__}.create: {subscription_plan_exec}"
            )
            raise subscription_plan_exec
        if subscription_plan_created:
            result: SubscriptionPlanOut = SubscriptionPlanOut(
                **subscription_plan_created.__dict__
            )
        return result

    def get_one_with_filter_or_fail(
        self, db: Session, filter: dict
    ) -> SubscriptionPlanOut:
        try:
            subscription_plan_found = self.__crud_subscription_plan.get_one_by_or_fail(
                db=db, filter=filter
            )
        except Exception as subscription_plan_exec:
            logger.error(
                f"Error in {__name__}.{self.__class__.__name__}.get_one_with_filter: {subscription_plan_exec}"
            )
            raise subscription_plan_exec
        if subscription_plan_found:
            result: SubscriptionPlanOut = SubscriptionPlanOut(
                **subscription_plan_found.__dict__
            )
        return result

    def get_one_with_filter_or_none(
        self, db: Session, filter: dict
    ) -> Optional[SubscriptionPlanOut]:
        subscription_plan_found = self.__crud_subscription_plan.get_one_by(
            db=db, filter=filter
        )
        if subscription_plan_found:
            result: SubscriptionPlanOut = SubscriptionPlanOut(
                **subscription_plan_found.__dict__
            )
            return result
        return None

    def update_one_with_filter(
        self, db: Session, filter: dict, subscription_plan_update: SubscriptionPlanUpdate
    ) -> SubscriptionPlanOut:
        try:
            subscription_plan_updated = self.__crud_subscription_plan.update_one_by(
                db=db, filter=filter, obj_in=subscription_plan_update
            )
        except Exception as subscription_plan_exec:
            logger.error(
                f"Error in {__name__}.{self.__class__.__name__}.update_one_with_filter: {subscription_plan_exec}"
            )
            raise subscription_plan_exec
        if subscription_plan_updated:
            result: SubscriptionPlanOut = SubscriptionPlanOut(
                **subscription_plan_updated.__dict__
            )
        return result

    def get_all(self, db: Session) -> list[SubscriptionPlanOut]:
        try:
            subscription_plans = self.__crud_subscription_plan.get_multi_not_paging(
                db=db
            )
        except Exception as subscription_plan_exec:
            logger.error(
                f"Error in {__name__}.{self.__class__.__name__}.get_all: {subscription_plan_exec}"
            )
            raise subscription_plan_exec

        if subscription_plans:
            results = [
                SubscriptionPlanOut(**subscription_plan.__dict__)
                for subscription_plan in subscription_plans
            ]
        return results
    
    def get_all_or_none(
        self, db: Session, current_user_membership: UserSubscriptionPlan
    ) -> Optional[List[SubscriptionPlanOut]]:
        try:
            results = self.__crud_subscription_plan.get_multi(
                db=db, filter_param={"user_id": current_user_membership.u_id}
            )
            return results
        except:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.get_all_or_none"
            )
            return None
        
    def delete(
        self,
        db: Session,
        plan_id: str,
        current_user_membership: UserSubscriptionPlan,
    ):
        # Chỉ cần xác minh rằng người dùng đã đăng nhập (current_user_membership tồn tại)
        if not current_user_membership:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.delete: User not authenticated"
            )
            raise HTTPException(
                status_code=403,
                detail="Delete chatbot failed: User not authenticated",
            )

        try:
            sub_plan_found = self.__crud_subscription_plan.get_one_by(
                db=db,
                filter={"id": plan_id},
            )

            if sub_plan_found is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        "status": 404,
                        "message": "Subscription plan not found",
                    },
                )

            sub_plan_deleted = self.__crud_subscription_plan.remove(
                db=db, id=sub_plan_found.id
            )
        except:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.remove_subscription_plan: {plan_id}"
            )
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "message": "Remove subscription plan failed",
                },
            )
        return {
            "plan_id": plan_id,
            "subscription_plan": {
                "id": sub_plan_deleted.id,
                "plan_title": sub_plan_deleted.plan_title,
                "deleted_at": sub_plan_deleted.deleted_at,
            },
        }