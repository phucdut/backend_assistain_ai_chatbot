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


@router.get("/profile", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_profile(
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
):
    user = user_service.get_profile(
        db=db, current_user_membership=current_user_membership
    )
    return user


@router.put(
    "/edit/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserOut,
)
def update(
    user_id: str,
    user_update: UserUpdate,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
) -> UserOut:
    updated_user = user_service.update_one_with_filter(
        db=db,
        user_update=user_update,
        current_user_membership=current_user_membership,
        filter={"id": user_id},
    )
    return updated_user


@router.post("/{user_id}/change-password")
async def change_password(
    change_password: UpdatePassword,
    user_id: str,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
):
    return await user_service.change_password(
        db=db,
        current_user_membership=current_user_membership,
        user_id=user_id,
        password=change_password,
    )

@router.get("/get-all", status_code=status.HTTP_200_OK)
def get_all(
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
):
    user = user_service.get_all_user_or_none(
        db=db, current_user_membership=current_user_membership
    )
    return user


@router.put(
    "/edit/{user_id}/{plan_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserOut,
)
def update(
    user_id: str,
    plan_id: str,
    subscription_plan_update: UserSubscriptionUpdate,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
) -> UserSubscriptionOut:
    updated_user = user_service.update_one_membership_with_filter(
        db=db,
        user_update=subscription_plan_update,
        current_user_membership=current_user_membership,
        filter1={"id": user_id},
        filter2={"id": plan_id},
    )


@router.get("/{user_id}/get-user-subscription", status_code=status.HTTP_200_OK)
def get_one(
    user_id: str,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
    response_model=Optional[UserSubscriptionOut],
) -> Optional[UserSubscriptionOut]:
    user_subscription = (
        user_service.get_one_user_subscription__with_filter_or_none(
            db=db, filter={"user_id": user_id}
        )
    )
    if user_subscription is None:
        raise HTTPException(
            status_code=404, detail="User subscription not found"
        )
    return user_subscription
