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


user_service = UserServiceImpl()
subscription_plan_service = SubscriptionPlanServiceImpl()
payment_vnpay_service: PaymentVnPayService = PaymentVnPayServiceImpl()
from app.schemas.conversation import ConversationCreate, ConversationOut
from app.schemas.user_subscription_plan import UserSubscriptionPlan 
from app.services.abc.chatbot_service import ChatBotService
from app.services.abc.message_service import MessageService
# from app.services.abc.revenue_service import RevenueService
from app.services.abc.knowledgebase_service import KnowledgeBaseService
from app.services.impl.chatbot_service_impl import ChatBotServiceImpl
from app.services.impl.message_service_impl import MessageServiceImpl
# from app.services.impl.revenue_service_impl import RevenueServiceImpl
from app.services.impl.knowledgebase_service_impl import (
    KnowledgeBaseServiceImpl,
)
from app.services.impl.conversation_service_impl import ConversationServiceImpl

router = APIRouter()
chatbot_service: ChatBotService = ChatBotServiceImpl()
message_service: MessageService = MessageServiceImpl()
# revenue_service: RevenueService = RevenueServiceImpl()
conversation_service = ConversationServiceImpl()
knowledgebase_service: KnowledgeBaseService = KnowledgeBaseServiceImpl()
from app.schemas.chatbot import (
    ChatBotCreate,
    ChatBotInDB,
    ChatBotUpdate,
    ChatBotOut,
)


@router.get("/ban/{user_id}")
def ban_user(
    user_id: str,
    db: Session = Depends(deps.get_db),
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
):
    user = user_service.get_one_with_filter_or_none(
        db=db, filter={"id": current_user_membership.u_id}
    )
    if user.user_role == "admin":
        user_ban = user_service.ban(db=db, user_id=user_id)
        return user_ban


@router.get("/unban/{user_id}")
def ban_user(
    user_id: str,
    db: Session = Depends(deps.get_db),
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
):
    user = user_service.get_one_with_filter_or_none(
        db=db, filter={"id": current_user_membership.u_id}
    )
    if user.user_role == "admin":
        user_ban = user_service.unban(db=db, user_id=user_id)
        return user_ban

@router.get(
    "/user/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[UserOut],
)
def get_one(
    user_id: str,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
) -> Optional[UserOut]:
    user = user_service.get_one_with_filter_or_none(
        db=db, filter={"id": user_id}
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get(
    "/chatbot/all",
    status_code=status.HTTP_200_OK,
)
def get_all(
    current_user_membership: UserSubscriptionPlan = Depends(oauth2.get_current_user_membership_info_by_token),
    db: Session = Depends(deps.get_db)
):
    chatbots = chatbot_service.get_all_or_none_id(db=db, current_user_membership=current_user_membership)
    return chatbots

# @router.get("/revenue")
# def get_revenue(db: Session = Depends(deps.get_db), current_user_membership: UserSubscriptionPlan = Depends(oauth2.get_current_user_membership_info_by_token)):
#     user = user_service.get_one_with_filter_or_none(db=db, filter={"id": current_user_membership.u_id})
#     if user.user_role == "admin":
#         revenues = revenue_service.get_all_or_none(db=db)
#         return revenues
#     else:
#         raise HTTPException(
#             detail="Access Denied", status_code=400
#         )