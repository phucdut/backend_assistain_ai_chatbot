import json
from typing import List, Optional

import requests
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
from sqlalchemy.orm import Session

from app.api import deps
from app.core import oauth2
from app.schemas.knowledge_base import (
    KnowledgeBaseAdd,
    KnowledgeBaseOut,
    KnowledgeBaseRemove,
    KnowledgeBaseInDB,
)
from app.schemas.conversation import ConversationCreate, ConversationOut
from app.schemas.user_subscription_plan import UserSubscriptionPlan
from app.services.abc.chatbot_service import ChatBotService
from app.services.abc.knowledgebase_service import KnowledgeBaseService
from app.services.impl.chatbot_service_impl import ChatBotServiceImpl
from app.services.impl.knowledgebase_service_impl import (
    KnowledgeBaseServiceImpl,
)
from app.services.impl.conversation_service_impl import ConversationServiceImpl

router = APIRouter()
chatbot_service: ChatBotService = ChatBotServiceImpl()
conversation_service = ConversationServiceImpl()
knowledgebase_service: KnowledgeBaseService = KnowledgeBaseServiceImpl()
from app.schemas.chatbot import (
    ChatBotCreate,
    ChatBotInDB,
    ChatBotUpdate,
    ChatBotOut,
)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=ChatBotOut
)
def create(
    chatbot_create: ChatBotCreate,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
) -> ChatBotOut:
    chatbot_created: ChatBotOut = chatbot_service.create(
        db=db,
        chatbot_create=chatbot_create,
        current_user_membership=current_user_membership,
    )
    return chatbot_created


# @router.get("/get-all", status_code=status.HTTP_200_OK)
# def get_all(
#     current_user_membership: UserSubscriptionPlan = Depends(
#         oauth2.get_current_user_membership_info_by_token
#     ),
#     db: Session = Depends(deps.get_db),
# ):
#     chatbots = chatbot_service.get_all_or_none(
#         db=db, current_user_membership=current_user_membership
#     )
#     return chatbots


@router.get(
    "/{user_id}/get-all-chatbot",
    status_code=status.HTTP_200_OK,
    # response_model=Optional[List[ChatBotOut]],
)
def get_all(
    user_id: str,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
):
    chatbots = chatbot_service.get_all_or_none(db=db, user_id=user_id)
    return chatbots


@router.get(
    "/{chatbot_id}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[ChatBotOut],
)
def get_one(
    chatbot_id: str,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
) -> Optional[ChatBotOut]:
    chatbot = chatbot_service.get_one_with_filter_or_none(
        db=db, filter={"id": chatbot_id}
    )
    if chatbot is None:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return chatbot


@router.put(
    "/edit/{chatbot_id}",
    status_code=status.HTTP_200_OK,
    response_model=ChatBotOut,
)
def update(
    chatbot_id: str,
    chatbot_update: ChatBotUpdate,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
) -> ChatBotOut:
    updated_chatbot = chatbot_service.update_one_with_filter(
        db=db,
        chatbot_update=chatbot_update,
        current_user_membership=current_user_membership,
        filter={"id": chatbot_id},
    )
    return updated_chatbot


@router.delete(
    "/delete/{chatbot_id}",
    status_code=status.HTTP_200_OK,
    response_model=ChatBotInDB,
)
def delete(
    chatbot_id: str,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
) -> ChatBotInDB:
    return chatbot_service.delete(
        db=db,
        chatbot_id=chatbot_id,
        current_user_membership=current_user_membership,
    )


@router.post("/{chatbot_id}/knowledge-base", status_code=status.HTTP_200_OK)
def add_knowledgeBase(
    chatbot_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
):
    file_path = f"knowledge_files/{chatbot_id}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    created_knowledgeBase = knowledgebase_service.create(
        db=db,
        chatbot_id=chatbot_id,
        file_path=file_path,
        file_name=file.filename,
    )
    return created_knowledgeBase


@router.get(
    "/{chatbot_id}/get-all-knowledge-base",
    status_code=status.HTTP_200_OK,
    response_model=Optional[List[KnowledgeBaseInDB]],
)
def get_all(
    chatbot_id: str,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
) -> Optional[List[KnowledgeBaseInDB]]:
    return knowledgebase_service.get_knowledgeBase_by_chatbot_id(
        db=db,
        chatbot_id=chatbot_id,
    )


@router.delete(
    "/{chatbot_id}/knowledge-base/{knowledge_base_id}",
    status_code=status.HTTP_200_OK,
)
def delete(
    chatbot_id: str,
    knowledge_base_id: str,
    # current_user_membership: UserSubscriptionPlan = Depends(
    #     oauth2.get_current_user_membership_info_by_token
    # ),
    db: Session = Depends(deps.get_db),
):
    return knowledgebase_service.delete(
        db=db,
        chatbot_id=chatbot_id,
        knowledge_base_id=knowledge_base_id,
        # current_user_membership=current_user_membership,
    )


@router.post("/{chatbot_id}/message", status_code=status.HTTP_200_OK)
def message_chatbot(
    chatbot_id: str,
    message: dict,
    request: Request,
    db: Session = Depends(deps.get_db),
    conversation_id: str = Cookie(None),
):
    # client_ip = request.client.host
    # client_ip = request.client.host
    client_ip = "42.118.119.124"
    response = chatbot_service.message(
        db=db,
        chatbot_id=chatbot_id,
        conversation_id=conversation_id,
        message=message["message"],
        client_ip=client_ip,
    )
    return response


@router.get("/{chatbot_id}/new-conversation", status_code=status.HTTP_200_OK)
def new_conversation(
    chatbot_id: str, request: Request, db: Session = Depends(deps.get_db)
) -> ConversationOut:
    # client_ip = request.client.host
    client_ip = "42.118.119.124"
    new_conversation = conversation_service.create(
        db=db, chatbot_id=chatbot_id, client_ip=client_ip
    )
    return new_conversation
