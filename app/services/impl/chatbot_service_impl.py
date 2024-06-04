import json
import traceback
import time
from typing import List, Optional
from fastapi.responses import JSONResponse

import PyPDF2
from fastapi import Depends, HTTPException
from openai import OpenAI
from sqlalchemy.orm import Session

from app.common import utils
from app.common.logger import setup_logger
from app.core.config import settings
from app.crud.crud_chatbot import crud_chatbot
from app.crud.crud_user import crud_user
from app.crud.crud_conversation import crud_conversation
from app.crud.crud_message import crud_message
from app.schemas.chatbot import (
    ChatBotCreate,
    ChatBotInDB,
    ChatBotOut,
    ChatBotUpdate,
)
from app.schemas.conversation import (
    ConversationCreate,
    ConversationOut,
    ConversationUpdate,
)
from app.schemas.message import (
    MessageBase,
    MessageCreate,
    MessageOut,
    MessageUpdate,
)
from app.schemas.user_subscription_plan import UserSubscriptionPlan
from app.services.abc.chatbot_service import ChatBotService
from app.services.abc.conversation_service import ConversationService
from app.services.abc.knowledgebase_service import KnowledgeBaseService
from app.services.abc.message_service import MessageService
from app.services.abc.user_session_service import UserSessionService
from app.services.impl.conversation_service_impl import ConversationServiceImpl
from app.services.impl.knowledgebase_service_impl import (
    KnowledgeBaseServiceImpl,
)
from app.services.impl.message_service_impl import MessageServiceImpl
from app.services.impl.user_session_service_impl import UserSessionServiceImpl

logger = setup_logger()


