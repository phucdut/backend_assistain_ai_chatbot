from app.crud.base import CRUDBase
from app.models.revenue import Revenue
from app.schemas.revenue import *
from sqlalchemy.orm import Session
from sqlalchemy import asc

import uuid as UUID


class CRUDRevenue(CRUDBase[Revenue, RevenueCreate, RevenueUpdate]):
    # Add a method to get messages by conversation_id
    def get_revenue_by_plan_id(self, db: Session, subscription_plan_id: UUID):
        result = (db.query(Revenue)
                .filter(Revenue.subscription_plan_id == subscription_plan_id)
                .filter(Revenue.deleted_at == None)
                .order_by(asc(Revenue.created_at))
                .all())
        return result


crud_revenue = CRUDRevenue(Revenue)
