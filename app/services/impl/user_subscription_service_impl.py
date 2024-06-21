from typing import Optional

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta

from app.common.logger import setup_logger
from app.crud.crud_user_subscription import crud_user_subscription
from app.schemas.user_subscription import (
    UserSubscriptionCreate,
    UserSubscriptionOut,
    UserSubscriptionUpdate,
)
from app.services.abc.user_subscription_service import UserSubscriptionService
from app.schemas.user_subscription_plan import UserSubscriptionPlan
from app.services.abc.subscription_plan_service import SubscriptionPlanService
from app.services.impl.subscription_plan_service_impl import \
    SubscriptionPlanServiceImpl

logger = setup_logger()


class UserSubscriptionServiceImpl(UserSubscriptionService):

    def __init__(self):
        self.__crud_user_subscription = crud_user_subscription
        self.__subscription_plan_service: SubscriptionPlanService = SubscriptionPlanServiceImpl()

    def create(
        self, db: Session, user_subscription: UserSubscriptionCreate
    ) -> UserSubscriptionOut:
        user_subscription_found = self.get_one_with_filter_or_none(
            db=db, filter={"user_id": user_subscription.user_id}
        )
        if user_subscription_found is not None:
            return user_subscription_found
        try:
            user_subscription_created = self.__crud_user_subscription.create(
                db=db, obj_in=user_subscription
            )
        except Exception as user_subscription_exec:
            logger.error(
                f"Error in {__name__}.{self.__class__.__name__}.create: {user_subscription_exec}"
            )
            raise user_subscription_exec
        if user_subscription_created:
            result: UserSubscriptionOut = UserSubscriptionOut(
                **user_subscription_created.__dict__
            )
        return result

    def get_one_with_filter_or_fail(
        self, db: Session, filter: dict
    ) -> UserSubscriptionOut:
        try:
            user_subscription_found = (
                self.__crud_user_subscription.get_one_by_or_fail(
                    db=db, filter=filter
                )
            )
        except Exception as user_subscription_exec:
            logger.error(
                f"Error in {__name__}.{self.__class__.__name__}.get_one_with_filter: {user_subscription_exec}"
            )
            raise user_subscription_exec
        if user_subscription_found:
            result: UserSubscriptionOut = UserSubscriptionOut(
                **user_subscription_found.__dict__
            )
        return result

    def get_one_with_filter_or_none(
        self, db: Session, filter: dict
    ) -> Optional[UserSubscriptionOut]:
        user_found = self.__crud_user_subscription.get_one_by(
            db=db, filter=filter
        )
        if user_found:
            result: UserSubscriptionOut = UserSubscriptionOut(
                **user_found.__dict__
            )
            return result
        return None

    def update_one_with_filter(
        self,
        db: Session,
        filter: dict,
        user_subscription: UserSubscriptionUpdate,
    ) -> UserSubscriptionOut:
        try:
            user_subscription_updated = (
                self.__crud_user_subscription.update_one_by(
                    db=db, filter=filter, obj_in=user_subscription
                )
            )
        except Exception as user_subscription_exec:
            logger.error(
                f"Error in {__name__}.{self.__class__.__name__}.update_one_with_filter: {user_subscription_exec}"
            )
            raise user_subscription_exec
        if user_subscription_updated:
            result: UserSubscriptionOut = UserSubscriptionOut(
                **user_subscription_updated.__dict__
            )
        return result

    def update_one_with_filter_expire_at(
        self,
        db: Session,
        filter: dict,
        current_user_membership: UserSubscriptionPlan,
    ) -> UserSubscriptionOut:
        user_found = self.__crud_user_subscription.get_one_by(
            db=db, filter=filter
        )
        if user_found is None:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.update_one_with_filter_expire_at: User not found"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        default_plan = (
            self.__subscription_plan_service.get_one_with_filter_or_none(
                db=db, filter={"plan_title": "monthly_free"}
            )
        )
        if default_plan is None:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.update_one_with_filter_expire_at: Default plan not found"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Default plan not found",
            )
        try:
            user_subscription_updated = (
                self.__crud_user_subscription.update_one_by(
                    db=db,
                    filter={"user_id": user_found.user_id},
                    obj_in=UserSubscriptionUpdate(
                        plan_id=default_plan.id,
                        updated_at=datetime.now(),
                        # expire_at=expire_at,
                    ),
                )
            )
        except Exception as user_subscription_exec:
            logger.error(
                f"Error in {__name__}.{self.__class__.__name__}.update_one_with_filter: {user_subscription_exec}"
            )
            raise user_subscription_exec
        if user_subscription_updated:
            result: UserSubscriptionOut = UserSubscriptionOut(
                **user_subscription_updated.__dict__
            )
        return result
