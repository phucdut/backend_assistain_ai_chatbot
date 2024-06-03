import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core import oauth2
from app.schemas.conversation import ConversationCreate, ConversationOut
from app.schemas.user_subscription_plan import UserSubscriptionPlan
from app.services.abc.conversation_service import ConversationService
from app.services.impl.conversation_service_impl import ConversationServiceImpl

router = APIRouter()

conversation_service = ConversationServiceImpl()


@router.get("/", status_code=status.HTTP_200_OK)
def get_all(
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
):
    conversations = conversation_service.get_all_or_none(
        db=db, current_user_membership=current_user_membership
    )
    return conversations


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
def get_all(
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
    user_id=str,
):
    conversations = conversation_service.get_all_or_none_with_user_id(
        db=db, current_user_membership=current_user_membership, user_id=user_id
    )
    return conversations


@router.get("/load-message/{conversation_id}", status_code=status.HTTP_200_OK)
def load_messages(
    conversation_id: str,
    # current_user_membership: UserSubscriptionPlan = Depends(
    #     oauth2.get_current_user_membership_info_by_token
    # ),
    db: Session = Depends(deps.get_db),
):
    messages = conversation_service.load_messsages(
        conversation_id=conversation_id,
        db=db,
        # current_user_membership=current_user_membership,
    )
    return messages


@router.get("/{conversation_id}/join", status_code=status.HTTP_200_OK)
def join_conversation(
    conversation_id: str,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
):
    user_join = conversation_service.join_conversation(
        conversation_id=conversation_id,
        db=db,
        current_user_membership=current_user_membership,
    )
    if user_join == True:
        return status.HTTP_200_OK
    else:
        return status.HTTP_404_NOT_FOUND


@router.post("/{conversation_id}/message", status_code=status.HTTP_200_OK)
def message_chatbot(
    conversation_id: str,
    message: dict,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
):
    response = conversation_service.message(
        db=db,
        message=message["message"],
        current_user_membership=current_user_membership,
        conversation_id=conversation_id,
    )
    return response


# @router.post("/create-conversation", status_code=status.HTTP_201_CREATED, response_model=ConversationOut)
# def create(token: str, conversation: ConversationCreate, chatbot_id: uuid.UUID, db: Session = Depends(deps.get_db)
#            ) -> ConversationOut:
#     new_conversation = conversation_service.create(
#         db=db, conversation=conversation, chatbot_id=chatbot_id, token=token)
#     return new_conversation
#
#
# @router.post("/ask-question", status_code=status.HTTP_200_OK, response_model=str)
# def ask_question(token: str, query: str, conversation_id: uuid.UUID, db: Session = Depends(deps.get_db)
#                  ) -> str:
#     response = conversation_service.conversation(
#         db, query, conversation_id, token)
#     return response
