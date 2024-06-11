import uuid
from typing import List, Optional
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core import oauth2

from app.schemas.user_subscription_plan import UserSubscriptionPlan
from app.schemas.subscription_plan import (
    SubscriptionPlanUpdate,
    SubscriptionPlanOut,
    SubscriptionPlanCreate,
)

from app.services.abc.user_service import UserService
from app.services.impl.user_service_impl import UserServiceImpl
from app.schemas.user import (
    UserCreate,
    UserInDB,
    UserOut,
    UserSignInWithGoogle,
    UserUpdate,
    UpdatePassword,
)
from app.schemas.user_subscription import (
    UserSubscriptionUpdate,
    UserSubscriptionOut,
)
from app.services.abc.payment_vnpay_service import PaymentVnPayService
from app.services.impl.payment_vnpay_service_impl import PaymentVnPayServiceImpl
from app.services.impl.subscription_plan_service_impl import (
    SubscriptionPlanServiceImpl,
)


router = APIRouter()

user_service = UserServiceImpl()
subscription_plan_service = SubscriptionPlanServiceImpl()
payment_vnpay_service: PaymentVnPayService = PaymentVnPayServiceImpl()


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=SubscriptionPlanOut,
)
def create(
    subscription_plan_create: SubscriptionPlanCreate,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
) -> SubscriptionPlanOut:
    subscription_plan_create: SubscriptionPlanOut = subscription_plan_service.create(
        db=db,
        subscription_plan_create=subscription_plan_create,
        # current_user_membership=current_user_membership,
    )
    return subscription_plan_create


@router.get("/get-all", status_code=status.HTTP_200_OK)
def get_all(
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
):
    user_subscription_plan = subscription_plan_service.get_all_or_none(
        db=db, current_user_membership=current_user_membership
    )
    return user_subscription_plan


@router.put(
    "/edit-sub-plan/{plan_id}",
    status_code=status.HTTP_200_OK,
    response_model=SubscriptionPlanUpdate,
)
def update(
    plan_id: str,
    subscription_plan_update: SubscriptionPlanUpdate,
    db: Session = Depends(deps.get_db),
) -> SubscriptionPlanOut:
    updated_subscription_plan = (
        subscription_plan_service.update_one_with_filter(
            db=db,
            subscription_plan_update=subscription_plan_update,
            filter={"id": plan_id},
        )
    )
    return updated_subscription_plan


@router.get(
    "/sub-plan-detail/{plan_id}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[SubscriptionPlanOut],
)
def get_one(
    plan_id: str,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
) -> Optional[SubscriptionPlanOut]:
    subscription_plan = subscription_plan_service.get_one_with_filter_or_none(
        db=db, filter={"id": plan_id}
    )
    if subscription_plan is None:
        raise HTTPException(
            status_code=404, detail="Subscription plan not found"
        )
    return subscription_plan


@router.delete(
    "/delete/{plan_id}",
    status_code=status.HTTP_200_OK,
)
def delete(
    plan_id: str,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
):
    return subscription_plan_service.delete(
        db=db,
        plan_id=plan_id,
        current_user_membership=current_user_membership,
    )