class ChatBotServiceImpl(ChatBotService):

    def __init__(self):
        self.__crud_chatbot = crud_chatbot
        self.__crud_user = crud_user
        self.__user_session_service: UserSessionService = (
            UserSessionServiceImpl()
        )
        self.__conversation_service: ConversationService = (
            ConversationServiceImpl()
        )
        self.__crud_message_base = crud_message
        self.__crud_message: MessageService = MessageServiceImpl()
        self.__crud_knowledgeBase: KnowledgeBaseService = (
            KnowledgeBaseServiceImpl()
        )
        self.client = OpenAI(api_key=settings.OPEN_API_KEY)
        self.DEFAULT_PROMPT = (
            "You are a helpful assistant. The first prompt will be a long text,"
            "and any messages that you get be regarding that. Please answer any "
            "questions and requests having in mind the first prompt"
        )

    def create(
        self,
        db: Session,
        chatbot_create: ChatBotCreate,
        user_id: str,
        current_user_membership: UserSubscriptionPlan,
    ) -> ChatBotOut:
        # logger.warning(f"{current_user_membership}")

        chatbots = self.get_all_or_none(db=db, user_id=user_id)
        if (
            chatbots is not None
            and chatbots["total"]
            >= current_user_membership.sp_number_of_chatbots
        ):
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.create_chatbot: User has reached the limit of chatbots"
            )
            logger.info(f"Current chatbots: {chatbots}")
            raise HTTPException(
                detail="Create Chatbot failed: User has reached the limit of chatbots",
                status_code=400,
            )
        chatbot_in_db: ChatBotInDB = ChatBotInDB(
            **chatbot_create.__dict__, user_id=current_user_membership.u_id
        )
        # prompt=self.DEFAULT_PROMPT)

        logger.info(f"ChatbotInDB: {chatbot_in_db}")

        try:
            chatbot_created = self.__crud_chatbot.create(
                db=db, obj_in=chatbot_in_db
            )
        except:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.create_chatbot"
            )
            raise HTTPException(detail="Create Chatbot failed", status_code=400)
        if chatbot_created:
            result: ChatBotOut = ChatBotOut(**chatbot_created.__dict__)
        return result

    def get_one_with_filter_or_none(
        self, db: Session, filter: dict
    ) -> Optional[ChatBotOut]:
        try:
            return self.__crud_chatbot.get_one_by(db=db, filter=filter)
        except:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.get_one_with_filter_or_none"
            )
            return None

    def update_one_with_filter(
        self,
        db: Session,
        chatbot_update: ChatBotUpdate,
        current_user_membership: UserSubscriptionPlan,
        filter: dict,
    ) -> ChatBotOut:
        try:
            chatbot = self.get_one_with_filter_or_none(db=db, filter=filter)
            if chatbot is None:
                logger.exception(
                    f"Exception in {__name__}.{self.__class__.__name__}.update_one_with_filter: Chatbot not found"
                )
                raise HTTPException(
                    detail="Update Chatbot failed: Chatbot not found",
                    status_code=404,
                )
            return self.__crud_chatbot.update(
                db=db, db_obj=chatbot, obj_in=chatbot_update
            )
        except:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.update_one_with_filter"
            )
            raise HTTPException(detail="Update Chatbot failed", status_code=400)

    def delete(
        self,
        db: Session,
        user_id: str,
        chatbot_id: str,
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
            chatbot_found = self.__crud_chatbot.get_one_by(
                db=db,
                filter={"id": chatbot_id, "user_id": user_id},
            )

            if chatbot_found is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        "status": 404,
                        "message": "Chatbot not found",
                    },
                )

            chatbot_deleted = self.__crud_chatbot.remove(
                db=db, id=chatbot_found.id
            )
        except:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.remove_chatbot"
            )
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "message": "Remove chatbot failed",
                },
            )
        return {
            "user_id": user_id,
            "chatbot": {
                "id": chatbot_deleted.id,
                "chatbot_name": chatbot_deleted.chatbot_name,
                "deleted_at": chatbot_deleted.deleted_at,
            },
        }

    def message(
        self,
        db: Session,
        chatbot_id: str,
        conversation_id: str,
        message: str,
        client_ip: str,
    ) -> MessageOut:
        try:
            start_time = time.time()
            conversation = self.__conversation_service.check_conversation(
                db=db,
                conversation_id=conversation_id,
                chatbot_id=chatbot_id,
                client_ip=client_ip,
            )
            # Add message to Message
            message_form = {
                "sender_id": conversation.conversation_name,
                "sender_type": "guest",
                "message": message,
                "conversation_id": conversation.id,
            }
            add_message = self.__crud_message_base.create(
                db=db, obj_in=message_form
            )
            if conversation.is_taken == False:
                # Handle auto response and add to Message
                response, chatbot_id = self.handle_message(
                    db=db,
                    chatbot_id=chatbot_id,
                    conversation_id=conversation_id,
                    message=message,
                )
                end_time = time.time()  # End time
                execution_time = end_time - start_time
                message_form = {
                    "sender_id": chatbot_id,
                    "sender_type": "bot",
                    "message": response,
                    "conversation_id": conversation.id,
                    "latency": execution_time,
                }
                add_message = self.__crud_message_base.create(
                    db=db, obj_in=message_form
                )
                return add_message
            else:
                # Handle manual response and add to Message
                return add_message
        except:
            traceback.print_exc()
            pass

    def message_with_auth(
        self,
        db: Session,
        chatbot_id: str,
        conversation_id: str,
        message: str,
        client_ip: str,
        current_user_membership: UserSubscriptionPlan,
    ) -> MessageOut:
        # logger.warning(f"{current_user_membership}")
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
            conversation = self.__conversation_service.check_conversation(
                db=db,
                conversation_id=conversation_id,
                chatbot_id=chatbot_id,
                client_ip=client_ip,
            )
            # Add message to Message
            message_form = {
                "sender_id": conversation.conversation_name,
                "sender_type": "guest",
                "message": message,
                "conversation_id": conversation.id,
            }
            add_message = self.__crud_message_base.create(
                db=db, obj_in=message_form
            )
            if conversation.is_taken == False:
                # Handle auto response and add to Message
                response, chatbot_id = self.handle_message(
                    db=db,
                    chatbot_id=chatbot_id,
                    conversation_id=conversation_id,
                    message=message,
                )
                message_form = {
                    "sender_id": chatbot_id,
                    "sender_type": "bot",
                    "message": response,
                    "conversation_id": conversation.id,
                }
                add_message = self.__crud_message_base.create(
                    db=db, obj_in=message_form
                )
                return add_message
            else:
                # Handle manual response and add to Message
                return add_message
        except:
            traceback.print_exc()
            pass

    def handle_message(
        self, db: Session, chatbot_id: str, conversation_id: str, message: str
    ):
        try:
            temp_knowledgeBase = []
            messages = self.__crud_message.get_messages_by_conversation_id(
                db=db, conversation_id=conversation_id
            )
            knowledgeBases = (
                self.__crud_knowledgeBase.get_knowledgeBase_by_chatbot_id(
                    db=db, chatbot_id=chatbot_id
                )
            )
            chatbot = self.get_one_with_filter_or_none(
                db=db, filter={"id": chatbot_id}
            )
            # Create response
            temp_knowledgeBase.append(
                {"role": "system", "content": chatbot.prompt}
            )
            for knowledgeBase in knowledgeBases:
                temp_knowledgeBase.append(
                    {
                        "role": "system",
                        "content": utils.read_pdf(knowledgeBase["file_path"]),
                    }
                )
            for message in messages:
                temp_knowledgeBase.append(
                    {"role": "user", "content": message["message"]}
                )
            response = self.client.chat.completions.create(
                model=chatbot.model,
                messages=temp_knowledgeBase,
                max_tokens=chatbot.max_tokens,
                temperature=chatbot.temperature,
            )
            response = response.choices[0].message.content
            return response, chatbot.id
        except:
            traceback.print_exc()
            pass

    def get_all_or_none(
        self,
        db: Session,
        user_id: str,
    ) -> Optional[List[ChatBotOut]]:
        try:
            user_found = self.__crud_user.get_one_by(
                db=db, filter={"id": user_id}
            )
            if user_found is None:
                raise HTTPException(status_code=404, detail="User not found")

            chatbots: List[ChatBotOut] = self.__crud_chatbot.get_multi(
                db=db,
                filter_param={
                    "filter": json.dumps({"user_id": str(user_found.id)})
                },
            )
            return chatbots
        except Exception as e:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.get_all_or_none"
            )
            raise HTTPException(
                status_code=400, detail="Get all chatbot failed"
            )
