import json
import traceback
from pathlib import Path
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
        self.__crud_conversation = crud_conversation
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

        # Check if chatbot name already exists in the database
        existing_chatbot = self.__crud_chatbot.get_by_name(
            db=db, name=chatbot_create.chatbot_name, user_id=user_id
        )
        if existing_chatbot:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.create_chatbot: Chatbot name already exists"
            )
            raise HTTPException(
                detail="Create Chatbot failed: Chatbot name already exists",
                status_code=400,
            )

        # logger.info(f"ChatbotInDB: {chatbot_in_db}")
        try:
            chatbot_created = self.__crud_chatbot.create(
                db=db, obj_in=chatbot_in_db
            )
            print(f"chatbot_created: {chatbot_created}")
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
        # Check if chatbot name already exists in the database
        # existing_chatbot = self.__crud_chatbot.get_by_name(db=db, name=chatbot_update.chatbot_name)
        # if existing_chatbot:
        #     logger.exception(
        #         f"Exception in {__name__}.{self.__class__.__name__}.update_one_with_filter: Chatbot name already exists"
        #     )
        #     raise HTTPException(
        #         detail="Update Chatbot failed: Chatbot name already exists",
        #         status_code=400,
        #     )

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
            
            from app.services.impl.conversation_service_impl import (
                ConversationServiceImpl,
            )
            from app.services.impl.knowledgebase_service_impl import (
                KnowledgeBaseServiceImpl,
            )


            conversation_service = ConversationServiceImpl()
            knowledge_base_service = KnowledgeBaseServiceImpl()

            # Lấy tất cả các tập tin kiến thức liên quan đến chatbot
            knowledgeBases = (knowledge_base_service.get_knowledgeBase_by_chatbot_id(
                db=db, chatbot_id = chatbot_id
            ))
            # print(f"knowledgeBases id: {knowledgeBases}")
            
            # Xóa các tập tin liên quan đến chatbot
            for kb in knowledgeBases:
                print(f"knowledgeBase id: {kb['id']}")  # Truy cập thuộc tính 'id' của từng dict
                knowledge_base_service.delete(db=db, chatbot_id=chatbot_id, knowledge_base_id=kb['id'])

            # Lấy tất cả các cuộc hội thoại liên quan đến chatbot
            conversations = (conversation_service.get_all_or_none_with_chatbot_id(
                db=db, chatbot_id = chatbot_id, current_user_membership=current_user_membership
            ))
            
            # Xóa các cuộc hội thoại liên quan đến chatbot
            for conv in conversations["results"]:
                print(f"conversation id: {conv.id}")
                conversation_service.delete(db=db, chatbot_id=chatbot_id, conversation_id=conv.id)

            # Xóa chatbot
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
            # Check condition
            chatbot = self.get_one_with_filter_or_none(
                db=db, filter={"id": chatbot_id}
            )
            owner_id = chatbot.user_id
            chatbots = self.get_all_or_none(db=db, user_id=owner_id)
            from app.services.impl.user_service_impl import UserServiceImpl

            user_service = UserServiceImpl()
            owner_plan_id = user_service.get_one_with_u_plan_filter_or_none(
                db=db, filter={"id": owner_id}
            ).plan_id
            from app.services.impl.subscription_plan_service_impl import (
                SubscriptionPlanServiceImpl,
            )

            subscription_plan_service = SubscriptionPlanServiceImpl()
            current_plan = (
                subscription_plan_service.get_one_with_filter_or_none(
                    db=db, filter={"id": owner_plan_id}
                )
            )
            total_messages = 0
            total_tokens = 0
            for _chatbot in chatbots["results"]:
                total_messages += _chatbot.total_messages
                total_tokens += _chatbot.total_tokens
            if (
                total_messages > current_plan.message_credits
                or total_tokens > current_plan.max_character_per_chatbot
            ):
                raise HTTPException(
                    detail="User has reached limitation", status_code=400
                )
            # Execution time
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
                answer, chatbot_id, completion_token = self.handle_message(
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
                    "message": answer,
                    "conversation_id": conversation.id,
                    "latency": execution_time,
                }
                add_message = self.__crud_message_base.create(
                    db=db, obj_in=message_form
                )

                print(f"add_message: {add_message}")
                # Update Chatbot Usage
                chatbot_update = {
                    "total_messages": chatbot.total_messages + 1,
                    "total_tokens": chatbot.total_tokens + completion_token,
                }
                chatbot_updated = self.__crud_chatbot.update_one_by(
                    db=db, filter={"id": chatbot_id}, obj_in=chatbot_update
                )
                return add_message
            else:
                # Handle manual response and add to Message
                return add_message
        except Exception as e:
            print(f"Exception in message: {e}")
            traceback.print_exc()
            raise HTTPException(
                detail=f"Error processing message: {str(e)}", status_code=500
            )

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
                file_path = knowledgeBase["file_path"]

                # Determine file extension
                file_extension = Path(file_path).suffix.lower()

                if file_extension == ".pdf":
                    content = utils.read_pdf(file_path)
                elif file_extension == ".csv":
                    content = utils.read_csv(file_path)
                elif file_extension == ".docx":
                    content = utils.read_docx(file_path)
                else:
                    raise ValueError(f"Unsupported file type: {file_extension}")
                # print(f"content: {content}")
                temp_knowledgeBase.append(
                    {
                        "role": "system",
                        "content": content,
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
            if (
                not response.choices
                or not response.choices[0].message.content.strip()
            ):
                raise HTTPException(
                    detail="Empty response from AI model", status_code=500
                )
            answer = response.choices[0].message.content
            # print(f"Exception in handle_message: {answer}")
            completion_token = response.usage.completion_tokens
            return answer, chatbot.id, completion_token
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
                f"Exception in {__name__}.{self.__class__.__name__}.message_with_auth: User not authenticated"
            )
            raise HTTPException(
                status_code=403,
                detail="Message failed: User not authenticated",
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

    def get_all_or_none_id(
        self, db: Session, current_user_membership: UserSubscriptionPlan
    ) -> Optional[List[ChatBotOut]]:
        try:
            results = self.__crud_chatbot.get_multi(
                db=db, filter_param={"user_id": current_user_membership.u_id}
            )
            return results
        except:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.get_all_or_none"
            )
            return None
