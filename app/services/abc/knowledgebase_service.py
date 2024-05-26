from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy.orm import Session
from app.schemas.knowledge_base import (
    KnowledgeBaseAdd,
    KnowledgeBaseOut,
    KnowledgeBaseRemove,
    KnowledgeBaseInDB,
)

from app.schemas.knowledge_base import KnowledgeBaseOut


class KnowledgeBaseService(ABC):
    @abstractmethod
    def create(
        self, db: Session, chatbot_id: str, file_path: str, file_name: str
    ) -> KnowledgeBaseOut:
        pass

    @abstractmethod
    def get_knowledgeBase_by_chatbot_id(self, db: Session, chatbot_id: str):
        pass

    @abstractmethod
    def get_all(
        self,
        db: Session,
        chatbot_id: str,
    ) -> Optional[List[KnowledgeBaseInDB]]:
        pass
