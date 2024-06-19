from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.common.logger import setup_logger
from app.core import oauth2
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
from app.services.abc.dashboard_service import AdminDashboardService
from app.services.impl.dashboard_service_impl import AdminDashboardServiceImpl

logger = setup_logger()

dashboard_service: AdminDashboardService = AdminDashboardServiceImpl()


router = APIRouter()


@router.get("/chart/{filter}/{value}/message/{conversation_id}", response_model=List[ChartDataTableMessageSchema])
def get_statistic_table_message_by_filter(
    filter: str,
    value: str,
    conversation_id: str,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
) -> List[ChartDataTableMessageSchema]:
    return dashboard_service.get_statistic_table_message_by_filter(
        db=db,
        filter=filter,
        value=value,
        conversation_id=conversation_id,
        current_user_membership=current_user_membership,
    )

@router.get("/chart/{filter}/{value}/conversation/{chatbot_id}", response_model=List[ChartDataTableConversationSchema])
def get_statistic_table_conversation_by_filter(
    filter: str,
    value: str,
    chatbot_id: str,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
) -> List[ChartDataTableConversationSchema]:
    return dashboard_service.get_statistic_table_conversation_by_filter(
        db=db,
        filter=filter,
        value=value,
        chatbot_id=chatbot_id,
        current_user_membership=current_user_membership,
    )



@router.get("/conversation/{filter}/{value}/{chatbot_id}", response_model=Optional[TotalDataTableConversationSchema])
def get_table_conversation_by_filter(
    filter: str,
    value: str,
    chatbot_id: str,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
) -> Optional[TotalDataTableConversationSchema]:
    return dashboard_service.get_table_conversation_by_filter(
        db=db,
        filter=filter,
        value=value,
        chatbot_id=chatbot_id,
        current_user_membership=current_user_membership,
    )

@router.get("/revenue/{filter}/{value}", response_model=Optional[TotalDataTableRevenueSchema])
def get_revenue_by_filter(
    filter: str,
    value: str,
    current_user_membership: UserSubscriptionPlan = Depends(
        oauth2.get_current_user_membership_info_by_token
    ),
    db: Session = Depends(deps.get_db),
) -> Optional[TotalDataTableRevenueSchema]:
    return dashboard_service.get_revenue_by_filter(
        db=db,
        filter=filter,
        value=value,
        current_user_membership=current_user_membership,
    )
