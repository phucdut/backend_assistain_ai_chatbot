from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy.orm import Session
from app.schemas.user_subscription_plan import UserSubscriptionPlan


from app.schemas.subscription_plan import (
    SubscriptionPlanCreate,
    SubscriptionPlanOut,
    SubscriptionPlanUpdate,
)


class SubscriptionPlanService(ABC):

    @abstractmethod
    def create(
        self, db: Session, subscription_plan_create: SubscriptionPlanCreate
    ) -> SubscriptionPlanOut:
        pass

    @abstractmethod
    def get_one_with_filter_or_fail(
        self, db: Session, filter: dict
    ) -> SubscriptionPlanOut:
        pass

    @abstractmethod
    def get_one_with_filter_or_none(
        self, db: Session, filter: dict
    ) -> Optional[SubscriptionPlanOut]:
        pass

    @abstractmethod
    def update_one_with_filter(
        self, db: Session, filter: dict, subscription_plan: SubscriptionPlanUpdate
    ) -> SubscriptionPlanOut:
        pass

    @abstractmethod
    def get_all(self, db: Session) -> list[SubscriptionPlanOut]:
        pass

    @abstractmethod
    def get_all_or_none(
        self, db: Session, user_id: str
    ) -> Optional[List[SubscriptionPlanOut]]:
        pass

    @abstractmethod
    def delete(
        self,
        db: Session,
        plan_id: str,
        current_user_membership: UserSubscriptionPlan,
    ):
        pass