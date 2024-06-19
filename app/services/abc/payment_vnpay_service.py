from abc import ABC, abstractmethod

from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.user_subscription import (
    UserSubscriptionUpdate,
    UserSubscriptionOut,
)
from app.schemas.user_subscription_plan import UserSubscriptionPlan


class PaymentVnPayService(ABC):

    @abstractmethod
    def read_root(self) -> RedirectResponse:
        pass

    @abstractmethod
    def read_item(self, request: Request, db: Session) -> str:
        pass

    @abstractmethod
    async def get_all_or_none(
        self, db: Session, current_user_membership: UserSubscriptionPlan
    ) -> Optional[List[UserSubscriptionOut]]:
        pass