from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy.orm import Session

from app.schemas.user import (
    UserCreate,
    UserInDB,
    UserOut,
    UserSignInWithGoogle,
    UserUpdate,
    UpdatePassword,
)
from app.schemas.subscription_plan import SubscriptionPlanOut

from app.schemas.user_subscription import (
    UserSubscriptionUpdate,
    UserSubscriptionOut,
)

from app.schemas.user_subscription_plan import UserSubscriptionPlan


class UserService(ABC):

    @abstractmethod
    def create(self, db: Session, user: UserCreate) -> UserOut:
        pass

    @abstractmethod
    def get_one_with_filter_or_fail(self, db: Session, filter: dict) -> UserOut:
        pass

    @abstractmethod
    def get_one_with_filter_or_none(
        self, db: Session, filter: dict
    ) -> Optional[UserOut]:
        pass

    @abstractmethod
    def get_one_user_subscription__with_filter_or_none(
        self, db: Session, filter: dict
    ) -> Optional[UserSubscriptionOut]:
        pass

    @abstractmethod
    def get_one_with_filter_or_none_db(
        self, db: Session, filter: dict
    ) -> Optional[UserInDB]:
        pass

    @abstractmethod
    def update_one_with_filter(
        self,
        db: Session,
        user_update: UserUpdate,
        current_user_membership: UserSubscriptionPlan,
        filter: dict,
    ) -> UserOut:
        pass

    @abstractmethod
    def create_user_with_google(
        self, db: Session, user: UserSignInWithGoogle
    ) -> UserOut:
        pass

    @abstractmethod
    def update_is_verified(self, db: Session, email: str) -> UserOut:
        pass

    @abstractmethod
    def get_profile(
        self, db: Session, current_user_membership: UserSubscriptionPlan
    ) -> UserOut:
        pass

    @abstractmethod
    async def change_password(
        self,
        db: Session,
        current_user_membership: UserSubscriptionPlan,
        password: UpdatePassword,
        user_id=str,
    ):
        pass

    @abstractmethod
    def get_all_user_or_none(
        self, db: Session, user_id: str
    ) -> Optional[List[UserOut]]:
        pass

    @abstractmethod
    def update_one_membership_with_filter(
        self,
        db: Session,
        user_update: UserSubscriptionUpdate,
        current_user_membership: UserSubscriptionPlan,
        filter1: dict,
        filter2: dict,
    ) -> UserSubscriptionOut:
        pass   

    @abstractmethod
    def ban(
        self,
        db: Session,
        user_id: str,
    ):
        pass   

    @abstractmethod
    def unban(
        self,
        db: Session,
        user_id: str,
    ):
        pass   
