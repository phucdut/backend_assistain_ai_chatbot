from typing import List, Optional

from sqlalchemy.orm import Session

from app.common.logger import setup_logger
from app.crud.crud_admin_dashboard import crud_admin_dashboard
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
from app.schemas.user_subscription_plan import UserSubscriptionPlan
from app.services.abc.admin_dashboard_service import AdminDashboardService

logger = setup_logger()


class AdminDashboardServiceImpl(AdminDashboardService):
    def __init__(self):
        self.__crud_admin_dashboard = crud_admin_dashboard

    def get_statistic_table_message_by_filter(
        self,
        db: Session,
        filter: str,
        value: str,
        current_user_membership: UserSubscriptionPlan,
    ) -> List[ChartDataTableMessageSchema]:
        try:
            return self.__crud_admin_dashboard.get_table_message_capital_by_filter(
                db, filter, value
            )
        except Exception as e:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.get_statistic_table_message_by_filter: {e}"
            )
            return []

    def get_statistic_table_conversation_by_filter(
        self,
        db: Session,
        filter: str,
        value: str,
        chatbot_id: str,
        current_user_membership: UserSubscriptionPlan,
    ) -> List[ChartDataTableConversationSchema]:
        try:
            return self.__crud_admin_dashboard.get_table_conversation_capital_by_filter(
                db, filter, value, chatbot_id
            )
        except Exception as e:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.get_statistic_table_conversation_by_filter: {e}"
            )
            return []


    def get_table_conversation_by_filter(
        self,
        db: Session,
        filter: str,
        value: str,
        chatbot_id: str,
        current_user_membership: UserSubscriptionPlan,
    ) -> Optional[TotalDataTableConversationSchema]:
        try:
            return self.__crud_admin_dashboard.get_total_rating_score_by_filter(
                db, filter, value, chatbot_id
            )
        except Exception as e:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.get_table_conversation_by_filter: {e}"
            )
            return []
