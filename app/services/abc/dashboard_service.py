from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy.orm import Session

from app.schemas.chart_data_table_conversations_schema import (
    ChartDataTableConversationSchema,
)
from app.schemas.total_data_table_conversations_schema import (
    TotalDataTableConversationSchema,
)
from app.schemas.chart_data_table_messages_schema import (
    ChartDataTableMessageSchema,
)
from app.schemas.total_data_table_messages_schema import (
    TotalDataTableMessageSchema,
)
from app.schemas.total_data_table_revenue import (
    TotalDataTableRevenueSchema, 
)
from app.schemas.user_subscription_plan import UserSubscriptionPlan


class AdminDashboardService(ABC):

    @abstractmethod
    def get_statistic_table_message_by_filter(
        self,
        db: Session,
        filter: str,
        value: str,
        conversation_id: str,
        current_user_membership: UserSubscriptionPlan,
    ) -> List[ChartDataTableMessageSchema]:
        pass

    @abstractmethod
    def get_statistic_table_conversation_by_filter(
        self,
        db: Session,
        filter: str,
        value: str,
        chatbot_id: str,
        current_user_membership: UserSubscriptionPlan,
    ) -> List[ChartDataTableConversationSchema]:
        pass

    @abstractmethod
    def get_table_conversation_by_filter(
        self,
        db: Session,
        filter: str,
        value: str,
        chatbot_id: str,
        current_user_membership: UserSubscriptionPlan,
    ) -> Optional[TotalDataTableConversationSchema]:
        pass

    @abstractmethod
    def get_revenue_by_filter(
        self,
        db: Session,
        filter: str,
        value: str,
        current_user_membership: UserSubscriptionPlan,
    ) -> Optional[TotalDataTableRevenueSchema]:
        pass

