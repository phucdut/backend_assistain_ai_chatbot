import uuid
from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session

from app.schemas.conversation import ConversationCreate, ConversationOut
from app.schemas.user_subscription_plan import UserSubscriptionPlan


class ConversationService(ABC):

    @abstractmethod
    def create(self, db: Session, conversation_create: ConversationCreate, chatbot_id: uuid.UUID,  current_user_membership: UserSubscriptionPlan) -> ConversationOut:
        pass

    @abstractmethod
    def get_one_with_filter_or_none(self, db: Session, current_user_membership: UserSubscriptionPlan, filter: dict) -> Optional[ConversationOut]:
        pass

    @abstractmethod
    def check_conversation(self, db: Session, current_user_membership: UserSubscriptionPlan, conversation_id: str, chatbot_id: str, client_ip: str) -> ConversationOut:
        pass

